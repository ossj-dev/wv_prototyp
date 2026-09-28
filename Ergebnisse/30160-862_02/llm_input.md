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

=== DOKUMENT: D108713_DE_001.pdf ===
--- SEITE 1 ---
REF-Nr.ERBE
Lot kann
OP….; WO…
Änderungsstand Mögliche Teilung Datamatrix Code
REF-Nr. und LOT
z.B. 12345-678OP123456
 Etikettenwerkstoff. Polyesterfolie mit Acrylatkleber
 Bei Platzmangel kann das Label geteilt werden
 Labelgröße kann vom Zulieferer bestimmt werden
 Mindestschriftgröße 2mm
 Das Symbol REF kann auch nur als Text dargestellt werden
 Die LOT-Nummer und der Status ist entsprechend dem Arbeitsauftrag einzutragen
 Dem Zulieferer wird freigestellt den Datamatrixcode mit einer alphanumerischen Trennung
zwischen REF-Nr. und LOT (z.B. 12345-678OP123456) oder ohne Trennung (z.B. 12345-678123456)
auszuführen
 Mindestgröße Datamatrixcode 6 x 6 mm
Alle mit * gekennzeichneten Zeichnungsobjekte haben sich gegenüber der Vorgängerversion geändert! . . . 2 : 1 .
Werkstoff, Bezeichnung, Lieferant Werkstoff-Nr. Volumen cm³ Maßstab
Status ERBE-Nr. ÄM-Nr. Datum Name Titel:
Gültig 30135-804 20023 Bearb. 07.06.2016 UWED Labellayout Chargenpflicht
Dokumentklasse Gepr. 07.06.2016 LAURAS 2D-Code Dokumentnummer: Version: Größe:
Produktkennzeichnung
Oberflächenbeschaffenheit nach ISO 1302
Maße ohne Toleranzangabe ISO 2768 - mH Elektromedizin GmbH D108713 001
Urspr.: Ers.für: Blatt: 1 / 1
=== DOKUMENT: D279711_DE_000.pdf ===
--- SEITE 1 ---
packaging instruction
Project name Project number Change number
Aurora 6520001 25242
Document class Document number
Packaging Specification D279711 Version: 000
Packaging specification/Verpackungsvorschrift
This packaging specification applies to/Diese Verpackungsvorschrift ist anzuwenden für:
Erbe article no./Erbe Artikel Nr.: Designation/Bezeichnung: PB-GM HW PB-Generator Module 30160-862
Image of packaging (not mandatory)/Abbildung der Verpackung (nicht zwingend erforderlich):
FB_0526_Packaging specification/Verpackungsvorschrift
Based on master template OID: 1501230, Version: 10 Version: Page:
3 1/4
--- SEITE 2 ---
packaging instruction
Project name Project number Change number
Aurora 6520001 25242
Document class Document number
Packaging Specification D279711 Version: 000
Delivery conditions/Anlieferbedingungen:
1. Delivery on pallet mandatory/Anlieferung auf Palette zwingend erforderlich: [ ] Yes/Ja
Pallet dimensions/Palettenabmaße: Length/Länge: Width/Breite: Height/Höhe: 1,2 Meter(s) 0,8 Meter(s) 1,4 Meter(s) [X] No/Nein
2. Specifications/Spezifikationen
To be supplied in ESD packaging/Anlieferung in ESD-Verpackung: [X] Yes/Ja [ ] No/Nein To be supplied in cleanroom compatible packaging/Anlieferung in Reinraum-geeigneter Verpackung: [ ] Yes/Ja [X] No/Nein
3. Packaging levels/Verpackungsebenen
Packaging level 0 is the smallest packing unit and must always be defined. If required, higher packaging levels can be defined. Verpackungsebene 0 ist die kleinste Verpackungseinheit und ist in jedem Fall zu definieren - Bei Bedarf können zusätzlich höhere Verpackungsebenen definiert werden.
Packaging level 0/Verpackungsebene 0: Type/Art: [X] Reusable packaging/Mehrwegbehälter
[ ] Cardboard/Kartonage
[ ] Bag/Beutel
[ ] Other/Sonstiges:
Content quantity of packaging level 0 in pcs./Inhaltsmenge der Verpackungsebene 0 in Stk: 24
Length/Länge: 400 mm Dimensions of packaging level 0/Abmessungen der Verpackungsebene 0: Width/Breite: 300 mm Height/Höhe: 170 mm
Label on packaging level 0/Kennzeichnung der Verpackungsebene 0 mit Label: [X] [ ] Yes/Ja No/Nein
Content of the label/Labelinhalt: [X]
[X]
[X]
[ ]
[ ]
[ ] Herstelldatum Erbe article no./Erbe-Artikel Nr. Designation/Bezeichnung Quantity/Menge Lot no. or SN/Lot- bzw. SN Expiry date or Manufacturing date/Mindesthaltbarkeitsdatum bzw. Barcode
 Content/Inhalt: [ ] Erbe article no./Erbe Artikel Nr. +
