"""Entry point for the PDF Merkmal Extrahierer."""

from __future__ import annotations

import json
import os
import argparse
import hashlib
import time
from pathlib import Path
from typing import Any
from collections import defaultdict # Neu hinzugefügt für die Gruppierung
from datetime import datetime, timezone

from pdf_merkmal_extrahierer.discovery import find_article_pdfs
from pdf_merkmal_extrahierer.extractor import (
    DoclingPaddleExtractor,
    LayoutExtractionResult,
    LayoutExtractor,
)
from pdf_merkmal_extrahierer.llm_client import LlmClient
from pdf_merkmal_extrahierer.preprocessing import merge_layout_to_markdown


STRATEGIES = {
    "few-shot-2": Path("./prompts/few-shot-2.txt"),
    "few-shot-4": Path("./prompts/few-shot-4.txt"),
    "zero-shot": Path("./prompts/zero_shot.txt"),
}


def load_system_prompt(prompt_path: Path) -> str:
    """Load a system prompt from a UTF-8 text file."""
    if not prompt_path.is_file():
        raise FileNotFoundError(f"Systemprompt nicht gefunden: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def write_debug_markdown(path: Path, title: str, content: str) -> None:
    """Write one extraction step to a readable Markdown debug file."""
    path.write_text(f"# {title}\n\n{content}\n", encoding="utf-8")


def create_run_directory(results_root: Path, article_name: str) -> Path:
    """Create the next numbered result directory for an article."""
    results_root.mkdir(parents=True, exist_ok=True)
    run_index = 1
    while True:
        run_directory = results_root / f"{article_name}_{run_index:02d}"
        if not run_directory.exists():
            run_directory.mkdir()
            return run_directory
        run_index += 1


def process_article(
    article_name: str,
    pdf_paths: list[Path],
    output_path: Path,
    system_prompt: str,
    prompt: str,
    layout_result: LayoutExtractionResult,
    llm_client: LlmClient | None = None,
    offline: bool = False,
) -> dict[str, Any]:
    """Run one prompting strategy for prepared article content."""
    write_debug_markdown(
        output_path.parent / "llm_input.md",
        "LLM-Eingabe",
        f"## Systemprompt\n\n{system_prompt}\n\n## Benutzereingabe\n\n{prompt}",
    )

    if offline:
        result: dict[str, Any] = {
            "merkmale": [],
            "_meta": {
                "source_files": [p.name for p in pdf_paths],
                "status": "offline-dummy",
                "layout_backend": layout_result.backend,
            },
        }
        (output_path.parent / "llm_output.md").write_text(
            "# LLM-Ausgabe\n\nKein LLM-Aufruf im Offline-Modus.\n",
            encoding="utf-8",
        )
    else:
        client = llm_client or LlmClient()
        try:
            result = client.extract_json(
                prompt,
                system_prompt,
                debug_output_path=output_path.parent / "llm_output.md",
            )
        except Exception as exc:  # noqa: BLE001 - intentionally keep run metadata
            result = {
                "merkmale": [],
                "_meta": {
                    "source_files": [p.name for p in pdf_paths],
                    "status": "llm_json_error",
                    "error": str(exc),
                    "layout_backend": layout_result.backend,
                },
            }
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            return result

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> None:
    """Run the extraction pipeline for one selected article."""
    from dotenv import load_dotenv

    parser = argparse.ArgumentParser(description="Extrahiert Merkmale eines Artikels.")
    parser.add_argument(
        "article_number",
        nargs="?",
        help="Artikelnummer, z. B. 123456; ohne Angabe wird interaktiv gefragt",
    )
    args = parser.parse_args()

    load_dotenv()
    input_root = Path(os.getenv("INPUT_ROOT", "./data"))
    offline = os.getenv("OFFLINE_MODE", "false").lower() in {"1", "true", "yes"}
    if args.article_number is None:
        args.article_number = input("Artikelnummer: ").strip()

    # PDFs suchen
    pdfs = find_article_pdfs(input_root, args.article_number)

    if not pdfs:
        print(f"Keine PDFs im Artikel-Ordner {args.article_number} gefunden.")
        return

    # NEU: PDFs nach Artikelnummer gruppieren
    pdfs_by_article = defaultdict(list)
    for article_name, pdf_path in pdfs:
        pdfs_by_article[article_name].append(pdf_path)

    layout_backend = os.getenv("LAYOUT_BACKEND", "docling-paddle").lower()
    if layout_backend == "pymupdf":
        extractor: LayoutExtractor | DoclingPaddleExtractor = LayoutExtractor(language="deu")
    elif layout_backend == "docling-paddle":
        extractor = DoclingPaddleExtractor(language="german")
    else:
        raise ValueError(
            "Unbekanntes LAYOUT_BACKEND. Erlaubt sind: docling-paddle, pymupdf."
        )

    results_root = Path(os.getenv("RESULTS_ROOT", "./Ergebnisse"))

    # Layout und Markdown werden pro Artikel nur einmal vorbereitet.
    for article_name, pdf_paths in pdfs_by_article.items():
        cache_key = hashlib.md5(
            "\n".join(path.name for path in pdf_paths).encode("utf-8")
        ).hexdigest()
        cache_path = Path(".cache") / f"layout_{cache_key}.json"
        if cache_path.is_file():
            layout_result = LayoutExtractionResult(
                source=pdf_paths,
                elements=json.loads(cache_path.read_text(encoding="utf-8")),
                backend=extractor.backend,
            )
        else:
            layout_result = extractor.extract(pdf_paths)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(
                json.dumps(layout_result.elements, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        prompt = merge_layout_to_markdown(layout_result.elements)

        for strategy_name, prompt_path in STRATEGIES.items():
            system_prompt = load_system_prompt(prompt_path)
            run_directory = create_run_directory(
                results_root, f"{article_name}_{strategy_name}"
            )
            output_path = (
                run_directory
                / f"{article_name}_{strategy_name}_extrahierte_daten.json"
            )
            started_at = datetime.now(timezone.utc)
            started_counter = time.perf_counter()
            client = LlmClient() if not offline else None

            write_debug_markdown(
                run_directory / "layout.md",
                "Layout-Extraktion (Kombiniert)",
                json.dumps(layout_result.elements, ensure_ascii=False, indent=2),
            )
            try:
                result = process_article(
                    article_name=article_name,
                    pdf_paths=pdf_paths,
                    output_path=output_path,
                    system_prompt=system_prompt,
                    prompt=prompt,
                    layout_result=layout_result,
                    llm_client=client,
                    offline=offline,
                )
                status = result.get("_meta", {}).get("status", "ok")
                error_text = result.get("_meta", {}).get("error")
            except Exception as exc:  # noqa: BLE001 - still write metadata for analysis
                result = {
                    "merkmale": [],
                    "_meta": {
                        "source_files": [str(path) for path in pdf_paths],
                        "status": "processing_error",
                        "error": str(exc),
                    },
                }
                status = "processing_error"
                error_text = str(exc)

            finished_at = datetime.now(timezone.utc)
            elapsed_seconds = time.perf_counter() - started_counter
            metadata = {
                "article_number": article_name,
                "strategy": strategy_name,
                "source_files": [str(path) for path in pdf_paths],
                "prompt_file": str(prompt_path),
                "json_schema": True,
                "thinking_enabled": os.getenv(
                    "LM_STUDIO_ENABLE_THINKING", "false"
                ).lower() in {"1", "true", "yes"},
                "model": os.getenv("LM_STUDIO_MODEL", "local-model"),
                "offline": offline,
                "started_at_utc": started_at.isoformat(),
                "finished_at_utc": finished_at.isoformat(),
                "duration_seconds": round(elapsed_seconds, 3),
                "token_usage": client.last_usage if client is not None else None,
                "result_file": output_path.name,
                "status": status,
                "error": error_text,
            }
            (run_directory / "metadata.json").write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(
                f"Fertig! Artikel: {article_name} | Strategie: {strategy_name} | "
                f"{len(pdf_paths)} Datei(en) verarbeitet | Ergebnisordner: "
                f"{run_directory} | JSON: {output_path} | Status: {status}"
            )


if __name__ == "__main__":
    main()