# WV Prototyp zur Dokumentenextraktion

## Prompt-Auswahl

Bei der interaktiven Auswahl startet Option 3 (`refinement`) zunächst die
Zero-Shot-Extraktion. Das Ergebnis wird anschließend gegen das erwartete
JSON-Schema geprüft. Bei Fehlern wird `prompts/refinement_prompt.txt` mit dem
automatischen Feedback und dem Dokumentkontext erneut an das LLM gesendet.

Die Anzahl der Korrekturversuche lässt sich über
`REFINEMENT_MAX_ATTEMPTS` konfigurieren und steht standardmäßig auf `1`.
Der Prompt kann über `REFINEMENT_PROMPT_FILE` überschrieben werden.

## PDF-Extraktion

Standardmäßig wird der hybride `docling-paddle`-Extractor verwendet. Docling
verarbeitet Seiten mit brauchbarem Textlayer und PaddleOCR übernimmt Scan- oder
beschädigte Seiten. Für einen Vergleich mit dem bisherigen Extractor kann der
Backend-Modus gesetzt werden:

```text
LAYOUT_BACKEND=pymupdf
```

PaddleOCR speichert erkannte Wörter mit Bounding Box und Konfidenz. Ergebnisse
unterhalb der Konfidenz von `0.35` werden nicht an das LLM weitergegeben.
