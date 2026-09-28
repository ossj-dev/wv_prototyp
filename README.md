# WV Prototyp zur Dokumentenextraktion

## Prompt-Auswahl

Bei der interaktiven Auswahl startet Option 3 (`refinement`) zunächst die
Zero-Shot-Extraktion. Das Ergebnis wird anschließend gegen das erwartete
JSON-Schema geprüft. Bei Fehlern wird `prompts/refinement_prompt.txt` mit dem
automatischen Feedback und dem Dokumentkontext erneut an das LLM gesendet.

Die Anzahl der Korrekturversuche lässt sich über
`REFINEMENT_MAX_ATTEMPTS` konfigurieren und steht standardmäßig auf `1`.
Der Prompt kann über `REFINEMENT_PROMPT_FILE` überschrieben werden.
