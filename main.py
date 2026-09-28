"""Entry point for the PDF Merkmal Extrahierer."""

from __future__ import annotations

import json
import os
import argparse
import time
from pathlib import Path
from typing import Any
from collections import defaultdict # Neu hinzugefügt für die Gruppierung
from datetime import datetime, timezone

from pdf_merkmal_extrahierer.discovery import find_article_pdfs
from pdf_merkmal_extrahierer.extractor import LayoutExtractor
from pdf_merkmal_extrahierer.llm_client import LlmClient
from pdf_merkmal_extrahierer.preprocessing import merge_layout_to_markdown
from pdf_merkmal_extrahierer.refinement import refine_extraction_result


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


def choose_experiment_settings(
    prompt_directory: Path,
) -> tuple[str, Path, bool]:
    """Select the article and prompt interactively."""
    article_number = input("Artikelnummer: ").strip()
    prompt_choices = {
        "1": ("few-shot-2", prompt_directory / "few-shot-2.txt", False),
        "2": ("few-shot-4", prompt_directory / "few-shot-4.txt", False),
        "3": ("refinement", prompt_directory / "zero_shot.txt", True),
    }
    print(
        "Prompt auswählen: [1] few-shot-2  [2] few-shot-4  [3] refinement"
    )
    prompt_choice = input("Auswahl [1]: ").strip() or "1"
    if prompt_choice not in prompt_choices:
        raise ValueError("Ungültige Prompt-Auswahl. Bitte 1, 2 oder 3 verwenden.")

    _, prompt_path, refinement_enabled = prompt_choices[prompt_choice]
    return article_number, prompt_path, refinement_enabled


# GEÄNDERT: Akzeptiert jetzt eine Liste von Pfaden (pdf_paths)
def process_article(
    article_name: str,
    pdf_paths: list[Path],
    output_path: Path,
    system_prompt: str,
    llm_client: LlmClient | None = None,
    offline: bool = False,
    refinement_enabled: bool = False,
    refinement_prompt_path: Path | None = None,
    refinement_max_attempts: int = 1,
) -> dict[str, Any]:
    """Extract multiple PDFs for one article and write a combined JSON."""
    debug_prefix = output_path.with_name(f"{output_path.stem}.DEBUG")

    # extractor.py haben wir so umgebaut, dass sie Listen akzeptieren
    layout_result = LayoutExtractor().extract(pdf_paths)
    write_debug_markdown(
        debug_prefix.with_name(f"{debug_prefix.name}_02_layout.md"),
        "Layout-Extraktion (Kombiniert)",
        json.dumps(layout_result.elements, ensure_ascii=False, indent=2),
    )

    prompt = merge_layout_to_markdown(layout_result.elements)
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
            if refinement_enabled:
                if refinement_prompt_path is None:
                    raise ValueError("Für den Refinement-Modus fehlt der Refinement-Prompt.")
                refinement_prompt = load_system_prompt(refinement_prompt_path)
                result, feedback = refine_extraction_result(
                    initial_result=result,
                    document_prompt=prompt,
                    refinement_prompt=refinement_prompt,
                    llm_extract=client.extract_json,
                    debug_directory=output_path.parent,
                    max_attempts=refinement_max_attempts,
                )
                (output_path.parent / "refinement_feedback.json").write_text(
                    json.dumps(feedback, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
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
    parser.add_argument(
        "-p",
        "--prompt-file",
        type=Path,
        help="Optionale Systemprompt-Datei für Prompt-Vergleiche",
    )
    args = parser.parse_args()

    load_dotenv()
    input_root = Path(os.getenv("INPUT_ROOT", "./data"))
    offline = os.getenv("OFFLINE_MODE", "false").lower() in {"1", "true", "yes"}
    if args.article_number is None and args.prompt_file is None:
        args.article_number, prompt_path, refinement_enabled = choose_experiment_settings(
            Path("./prompts")
        )
    else:
        prompt_path = args.prompt_file or Path(
            os.getenv("SYSTEM_PROMPT_FILE", "./prompts/system_default.txt")
        )
        refinement_enabled = False
    system_prompt = load_system_prompt(prompt_path)
    
    # PDFs suchen
    pdfs = find_article_pdfs(input_root, args.article_number)

    if not pdfs:
        print(f"Keine PDFs im Artikel-Ordner {args.article_number} gefunden.")
        return

    # NEU: PDFs nach Artikelnummer gruppieren
    pdfs_by_article = defaultdict(list)
    for article_name, pdf_path in pdfs:
        pdfs_by_article[article_name].append(pdf_path)

    # Verarbeitung auf Artikelebene (nicht mehr auf Dateiebene)
    for article_name, pdf_paths in pdfs_by_article.items():
        run_directory = create_run_directory(
            Path(os.getenv("RESULTS_ROOT", "./Ergebnisse")), article_name
        )
        output_path = run_directory / f"{article_name}_extrahierte_daten.json"
        started_at = datetime.now(timezone.utc)
        started_counter = time.perf_counter()
        client = LlmClient() if not offline else None

        try:
            result = process_article(
                article_name=article_name,
                pdf_paths=pdf_paths,
                output_path=output_path,
                system_prompt=system_prompt,
                llm_client=client,
                offline=offline,
                refinement_enabled=refinement_enabled,
                refinement_prompt_path=Path(
                    os.getenv("REFINEMENT_PROMPT_FILE", "./prompts/refinement_prompt.txt")
                ),
                refinement_max_attempts=int(os.getenv("REFINEMENT_MAX_ATTEMPTS", "1")),
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
            f"Fertig! Artikel: {article_name} | {len(pdf_paths)} Datei(en) verarbeitet "
            f"| Ergebnisordner: {run_directory} | JSON: {output_path} | Status: {status}"
        )


if __name__ == "__main__":
    main()