# WV-Prototyp: Label-Anforderungen aus PDFs extrahieren

Dieser Forschungsprototyp überführt Prüfhinweise für Logistik-Labels aus heterogenen Produktdokumenten in strukturiertes JSON. Aus Verpackungsvorschriften und Beispiel-Labels ermittelt er, **welche Verpackungsebene ein Label benötigt und welche Datenfelder darauf stehen müssen**, etwa Artikelnummer, Charge oder Barcode. Dafür verbindet er Layout-Erkennung und OCR mit einem lokal betriebenen Large Language Model (LLM).

Das Repository enthält die Extraktionspipeline, die Versuchsergebnisse und die Auswertung einer dreiteiligen Studie zu Formatstabilität und inhaltlicher Zuverlässigkeit.

## Wie die Pipeline arbeitet

```text
PDFs eines Artikels → Layout, OCR und Checkboxen → Markdown → lokales LLM → JSON + Laufprotokolle
```

1. **Dokumente sammeln:** [main.py](main.py) findet die PDFs unter `data/<Artikelnummer>/` und verarbeitet alle Dokumente eines Artikels gemeinsam.
2. **Layout und Inhalte erkennen:** Standardmäßig extrahiert Docling Text und Tabellen; PaddleOCR liest Seiten ohne brauchbare Textebene. Alternativ steht PyMuPDF mit Tesseract zur Verfügung. Gezeichnete Checkboxen werden anhand ihrer Form erkannt und über den dunklen Pixelanteil im Inneren als markiert oder leer klassifiziert.
3. **LLM-Eingabe aufbereiten:** Die Elemente werden in Lesereihenfolge zu Markdown zusammengeführt. Dokument- und Seitenmarkierungen erhalten den Quellenbezug, `[X]` und `[ ]` die Checkbox-Zustände. Das Layout wird pro Artikel einmal vorbereitet und in `.cache/` zwischengespeichert.
4. **Anforderungen extrahieren:** Ein lokales Modell erhält den Dokumenttext und einen Prompt aus [prompts/](prompts/) über die OpenAI-kompatible Schnittstelle von LM Studio. Die Prompts unterscheiden Verpackungsvorschriften von Beispiel-Labels und steuern die Zuordnung von Label-Pflicht und Datenfeldern. Ein vorgegebenes JSON-Schema beschränkt die Ausgabestruktur.
5. **Ergebnisse speichern:** Pro Prompt-Variante entsteht ein nummerierter Lauf in [Ergebnisse/](Ergebnisse/), einschließlich JSON-Ausgabe, Layout, LLM-Ein-/Ausgabe und Metadaten zu Modell, Laufzeit, Tokenverbrauch und Status.

Das Zielschema enthält `dokumentensprache`, `artikelnummer` und `labels` mit jeweils `verpackungsebene` und `label_inhalt`. Der aktuelle **Internal-CoT**-Ansatz fordert zusätzlich eine Analyse im ersten JSON-Feld `_gedankengang` an; Analyse und Extraktion erfolgen in einem LLM-Aufruf. Der separate modellinterne Thinking-Modus wird über `LM_STUDIO_ENABLE_THINKING` gesteuert.

## Dreiteiliges Studiendesign

Die Studie untersucht die Dokumente von **zehn Artikeln** in drei aufeinander aufbauenden Schritten. Die Jupyter-Notebooks und zugehörigen Bewertungsdaten als CSV liegen in [study/](study/).

| Teil | Versuchsaufbau und Ziel | Auswertung |
| --- | --- | --- |
| **1 · Modelle und Formatstabilität** | Llama 3.1 8B, NuExtract3 4B, Qwen 2.5 7B und Qwen 2.5 Coder 14B; jeweils Minimal-/Regelprompt und JSON-Schema an/aus. Auswahl geeigneter Modelle anhand von Formatstabilität, Extraktionsqualität und Laufzeit (**160 Läufe**). | [Notebook 1](study/auswertung_study_01.ipynb) |
| **2 · Prompting-Strategien** | NuExtract3 und Qwen 2.5 7B mit Zero-Shot sowie Few-Shot mit zwei bzw. vier Beispielen. Vergleich der inhaltlichen Genauigkeit (**60 Läufe**). | [Notebook 2](study/auswertung_study_02.ipynb) |
| **3 · Chain-of-Thought** | NuExtract3 mit denselben drei Prompt-Strategien und zusätzlichem Internal-CoT. Vergleich mit den Ergebnissen ohne CoT aus Teil 2 (**30 Läufe**). | [Notebook 3](study/auswertung_study_03.ipynb) |

