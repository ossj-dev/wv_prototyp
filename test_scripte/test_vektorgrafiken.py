import pymupdf
from pathlib import Path

def test_kaestchen_visuell(pdf_path: Path):
    print(f"Prüfe Kästchen in: {pdf_path}")
    with pymupdf.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            drawings = page.get_drawings()
            
            # 1. Alle potenziellen Kästchen finden
            roh_kaestchen = []
            for draw in drawings:
                bbox = draw["rect"]
                width = bbox.width
                height = bbox.height
                
                if 8 < width < 25 and 8 < height < 25 and abs(width - height) < 5:
                    roh_kaestchen.append(bbox)
            
            # 2. Duplikate exakt filtern
            gefilterte_kaestchen = []
            for bbox in roh_kaestchen:
                ist_duplikat = False
                for schon_gepueft in gefilterte_kaestchen:
                    if abs(bbox.x0 - schon_gepueft.x0) < 2 and abs(bbox.y0 - schon_gepueft.y0) < 2:
                        ist_duplikat = True
                        break
                if not ist_duplikat:
                    gefilterte_kaestchen.append(bbox)

            if not gefilterte_kaestchen:
                continue
                
            print(f"\nSeite {page_num} | {len(gefilterte_kaestchen)} einzigartige Kästchen gefunden.")
            
            # 3. Visuelle Prüfung (Foto vom Inneren des Kästchens)
            for i, kaestchen in enumerate(gefilterte_kaestchen, start=1):
                # Wir schrumpfen die Box auf allen Seiten um 2 Punkte.
                # So fällt der schwarze Rand weg und wir betrachten nur das Innere.
                inner_rect = pymupdf.Rect(
                    kaestchen.x0 + 2, 
                    kaestchen.y0 + 2, 
                    kaestchen.x1 - 2, 
                    kaestchen.y1 - 2
                )
                
                # Wir machen ein Mini-Bild vom Inneren in Graustufen
                pix = page.get_pixmap(clip=inner_rect, colorspace=pymupdf.csGRAY)
                
                # Zähle alle dunklen Pixel (0 = Schwarz, 255 = Weiß). Alles unter 220 ist Tinte.
                dark_pixels = sum(1 for p in pix.samples if p < 220)
                total_pixels = len(pix.samples)
                
                # Wenn mehr als 5 % des Inneren mit Tinte gefüllt sind, ist es angekreuzt
                fill_ratio = dark_pixels / total_pixels if total_pixels > 0 else 0
                
                status = "Angekreuzt" if fill_ratio > 0.05 else "Leer"
                print(f"  -> Kästchen {i} (Füllung: {fill_ratio:.1%}): {status}")

# Pfad anpassen!
test_kaestchen_visuell(Path("data/40402-405/D120420_DE_000.pdf"))