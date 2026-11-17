# LLM-Eingabe

## Reasoning-Modus

Internal-CoT

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

=== DOKUMENT: D267408_DE_001.pdf ===
--- SEITE 1 ---
packaging intructions 30160-863
Project name Project number Change number
Aurora 6520001 26768
Document class Document number
Packaging Specification D267408 Version: 001
Packaging specification/Verpackungsvorschrift
This packaging specification applies to/Diese Verpackungsvorschrift ist anzuwenden für:
Erbe article no./Erbe Artikel Nr.:
Designation/Bezeichnung: 30160-863 PB-MCM HW PB-Measurement & Control Modul
Image of packaging (not mandatory)/Abbildung der Verpackung (nicht zwingend erforderlich):
4
--- SEITE 2 ---
Project name
Aurora Project number Change number 6520001 26768
Document class Document number
Packaging Specification D267408 Version: 001
Delivery conditions/Anlieferbedingungen:
[ ] Delivery on pallet mandatory/Anlieferung auf Palette zwingend erforderlich: Yes/Ja
[X] No/Nein
[X] [ ] Yes/Ja No/Nein
[ ] [X] Yes/Ja No/Nein Specifications/Spezifikationen To be supplied in ESD packaging/Anlieferung in ESD-Verpackung: To be supplied in cleanroom compatible packaging/Anlieferung in Reinraum-geeigneter Verpackung:
Packaging levels/Verpackungsebenen
Packaging level 0 is the smallest packing unit and must always be defined. If required, higher packaging levels can be defined.
Verpackungsebene 0 ist die kleinste Verpackungseinheit und ist in jedem Fall zu definieren - Bei Bedarf können zusätzlich höhere Verpackungsebenen definiert werden.
Packaging level 0/Verpackungsebene 0:
[X] Type/Art: Reusable packaging/Mehrwegbehälter
[ ] Cardboard/Kartonage
[ ] Bag/Beutel
[ ] Other/Sonstiges:
Content quantity of packaging level 0 in pcs./Inhaltsmenge der Verpackungsebene 0 in Stk: 21
Dimensions of packaging level 0/Abmessungen der Verpackungsebene 0:
Length/Länge: 400 mm Width/Breite: 300 mm Height/Höhe: 220 mm
[X] Label on packaging level 0/Kennzeichnung der Verpackungsebene 0 mit Label: Yes/Ja
[ ] No/Nein
Content of the label/Labelinhalt:
[X] Erbe article no./Erbe-Artikel Nr.
[X] Designation/Bezeichnung
[X] Quantity/Menge + Unit/Einheit
[X] Lot no. or SN/Lot- bzw. SN
[ ] Expiry date/Verfallsdatum
[ ] Manufacturing Date/Herstelldatum
[X] Barcode
[X]  Content/Inhalt: Erbe article no./Erbe Artikel Nr. +
[X] Lot no. or SN/Lot- bzw. SN +
FB_0526_Packaging specification/Verpackungsvorschrift Other/Sonstiges:
--- SEITE 3 ---
Project name
Aurora Project number Change number 6520001 26768
Document class Document number
Packaging Specification D267408 Version: 001
4. Article/Einzelartikel
[X] [ ] Label on article/Kennzeichnung des Einzelartikel mit Label: Yes/Ja No/Nein
[X] Label content/Labelinhalt: Erbe article no./Erbe-Artikel Nr.
[ ] Designation/Bezeichnung
[ ] Quantity/Menge + Unit/Einheit
[X] Lot no. or SN/Lot- bzw. SN
[ ] Expiry date/Verfallsdatum
[ ] Manufacturing Date/Herstelldatum
[X] Barcode
[X]  Content/Inhalt: Erbe article no./Erbe Artikel Nr. +
[X]
Other/Sonstiges:
Comments and additional information on transport and delivery conditions/Vermerke und Zusätze zu den Transport-, Lieferbedingungen: Lot no. or SN/Lot- bzw. SN +