Bewertet werden unter anderem JSON-Parsbarkeit und Schemakonformität, Precision/Recall, F1-Score sowie die korrekte Erkennung von Verpackungsebenen, Artikelnummern und Labelinhalten. Die Notebooks lesen die Bewertungs-CSV-Dateien; sie führen keine neuen LLM-Versuche aus.

**Aktueller Code-Stand:** `main.py` führt Zero-Shot, Few-Shot-2 und Few-Shot-4 mit JSON-Schema und Internal-CoT aus. Die früheren Versuchsvarianten der Studie sind in den Ergebnissen dokumentiert, aber nicht vollständig über die aktuelle Kommandozeile auswählbar.

## Wissenschaftliches Paper

Die Motivation, Methodik, Ergebnisse und Grenzen der Studie beschreibt das Paper von Jonas Osswald:

**[Evaluierung unterschiedlicher LLM-Steuerungsansätze zur strukturierten Extraktion von Prüfplänen aus heterogenen Produktdokumenten](short-paper/osswald_endfassung.pdf)** — abgelegt in [short-paper/](short-paper/).

## Lokal ausführen

Vorausgesetzt werden Python 3.10+, LM Studio mit geladenem Modell und aktiviertem OpenAI-kompatiblem Server sowie für das optionale PyMuPDF-Backend Tesseract inklusive deutscher Sprachdaten.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

PDFs unter `data/<Artikelnummer>/` ablegen; die Eingabedokumente werden nicht mit Git versioniert. Die Konfiguration erfolgt über `.env` oder Umgebungsvariablen, beispielsweise:

```dotenv
LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1
LM_STUDIO_MODEL=local-model
LAYOUT_BACKEND=docling-paddle
```

`LM_STUDIO_MODEL` muss zum geladenen Modell passen. Optional lassen sich `INPUT_ROOT` (Standard: `./data`), `RESULTS_ROOT` (`./Ergebnisse`), `LM_STUDIO_API_KEY` (`lm-studio`) und `LM_STUDIO_ENABLE_THINKING` (`false`) setzen. Als alternatives Layout-Backend ist `pymupdf` verfügbar.

```bash
# Alle drei Prompt-Varianten für einen Artikel
python main.py 20323-000

# Einzelnen Prompt verwenden
python main.py 20323-000 --prompt-file prompts/zero_shot.txt

# Layout-Verarbeitung mit Dummy-Ergebnis, ohne LLM-Aufruf
OFFLINE_MODE=true python main.py 20323-000
```

Ohne Artikelnummer fragt das Programm interaktiv danach. Zum Ausführen der Auswertungen zusätzlich `jupyterlab pandas seaborn matplotlib` installieren und die Notebooks mit `study/` als Arbeitsverzeichnis öffnen.

## Lizenz

Copyright 2026 Jonas Osswald.

Der eigene Quellcode dieses Projekts einschließlich des Auswertungscodes in den Notebooks sowie die eigene Dokumentation stehen unter der **[Apache License, Version 2.0](LICENSE)** (`SPDX-License-Identifier: Apache-2.0`). Dies gilt auch für selbst verfasste Prompt-Anweisungen, jedoch nicht für darin enthaltene fremde Dokumentauszüge. Die Software wird nach Maßgabe der Lizenz ohne Gewährleistungen bereitgestellt.

Vom Geltungsbereich dieser Apache-Lizenz ausgenommen sind:

- **Paper:** Für [short-paper/osswald_endfassung.pdf](short-paper/osswald_endfassung.pdf) gilt die im PDF angegebene **CC BY 4.0**.
- **Dokumente und Studiendaten:** Eingabedokumente unter `data/`, Laufartefakte unter `Ergebnisse/`, Bewertungs-CSV-Dateien und gespeicherte Notebook-Ausgaben werden durch diese Erklärung nicht unter Apache 2.0 lizenziert. Gleiches gilt für fremde Dokumentauszüge, insbesondere in den Few-Shot-Prompts. Rechte und vorhandene Hinweise der jeweiligen Rechteinhaber bleiben bestehen; diese Projektlizenz erteilt dafür keine Nutzungserlaubnis.
- **Abhängigkeiten und Modelle:** Es gelten deren jeweilige Lizenzen. Insbesondere wird [PyMuPDF unter AGPL oder einer kommerziellen Lizenz](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright) angeboten. Die Apache-Lizenz des eigenen Codes ersetzt diese Bedingungen nicht; bei Weitergabe oder Bereitstellung der kombinierten Anwendung sind sie gesondert zu beachten.
