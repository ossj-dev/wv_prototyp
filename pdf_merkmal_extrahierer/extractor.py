"""Text and layout extraction from PDF documents."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pymupdf
import pytesseract
from PIL import Image


OcrBackend = Literal["tesseract", "doctr"]
LayoutBackend = Literal["pymupdf", "table-transformer", "layoutlmv3"]


@dataclass(frozen=True)
class TextExtractionResult:
    """Text extracted from one or multiple PDF documents."""
    source: list[Path]  # Geändert von Path zu list[Path]
    text: str
    backend: OcrBackend


@dataclass(frozen=True)
class LayoutExtractionResult:
    """Layout elements extracted from one or multiple PDF documents."""
    source: list[Path]  # Geändert von Path zu list[Path]
    elements: list[dict[str, object]]
    backend: LayoutBackend


def _validate_pdf_path(pdf_path: Path) -> None:
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF nicht gefunden: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Datei ist kein PDF: {pdf_path}")


class OcrExtractor:
    """Extract text from PDF pages with Tesseract OCR."""

    def __init__(
        self,
        backend: OcrBackend = "tesseract",
        language: str = "eng",
        dpi: int = 300,
    ) -> None:
        self.backend = backend
        self.language = language
        self.dpi = dpi

    def extract(self, pdf_paths: list[Path]) -> TextExtractionResult:
        """Render every PDF page of multiple files and extract its text with Tesseract."""
        if self.backend != "tesseract":
            raise NotImplementedError(
                f"OCR-Backend noch nicht implementiert: {self.backend}"
            )
        if self.dpi <= 0:
            raise ValueError(f"Die OCR-Auflösung muss positiv sein: {self.dpi}")

        page_texts: list[str] = []
        
        # --- NEU: Schleife über alle PDFs ---
        for pdf_path in pdf_paths:
            _validate_pdf_path(pdf_path)
            
            # Trenner einfügen, damit das LLM die Dokumente unterscheiden kann
            page_texts.append(f"=== Datei: {pdf_path.name} ===")
            
            with pymupdf.open(pdf_path) as document:
                for page_number, page in enumerate(document, start=1):
                    pixmap = page.get_pixmap(dpi=self.dpi, alpha=False)
                    image = Image.frombytes(
                        "RGB", (pixmap.width, pixmap.height), pixmap.samples
                    )
                    try:
                        text = pytesseract.image_to_string(
                            image,
                            lang=self.language,
                            config="--psm 3",
                        ).strip()
                    finally:
                        image.close()
                    page_texts.append(f"--- Seite {page_number} ---\n{text}")

        return TextExtractionResult(
            source=pdf_paths,
            text="\n\n".join(page_texts),
            backend=self.backend,
        )


class LayoutExtractor:
    """Extract positioned text blocks and checkboxes from PDF pages."""

    def __init__(
        self,
        backend: LayoutBackend = "pymupdf",
        language: str = "eng",
        dpi: int = 300,
    ) -> None:
        self.backend = backend
        self.language = language
        self.dpi = dpi

    def extract(self, pdf_paths: list[Path]) -> LayoutExtractionResult:
        """Extract text blocks, checkboxes, and their page coordinates from multiple PDFs."""
        if self.backend != "pymupdf":
            raise NotImplementedError(
                f"Layout-Backend noch nicht implementiert: {self.backend}"
            )
        if self.dpi <= 0:
            raise ValueError(f"Die Layout-Auflösung muss positiv sein: {self.dpi}")

        elements: list[dict[str, object]] = []
        
        for pdf_path in pdf_paths:
            _validate_pdf_path(pdf_path)
            
            with pymupdf.open(pdf_path) as document:
                for page_number, page in enumerate(document, start=1):
                    
                    # Temporärer Speicher für diese eine Seite
                    page_elements: list[dict[str, object]] = []

                    # 1. Checkboxen extrahieren
                    # Wir übergeben 0 als previous_count, da der Index später vergeben wird
                    checkbox_elements = self._extract_vector_checkboxes(
                        page, page_number, pdf_path.name, 0
                    )
                    page_elements.extend(checkbox_elements)

                    # 2. Text und Bilder extrahieren
                    blocks = page.get_text("blocks")

                    # Text zeilenweise extrahieren, damit Checkboxen anhand ihrer
                    # Position in die jeweilige Zeile einsortiert werden können.
                    words = page.get_text("words")
                    text_lines: dict[tuple[int, int], list[tuple]] = {}
                    for word in words:
                        block_number = int(word[5])
                        line_number = int(word[6])
                        text_lines.setdefault((block_number, line_number), []).append(word)

                    for line_words in text_lines.values():
                        line_words.sort(key=lambda word: word[0])
                        text = " ".join(word[4] for word in line_words).strip()
                        if text:
                            page_elements.append({
                                "file": pdf_path.name,
                                "page": page_number,
                                "type": "text",
                                "bbox": [
                                    round(float(min(word[0] for word in line_words)), 2),
                                    round(float(min(word[1] for word in line_words)), 2),
                                    round(float(max(word[2] for word in line_words)), 2),
                                    round(float(max(word[3] for word in line_words)), 2),
                                ],
                                "text": text,
                            })

                    for block in blocks:
                        # block[6] enthält den Block-Typ in PyMuPDF
                        if len(block) >= 7:
                            block_type = block[6]
                            
                            # --- Typ 1: Eingebettetes Bild ---
                            if block_type == 1:
                                # Wir schneiden das Bild exakt an seinen Koordinaten aus
                                clip_rect = pymupdf.Rect(block[:4])
                                pixmap = page.get_pixmap(dpi=self.dpi, alpha=False, clip=clip_rect)
                                
                                import pytesseract
                                from PIL import Image
                                image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
                                
                                try:
                                    # OCR nur auf diesen Bild-Ausschnitt anwenden
                                    ocr_text = pytesseract.image_to_string(
                                        image, lang=self.language, config="--psm 3"
                                    ).strip()
                                finally:
                                    image.close()
                                    
                                if ocr_text:
                                    page_elements.append({
                                        "file": pdf_path.name,
                                        "page": page_number,
                                        "type": "text", # Wir behandeln den OCR-Text danach wie normalen Text
                                        "bbox": [round(float(value), 2) for value in block[:4]],
                                        "text": ocr_text,
                                    })

                    # 3. Fallback für Seiten, die GANZ ohne Blöcke sind (z.B. fehlerhafte PDFs)
                    if not words:
                        ocr_elements = self._extract_ocr_elements(page, page_number, 0)
                        for el in ocr_elements:
                            el["file"] = pdf_path.name
                        page_elements.extend(ocr_elements)

                    
                    # A) In Lesereihenfolge sortieren. Elemente derselben Zeile
                    # werden über ihre vertikale Überlappung zusammengefasst.
                    page_elements = self._sort_in_reading_order(page_elements)
                    
                    # B) Index sauber durchzählen und Datenmüll entfernen
                    for el in page_elements:
                        el["index"] = len(elements) + 1
                        
                        # Bbox (und ggf. OCR-Confidence) bei Texten löschen!
                        if el["type"] in ["text", "ocr-word"]:
                            del el["bbox"]
                            if "confidence" in el:
                                del el["confidence"]
                                
                        elements.append(el)

        return LayoutExtractionResult(
            source=pdf_paths,
            elements=elements,
            backend=self.backend,
        )

    @staticmethod
    def _sort_in_reading_order(
        elements: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        """Sort elements by rows and then by their horizontal position."""
        rows: list[dict[str, object]] = []
        for element in sorted(elements, key=lambda item: item["bbox"][1]):
            bbox = element["bbox"]
            row = next(
                (
                    candidate
                    for candidate in rows
                    if bbox[1] < candidate["bottom"]
                    and bbox[3] > candidate["top"]
                ),
                None,
            )
            if row is None:
                rows.append({"top": bbox[1], "bottom": bbox[3], "elements": [element]})
            else:
                row["top"] = min(row["top"], bbox[1])
                row["bottom"] = max(row["bottom"], bbox[3])
                row["elements"].append(element)

        rows.sort(key=lambda row: row["top"])
        return [
            element
            for row in rows
            for element in sorted(row["elements"], key=lambda item: item["bbox"][0])
        ]

    def _extract_vector_checkboxes(
        self, page: pymupdf.Page, page_number: int, file_name: str, previous_count: int
    ) -> list[dict[str, object]]:
        """Find drawn squares and determine if they are checked via pixel analysis."""
        elements: list[dict[str, object]] = []
        drawings = page.get_drawings()
        
        roh_kaestchen = []
        for draw in drawings:
            bbox = draw["rect"]
            width = bbox.width
            height = bbox.height
            if 8 < width < 25 and 8 < height < 25 and abs(width - height) < 5:
                roh_kaestchen.append(bbox)
        
        gefilterte_kaestchen = []
        for bbox in roh_kaestchen:
            ist_duplikat = False
            for schon_gepueft in gefilterte_kaestchen:
                if abs(bbox.x0 - schon_gepueft.x0) < 2 and abs(bbox.y0 - schon_gepueft.y0) < 2:
                    ist_duplikat = True
                    break
            if not ist_duplikat:
                gefilterte_kaestchen.append(bbox)

        for i, kaestchen in enumerate(gefilterte_kaestchen):
            inner_rect = pymupdf.Rect(
                kaestchen.x0 + 2, kaestchen.y0 + 2, kaestchen.x1 - 2, kaestchen.y1 - 2
            )
            pix = page.get_pixmap(clip=inner_rect, colorspace=pymupdf.csGRAY)
            
            dark_pixels = sum(1 for p in pix.samples if p < 220)
            total_pixels = len(pix.samples)
            fill_ratio = dark_pixels / total_pixels if total_pixels > 0 else 0
            
            is_checked = fill_ratio > 0.05
            
            elements.append(
                {
                    "file": file_name,
                    "page": page_number,
                    "index": previous_count + i + 1,
                    "type": "checkbox",
                    "bbox": [
                        round(kaestchen.x0, 2),
                        round(kaestchen.y0, 2),
                        round(kaestchen.x1, 2),
                        round(kaestchen.y1, 2),
                    ],
                    "state": "checked" if is_checked else "unchecked",
                    "text": "[X]" if is_checked else "[ ]",
                }
            )
            
        return elements

    def _extract_ocr_elements(
        self, page: pymupdf.Page, page_number: int, previous_count: int
    ) -> list[dict[str, object]]:
        """Extract positioned words when a page has no embedded text layer."""
        pixmap = page.get_pixmap(dpi=self.dpi, alpha=False)
        from PIL import Image
        import pytesseract
        
        image = Image.frombytes(
            "RGB", (pixmap.width, pixmap.height), pixmap.samples
        )
        try:
            data = pytesseract.image_to_data(
                image,
                lang=self.language,
                config="--psm 3",
                output_type=pytesseract.Output.DICT,
            )
        finally:
            image.close()

        scale = 72 / self.dpi
        elements: list[dict[str, object]] = []
        for index, text in enumerate(data["text"]):
            text = text.strip()
            if not text:
                continue
            left = float(data["left"][index]) * scale
            top = float(data["top"][index]) * scale
            width = float(data["width"][index]) * scale
            height = float(data["height"][index]) * scale
            elements.append(
                {
                    "page": page_number,
                    "index": previous_count + len(elements) + 1,
                    "type": "ocr-word",
                    "bbox": [
                        round(left, 2),
                        round(top, 2),
                        round(left + width, 2),
                        round(top + height, 2),
                    ],
                    "text": text,
                    "confidence": float(data["conf"][index]),
                }
            )
        return elements