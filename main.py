"""Entry point for the PDF Merkmal Extrahierer."""

from __future__ import annotations

import json
import os
import argparse
from pathlib import Path
from typing import Any
from collections import defaultdict # Neu hinzugefügt für die Gruppierung

from pdf_merkmal_extrahierer.discovery import find_article_pdfs
from pdf_merkmal_extrahierer.extractor import LayoutExtractor
from pdf_merkmal_extrahierer.llm_client import LlmClient
from pdf_merkmal_extrahierer.preprocessing import merge_layout_to_markdown


def load_system_prompt(prompt_path: Path) -> str:
    """Load a system prompt from a UTF-8 text file."""
    if not prompt_path.is_file():
        raise FileNotFoundError(f"Systemprompt nicht gefunden: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def write_debug_markdown(path: Path, title: str, content: str) -> None:
    """Write one extraction step to a readable Markdown debug file."""
    path.write_text(f"# {title}\n\n{content}\n", encoding="utf-8")


# GEÄNDERT: Akzeptiert jetzt eine Liste von Pfaden (pdf_paths)
def process_article(
    article_name: str,
    pdf_paths: list[Path],
    output_path: Path,
    system_prompt: str,
    llm_client: LlmClient | None = None,
    offline: bool = False,
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

    if offline:
        result: dict[str, Any] = {
            "merkmale": [],
            "_meta": {
                "source_files": [p.name for p in pdf_paths], # GEÄNDERT auf Plural
                "status": "offline-dummy",
                "layout_backend": layout_result.backend,
            },
        }
    else:
        client = llm_client or LlmClient()
        prompt = merge_layout_to_markdown(layout_result.elements)
        write_debug_markdown(
            debug_prefix.with_name(f"{debug_prefix.name}_03_llm_input.md"),
            "LLM-Eingabe",
            f"## Systemprompt\n\n{system_prompt}\n\n## Benutzereingabe\n\n{prompt}",
        )
        result = client.extract_json(
            prompt,
            system_prompt,
            debug_output_path=debug_prefix.with_name(
                f"{debug_prefix.name}_04_llm_output.md"
            ),
        )

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
    parser.add_argument("article_number", help="Artikelnummer, z. B. 123456")
    parser.add_argument(
        "--prompt-file",
        type=Path,
        help="Optionale Systemprompt-Datei für Prompt-Vergleiche",
    )
    args = parser.parse_args()

    load_dotenv()
    input_root = Path(os.getenv("INPUT_ROOT", "./data"))
    offline = os.getenv("OFFLINE_MODE", "false").lower() in {"1", "true", "yes"}
    prompt_path = args.prompt_file or Path(
        os.getenv("SYSTEM_PROMPT_FILE", "./prompts/system_default.txt")
    )
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
        # Ausgabe-JSON direkt in den Artikel-Ordner legen
        # Wir nehmen den Parent-Ordner des ersten PDFs
        article_dir = pdf_paths[0].parent
        output_path = article_dir / f"{article_name}_extrahierte_daten.json"
        
        process_article(
            article_name=article_name,
            pdf_paths=pdf_paths,
            output_path=output_path,
            system_prompt=system_prompt,
            offline=offline
        )
        print(f"Fertig! Artikel: {article_name} | {len(pdf_paths)} Datei(en) verarbeitet | JSON: {output_path}")


if __name__ == "__main__":
    main()