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

=== DOKUMENT: 20240620081328.pdf ===
--- SEITE 1 ---
000A
(01 )04050147023710C11 )000101(21 )12345678
CE
Ouantity: ONE (1) 0.09 140F 558
39050 15%
Folo lss suse 20180-110 2345678 2000-01-01 nn er meif
REF SN 3 Systrrrnce h t on op temas har sme Érbe mbH aldhoE 1 207 any Éyste ier ystger 上品品车 wrm/ agja
=== DOKUMENT: D289949_DE_000.pdf ===
--- SEITE 1 ---
Muli Project number Change number 6519007 -
Document class Document number
Packaging Specification D289949 Version: 000
Packaging specification/Verpackungsvorschrift
This packaging specification applies to/Diese Verpackungsvorschrift ist anzuwenden für:
Erbe article no./Erbe Artikel Nr.:
Designation/Bezeichnung: 20180-110 SystemCarrier performance
Image of packaging (not mandatory)/Abbildung der Verpackung (nicht zwingend erforderlich):
--- SEITE 2 ---
Project name
Muli Project number Change number 6519007 -
Document class Document number
Packaging Specification D289949 Version: 000
Delivery conditions/Anlieferbedingungen:
[X] Delivery on pallet mandatory/Anlieferung auf Palette zwingend erforderlich: Yes/Ja
[ ] No/Nein
[ ] [X] Yes/Ja No/Nein
[ ] [X] Yes/Ja No/Nein Pallet dimensions/Palettenabmaße: Length/Länge: 0,7 Meter(s) Width/Breite: 0,7 Meter(s) Height/Höhe: 0,15 Meter(s) Specifications/Spezifikationen To be supplied in ESD packaging/Anlieferung in ESD-Verpackung: To be supplied in cleanroom compatible packaging/Anlieferung in Reinraum-geeigneter Verpackung:
Packaging levels/Verpackungsebenen
Packaging level 0 is the smallest packing unit and must always be defined. If required, higher packaging levels can be defined.
Verpackungsebene 0 ist die kleinste Verpackungseinheit und ist in jedem Fall zu definieren - Bei Bedarf können zusätzlich höhere Verpackungsebenen definiert werden.
Packaging level 0/Verpackungsebene 0:
[ ] Type/Art: Reusable packaging/Mehrwegbehälter
[ ] Cardboard/Kartonage
[ ] Bag/Beutel
[X] Other/Sonstiges: Einweg-Palette
Content quantity of packaging level 0 in pcs./Inhaltsmenge der Verpackungsebene 0 in Stk: 1
Dimensions of packaging level 0/Abmessungen der Verpackungsebene 0:
Length/Länge: 700 mm Width/Breite: 700 mm Height/Höhe: 1165 mm
[X] Label on packaging level 0/Kennzeichnung der Verpackungsebene 0 mit Label: Yes/Ja
[ ] No/Nein
Content of the label/Labelinhalt:
[X] Erbe article no./Erbe-Artikel Nr.
[X] Designation/Bezeichnung
[X] Quantity/Menge
[X] Lot no. or SN/Lot- bzw. SN
[X] Expiry date or Manufacturing date/Mindesthaltbarkeitsdatum bzw.
Herstelldatum
[X] Barcode
[ ]  Content/Inhalt: Erbe article no./Erbe Artikel Nr. +
[X]
Other/Sonstiges: Lot no. or SN/Lot- bzw. SN + UDI-Code
FB_0526_Packaging specification/Verpackungsvorschrift
--- SEITE 3 ---
Project name
Muli Project number Change number 6519007 -
Document class Document number
Packaging Specification D289949 Version: 000
Packaging level 1/Verpackungsebene 1:
[ ] Type/Art: Reusable packaging/Mehrwegbehälter
[ ] Cardboard/Kartonage
[ ] Bag/Beutel
[ ] Other/Sonstiges:
Content quantity of packaging level 1 in pcs./Inhaltsmenge der Verpackungsebene 1 in Stk:
Dimensions of packaging level 1/Abmessungen der Verpackungsebene 1:
Length/Länge: mm Width/Breite: mm Height/Höhe: mm
[ ] Label on packaging level 1/Kennzeichnung der Verpackungsebene 1 mit Label: Yes/Ja
[ ] No/Nein
Content of the label/Labelinhalt:
[ ] Erbe article no./Erbe-Artikel Nr.
[ ] Designation/Bezeichnung
[ ] Quantity/Menge
[ ] Lot no. or SN/Lot- bzw. SN
[ ] Expiry date or Manufacturing date/Mindesthaltbarkeitsdatum bzw. Herstelldatum
[ ] Barcode
[ ]  Content/Inhalt: Erbe article no./Erbe Artikel Nr. +
[ ]
Other/Sonstiges:
[ ] Additional packaging levels/weitere Verpackungsebenen:
Article/Einzelartikel
[ ] [ ] Label on article/Kennzeichnung des Einzelartikel mit Label: Yes/Ja No/Nein
[ ] Label content/Labelinhalt: Erbe article no./Erbe-Artikel Nr.
[ ] Designation/Bezeichnung
[ ] Quantity/Menge
[ ] Lot no. or SN/Lot- bzw. SN
[ ] Expiry date or manufacturing date/Mindesthaltbarkeitsdatum bzw. Herstelldatum Lot no. or SN/Lot- bzw. SN +
FB_0526_Packaging specification/Verpackungsvorschrift
Page:
--- SEITE 4 ---
Project name
Muli Project number Change number 6519007 -
Document class Document number
Packaging Specification D289949 Version: 000
[ ] Barcode
[ ]  Content/Inhalt: Erbe article no./Erbe Artikel Nr. +
[ ]
Other/Sonstiges:
Comments and additional information on transport and delivery conditions/Vermerke und Zusätze zu den Transport-, Lieferbedingungen:
Siehe Verpackungsschritte 1-8 (Bilder Seite 1) Lot no. or SN/Lot- bzw. SN +