Other/Sonstiges: [ ] Lot no. or SN/Lot- bzw. SN +
FB_0526_Packaging specification/Verpackungsvorschrift
Based on master template OID: 1501230, Version: 10 Version: Page:
3 2/4
--- SEITE 3 ---
packaging instruction
Project name Project number Change number
Aurora 6520001 25242
Document class Document number
Packaging Specification D279711 Version: 000
Packaging level 1/Verpackungsebene 1: Type/Art: [ ] Reusable packaging/Mehrwegbehälter
[ ] Cardboard/Kartonage
[ ] Bag/Beutel
[ ] Other/Sonstiges:
Content quantity of packaging level 1 in pcs./Inhaltsmenge der Verpackungsebene 1 in Stk:
Length/Länge: mm Dimensions of packaging level 1/Abmessungen der Verpackungsebene 1: Width/Breite: mm Height/Höhe: mm
Label on packaging level 1/Kennzeichnung der Verpackungsebene 1 mit Label: [ ] [ ] Yes/Ja No/Nein
Content of the label/Labelinhalt: [ ]
[ ]
[ ]
[ ]
[ ]
[ ] Herstelldatum Erbe article no./Erbe-Artikel Nr. Designation/Bezeichnung Quantity/Menge Lot no. or SN/Lot- bzw. SN Expiry date or Manufacturing date/Mindesthaltbarkeitsdatum bzw. Barcode
 Content/Inhalt: [ ] Erbe article no./Erbe Artikel Nr. +
Other/Sonstiges: [ ] Lot no. or SN/Lot- bzw. SN +
[ ] Additional packaging levels/weitere Verpackungsebenen:
4. Article/Einzelartikel Label on article/Kennzeichnung des Einzelartikel mit Label: [X] Yes/Ja [ ] No/Nein
Label content/Labelinhalt: [X] [ ]
[ ]
[X]
[ ] bzw. Herstelldatum Erbe article no./Erbe-Artikel Nr. Designation/Bezeichnung Quantity/Menge Lot no. or SN/Lot- bzw. SN Expiry date or manufacturing date/Mindesthaltbarkeitsdatum
FB_0526_Packaging specification/Verpackungsvorschrift
Based on master template OID: 1501230, Version: 10 Version: Page:
3 3/4
--- SEITE 4 ---
packaging instruction
Project name Project number Change number
Aurora 6520001 25242
Document class Document number
Packaging Specification D279711 Version: 000
Other/Sonstiges: [X] Barcode  Content/Inhalt: [X] [X] Erbe article no./Erbe Artikel Nr. + Lot no. or SN/Lot- bzw. SN +
Comments and additional information on transport and delivery conditions/Vermerke und Zusätze zu den Transport-, Lieferbedingungen: KLT43/17 ink. Deckel HKP Gefache inkl. Einleger Boden und Deckel
FB_0526_Packaging specification/Verpackungsvorschrift
Based on master template OID: 1501230, Version: 10 Version: Page:
3 4/4
