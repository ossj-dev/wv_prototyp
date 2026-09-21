"""Discovery of article folders and source PDF documents."""

from __future__ import annotations

from pathlib import Path


def find_article_pdfs(
    input_root: Path, article_number: str | None = None
) -> list[tuple[str, Path]]:
    """Find PDFs below one article directory or all article directories."""
    if not input_root.is_dir():
        raise FileNotFoundError(f"Hauptordner nicht gefunden: {input_root}")

    article_directories = (
        [input_root / article_number]
        if article_number is not None
        else [path for path in input_root.iterdir() if path.is_dir()]
    )
    if article_number is not None and not article_directories[0].is_dir():
        raise FileNotFoundError(
            f"Artikel-Ordner nicht gefunden: {article_directories[0]}"
        )

    article_pdfs: list[tuple[str, Path]] = []
    for article_directory in sorted(article_directories):
        for pdf_path in sorted(article_directory.rglob("*")):
            if pdf_path.is_file() and pdf_path.suffix.lower() == ".pdf":
                article_pdfs.append((article_directory.name, pdf_path))

    return article_pdfs