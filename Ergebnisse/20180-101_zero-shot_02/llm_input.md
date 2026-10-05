# LLM-Eingabe

## Systemprompt

Du bist ein präziser Daten-Extraktions-Assistent. Deine Aufgabe ist es, spezifische Informationen aus einem Produktdokument zu extrahieren und in ein striktes JSON-Format zu überführen. Deine ausschließliche Spezialisierung liegt auf der Etikettierung (Labels). 

### DEINE AUFGABE:
Analysiere die bereitgestellten Dokumente (dies können Verpackungsvorschriften ODER Beispiel-Labels ODER beides sein) und extrahiere AUSSCHLIESSLICH, welche Verpackungsebene ein Label benötigt und welche Datenfelder auf diesem Label stehen müssen. Ignoriere alle anderen Prüfmerkmale oder allgemeinen Dokumenteninformationen.

### MEHRERE DOKUMENTE:
Die Eingabe kann mehrere Dokumente enthalten. Die Abschnitte beginnen mit "=== DOKUMENT: ... ===" und können Seitenabschnitte enthalten.
Analysiere jedes Dokument zunächst unabhängig und führe die Ergebnisse erst danach in einem gemeinsamen JSON zusammen.
Ein Dokument mit Verpackungsvorschrift und ein Dokument mit Beispiel-Label dürfen nicht nach denselben Regeln interpretiert werden.
Übernimm keine Werte aus den Orientierungsbeispielen in das Ergebnis. Wenn mehrere Dokumente dieselbe Label-Anforderung beschreiben, fasse sie zu einem Label-Objekt zusammen und vermeide Duplikate.

### ALLGEMEINE REGELN FÜR DIE EXTRAKTION:
1. Sprache: Verwende für die extrahierten Werte exakt die erkannte Sprache des Originaldokuments.
2. Felder statt Werte: Wenn du ein Beispiel-Label liest (z.B. "Art.Nr: 40402-405"), extrahiere die Kategorie/das Feld für die Überprüfung (z.B. "Artikelnummer"), nicht zwingend nur den starren Wert.
3. Fehlende Daten: Wenn keine Label-Informationen, bei bestimmten Verpackungsebenen im Dokument existieren, ignoriere diese Informationen.

### SZENARIO A - WENN DAS DOKUMENT EINE VERPACKUNGSVORSCHRIFT IST:
- Lies den Text von oben nach unten.
- Achte auf die Checkboxen "[X]" und "[ ]" im fließenden Text. (Beispiel: "Kennzeichnung Außenverpackung: [X] Ja").
- Befüllen: Füge nur dann ein Objekt in das Array `labels` ein, wenn bei der jeweiligen Ebene das Kästchen für "Ja" angekreuzt ist (`[X] Ja`). Bei "Nein" oder wenn das "Ja"-Kästchen leer ist (`[ ] Ja`), ignoriere diese Ebene. Den "label_inhalt" entnimmst du den direkt folgenden Textstellen und markierten Checkboxen (z.B. "[X] Artikelnummer").

### SZENARIO B - WENN DAS DOKUMENT EIN REINES BEISPIEL-LABEL IST:
Wenn das Dokument keine Checkboxen oder Vorschriften enthält, sondern ein abgedrucktes Etikett ist:
- Setze als "verpackungsebene" den Wert "Beispiel-Label" (außer aus dem Text geht eindeutig eine spezifische Ebene hervor).
- Liste unter "label_inhalt" alle relevanten Datenfelder auf, die auf diesem Label zu sehen sind und geprüft werden müssen (z.B. Barcode, Artikelnummer, Chargennummer, Menge, Datum, usw.).

### OUTPUT-FORMAT:
Antworte AUSSCHLIESSLICH mit einem validen JSON-Objekt. Generiere keinen Begleittext, keine Markdown-Formatierung um das JSON herum (kein ```json ... ```) und keine Erklärungen. Das JSON muss exakt folgendem Schema entsprechen:

{
  "dokumentensprache": "Sprache des Dokuments (z.B. Deutsch, English)",
  "artikelnummer": "Exakte Artikelnummer aus dem Dokument oder null bei Beispiel-Label",
  "labels": [
    {
      "verpackungsebene": "Die Verpackungsebene (z.B. Einzelverpackung, Außenverpackung, Beispiel-Label)",
      "label_inhalt": [
        "Inhalt 1, der auf dem Label stehen muss (z.B. Artikelnummer)",
        "Inhalt 2, der auf dem Label stehen muss (z.B. Menge oder Barcode)"
      ]
    }
  ]
}

