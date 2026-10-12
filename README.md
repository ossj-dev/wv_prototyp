# WV-Prototyp zur Dokumentenextraktion

Dieses Forschungsprojekt extrahiert Label-Anforderungen aus PDF-Dokumenten wie Verpackungsvorschriften und Beispiel-Labels. Es erkennt Text, Layout und Checkboxen, bereitet die Inhalte als Markdown auf und lässt sie von einem lokalen OpenAI-kompatiblen Large Language Model in ein festes JSON-Schema überführen.

Der Prototyp dient insbesondere zum Vergleich von Prompting-Strategien und Reasoning-Einstellungen. Die Ergebnisse und Zwischenschritte werden für die spätere Auswertung gespeichert.

## Ablauf

1. `main.py` sucht PDFs im Ordner des ausgewählten Artikels und gruppiert diese nach Artikelnummer, sodass auch mehrere PDFs pro Artikel kombiniert verarbeitet werden können.
2. Der Layout-Extractor verarbeitet Text, eingebettete Bilder, OCR und gezeichnete Checkboxen. Checkbox-Zustände (`[X]` oder `[ ]`) werden durch eine Pixelfüllgrad-Analyse der gezeichneten Kästchen ermittelt.
3. Die erkannten Elemente werden dateiübergreifend in Lesereihenfolge sortiert und zu Markdown kombiniert.
4. Ein lokales LLM extrahiert die Daten gemäß einem strikten JSON-Schema unter Verwendung des `Internal-CoT` (Chain-of-Thought) Reasoning-Modus.
5. JSON-Ergebnis, Metadaten, LLM-Ein-/Ausgabe und Layout werden unter `Ergebnisse/` abgelegt.

Die Standard-Prompts liegen in `prompts/`:

- `zero_shot.txt`
- `few-shot-2.txt`
- `few-shot-4.txt`

Alle drei werden standardmäßig mit dem Reasoning-Modus `Internal-CoT` ausgeführt. Mit `--prompt-file` kann ein einzelner eigener Systemprompt getestet werden.

## Voraussetzungen

- Python 3.10 oder neuer
- [LM Studio](https://lmstudio.ai/) mit geladenem Modell und aktiviertem OpenAI-kompatiblem Server (standardmäßig `http://127.0.0.1:1234/v1`)
- Tesseract OCR inklusive der benötigten Sprachdaten (falls das `pymupdf` Backend für OCR verwendet wird)
- Abhängigkeiten aus `requirements.txt`

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Die Eingabedaten werden artikelweise in Verzeichnissen unter `data/` erwartet, zum Beispiel:

```text
data/20323-000/*.pdf
```

## Verwendung

Artikelnummer direkt übergeben:

```bash
python main.py 20323-000
```

Ohne Argument fragt das Programm interaktiv nach der Artikelnummer. Für einen einzelnen Prompt:

```bash
python main.py 20323-000 --prompt-file prompts/zero_shot.txt
```

Für einen Lauf ohne LLM-Aufruf, etwa zum Testen der Pipeline, kann der Offline-Modus genutzt werden:

```bash
OFFLINE_MODE=true python main.py 20323-000
```

## Konfiguration

Die Einstellungen können in einer lokalen `.env`-Datei oder als Umgebungsvariablen gesetzt werden:

| Variable | Standard | Bedeutung |
| :--- | :--- | :--- |
| `INPUT_ROOT` | `./data` | Ordner mit den PDF-Eingaben |
| `RESULTS_ROOT` | `./Ergebnisse` | Zielordner für Läufe |
| `LAYOUT_BACKEND` | `docling-paddle` | `docling-paddle` (nutzt Docling für Layout & PaddleOCR für Scans) oder `pymupdf` (nutzt PyMuPDF & Tesseract) |
| `LM_STUDIO_BASE_URL` | `http://127.0.0.1:1234/v1` | LLM-Endpunkt |
| `LM_STUDIO_API_KEY` | `lm-studio` | API-Schlüssel des Endpunkts |
| `LM_STUDIO_MODEL` | `local-model` | Name des geladenen Modells |
| `LM_STUDIO_ENABLE_THINKING` | `false` | Thinking-Modus des Modells |
| `OFFLINE_MODE` | `false` | LLM-Aufruf durch Dummy-Ergebnis ersetzen |

Der Layout-Extractor wird pro Artikel nur einmal ausgeführt. Die extrahierten Layout-Rohdaten werden zusätzlich in `.cache/` als JSON zwischengespeichert, identifiziert durch einen MD5-Hash der Dateinamen.

## Ergebnisse

Für jede Prompt-Strategie entsteht ein eigener nummerierter Lauf unter `Ergebnisse/`. Ein Lauf enthält typischerweise:

- `*_extrahierte_daten.json`: strukturiertes Extraktionsergebnis
- `metadata.json`: Strategie, Modell, Laufzeit, Status, Tokenverbrauch und Fehlermeldungen
- `layout.md`: extrahierte Layout-Elemente als kombiniertes JSON
- `llm_input.md` und `llm_output.md`: Debug-Ausgaben mit Systemprompt, Reasoning-Modus und Benutzereingabe

Das JSON-Ergebnis beinhaltet aufgrund der strikten Schema-Definition folgende Felder:
- `_gedankengang`: Ausführliche Klartextanalyse (Belege, Checkbox-Entscheidungen, Ableitung, Unsicherheiten)
- `dokumentensprache`: Erkannte Sprache (oder null)
- `artikelnummer`: Extrahierte Artikelnummer (oder null)
- `labels`: Array bestehend aus `verpackungsebene` und `label_inhalt`

## Auswertung und Tests

Die Notebooks in `study/` werten die erzeugten Läufe aus. Die CSV-Dateien dort enthalten zusammengefasste Studienergebnisse zu Schema, Prompting und CoT.

Der automatisierte Test prüft, dass auch bei einer ungültigen LLM-JSON-Antwort `metadata.json` geschrieben wird:

```bash
pytest test_scripte/test_metadata_on_llm_failure.py
```

`test_scripte/test_vektorgrafiken.py` ist ein manuelles Hilfsskript zur visuellen Prüfung von Checkboxen in einem PDF.