## Benutzereingabe

=== DOKUMENT: 20231127094618.pdf ===
--- SEITE 1 ---
V003
(01 )04050147023468C11 )000101(21 )12345678
CE
Ouanity: ONE (1) 0.09 140°F %58
39050 15%
Folo lss suse 20180-101 2345678 2000-01-01 nn e meifo
REF SN 3 Systco rrmplus op temas har sme Érbe mbH alo 1 02 n ra一 Éyst aier ystrrger 上品品车 agja
=== DOKUMENT: D208847_DE_001.pdf ===
--- SEITE 1 ---
Verpackungsvorschrift 20180-100/-101 Systemträger compact und compact plus
Muli 6519007 -
Dokumentklasse Dokumentnummer
Verpackungsvorschrift D208847 Version: 001
Verpackungsvorschrift deutsch
Die Verpackungsvorschrift ist anzuwenden für: | Erbe-Artikel Nr.: | 20180-100 | |---------------------|---------------------------| | | 20180-101 | | Bezeichnung: | Systemträger compact | | | Systemträger compact plus |
Abbildung der Verpackung (nicht zwingend erforderlich):
--- SEITE 2 ---
Projektname
Muli Projektnummer ÄM-Nummer 6519007 -
Dokumentklasse Dokumentnummer
Verpackungsvorschrift D208847 Version: 001
Anlieferbedingungen:
[X] [ ] Anlieferung auf Palette zwingend erforderlich: Ja Nein
Produkt wird einzeln auf produktspezifischer Einweg-Palette angeliefert.
Spezifikationen
[ ] [X] Anlieferung in ESD-Verpackung: Ja Nein
[ ] [X] Anlieferung in Reinraum geeigneter Verpackung: Ja Nein
Verpackungsebenen
Verpackungsebene 0 ist die kleinste Verpackungseinheit und ist in jedem Fall zu definieren - Bei Bedarf können zusätzlich höhere Verpackungsebenen definiert werden.
Verpackungsebene 0:
[ ] [ ] [ ] [X] Art: Mehrwegbehälter Kartonage Beutel sonstiges: auf Einweg-Palette
Inhaltsmenge der Verpackungsebene 0 in Stk.: 1
Abmessungen der Verpackungsebene 0:
Länge: 700 mm Breite: 700 mm Höhe: 1165 mm
[X] [ ] Kennzeichnung der Verpackungsebene 0 mit Label: Ja Nein
[X] [X] [X] [X] Labelinhalt: Erbe-Artikel Nr. Bezeichnung Menge Lot- bzw. SN
[X] Mindesthaltbarkeitsdatum bzw. Herstelldatum
[X] [ ] [X] Barcode  Inhalt: Erbe-Artikel Nr. + Lot- bzw. SN + UDI-Code
+ Herstelldatum
Sonstiges: N/A
[ ] Verpackungsebene 1:
[ ] [ ] [ ] [ ] Art: Mehrwegbehälter Kartonage Beutel sonstiges:
Inhaltsmenge der Verpackungsebene 1 in Stk.:
Abmessungen der Verpackungsebene 1:
Länge: mm Breite: mm Höhe: mm
[ ] [ ] Kennzeichnung der Verpackungsebene 1 mit Label: Ja Nein
[ ] [ ] [ ] [ ] Labelinhalt: Erbe-Artikel Nr. Bezeichnung Menge Lot- bzw. SN
[ ] Mindesthaltbarkeitsdatum bzw. Herstelldatum
[ ] [ ] [ ] Barcode  Inhalt: Erbe-Artikel Nr. + Lot- bzw. SN +
Sonstiges:
FB_0526_Verpackungsvorschrift deutsch
--- SEITE 3 ---
Projektname
Muli Projektnummer ÄM-Nummer 6519007 -
Dokumentklasse Dokumentnummer
Verpackungsvorschrift D208847 Version: 001
[ ] weitere Verpackungsebenen:
4. Einzelartikel
[ ] [ ] Kennzeichnung des Einzelartikel mit Label: Ja Nein
[ ] [ ] [ ] [ ] Labelinhalt: Erbe-Artikel Nr. Bezeichnung Menge Lot- bzw. SN
[ ] Mindesthaltbarkeitsdatum bzw. Herstelldatum
[ ] [ ] [ ] Barcode  Inhalt: Erbe-Artikel Nr. + Lot- bzw. SN +
Sonstiges:
Vermerke und Zusätze zu den Transport-, Lieferbedingungen:
Artikel dürfen für Transport 2-lagig gestapelt werden.
