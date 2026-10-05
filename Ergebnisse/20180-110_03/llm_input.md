# LLM-Eingabe

## Systemprompt

Du bist ein hochpräziser KI-Assistent für die Datenextraktion aus PLM-Dokumenten (Product Lifecycle Management). Deine ausschließliche Spezialisierung liegt auf der Etikettierung (Labels). 

DEINE AUFGABE:
Analysiere die bereitgestellten Dokumente (dies können Verpackungsvorschriften ODER Beispiel-Labels ODER beides sein) und extrahiere AUSSCHLIESSLICH, welche Verpackungsebene ein Label benötigt und welche Datenfelder auf diesem Label stehen müssen. Ignoriere alle anderen Prüfmerkmale oder allgemeinen Dokumenteninformationen.

AUFBAU DER EINGABEDATEN:
Du erhältst den Text des Dokuments. Layout-Elemente wie Checkboxen wurden bereits direkt in den Text integriert.
Ein angekreuztes Kästchen wird als "[X]" dargestellt, ein leeres Kästchen als "[ ]".

ALLGEMEINE REGELN FÜR DIE EXTRAKTION:
1. Sprache: Verwende für die extrahierten Werte exakt die erkannte Sprache des Originaldokuments.
2. Felder statt Werte: Wenn du ein Beispiel-Label liest (z.B. "Art.Nr: 40402-405"), extrahiere die Kategorie/das Feld für die Überprüfung (z.B. "Artikelnummer"), nicht zwingend nur den starren Wert.
3. Fehlende Daten: Wenn keine Label-Informationen im Dokument existieren, gib ein leeres Array `[]` unter dem Schlüssel "labels" zurück. Nutze `null` für Strings, falls keine Daten vorhanden sind.

SZENARIO A - WENN DAS DOKUMENT EINE VERPACKUNGSVORSCHRIFT IST:
- Lies den Text von oben nach unten.
- Achte auf die Checkboxen "[X]" und "[ ]" im fließenden Text. (Beispiel: "Kennzeichnung Außenverpackung: [X] Ja").
- Befüllen: Füge nur dann ein Objekt in das Array `labels` ein, wenn bei der jeweiligen Ebene das Kästchen für "Ja" angekreuzt ist (`[X] Ja`). Bei "Nein" oder wenn das "Ja"-Kästchen leer ist (`[ ] Ja`), ignoriere diese Ebene. Den "label_inhalt" entnimmst du den direkt folgenden Textstellen und markierten Checkboxen (z.B. "[X] Artikelnummer").

SZENARIO B - WENN DAS DOKUMENT EIN REINES BEISPIEL-LABEL IST:
Wenn das Dokument keine Checkboxen oder Vorschriften enthält, sondern ein abgedrucktes Etikett ist:
- Setze als "verpackungsebene" den Wert "Beispiel-Label" (außer aus dem Text geht eindeutig eine spezifische Ebene hervor).
- Liste unter "label_inhalt" alle relevanten Datenfelder auf, die auf diesem Label zu sehen sind und geprüft werden müssen (z.B. Barcode, Artikelnummer, Chargennummer, Menge, Datum).

OUTPUT-FORMAT:
Antworte AUSSCHLIESSLICH mit einem validen JSON-Objekt. Generiere keinen Begleittext, keine Markdown-Formatierung um das JSON herum (kein ```json ... ```) und keine Erklärungen. Das JSON muss exakt folgendem Schema entsprechen:

{
  "dokumentensprache": "Sprache des Dokuments (z.B. Deutsch, English)",
  "artikelnummer": "Exakte Artikelnummer aus dem Dokument oder null",
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

Packaging specification 20180-110 SystemCarrier performance Project name Project number Change number Muli 6519007 - Document class Document number Packaging Specification D289949 Version: 000 Packaging specification/Verpackungsvorschrift This packaging specification applies to/Diese Verpackungsvorschrift ist anzuwenden für: Erbe article no./Erbe Artikel Nr.: Designation/Bezeichnung: 20180-110 SystemCarrier performance Image of packaging (not mandatory)/Abbildung der Verpackung (nicht zwingend erforderlich): FB_0526_Packaging specification/Verpackungsvorschrift Based on master template OID: 1501230, Version: 10 Version: Page: 3 1/4 Packaging specification 20180-110 SystemCarrier performance Project name Project number Change number Muli 6519007 - Document class Document number Packaging Specification D289949 Version: 000 Delivery conditions/Anlieferbedingungen: 1. Delivery on pallet mandatory/Anlieferung auf Palette zwingend erforderlich: [X] Yes/Ja [ ] No/Nein Pallet dimensions/Palettenabmaße: Length/Länge: Width/Breite: 0,7 Meter(s) 0,7 Meter(s) Height/Höhe: 0,15 Meter(s) 2. Specifications/Spezifikationen To be supplied in ESD packaging/Anlieferung in ESD-Verpackung: [ ] Yes/Ja [X] No/Nein To be supplied in cleanroom compatible packaging/Anlieferung in Reinraum-geeigneter Verpackung: [ ] Yes/Ja [X] No/Nein 3. Packaging levels/Verpackungsebenen Packaging level 0 is the smallest packing unit and must always be defined. If required, higher packaging levels can be defined. Verpackungsebene 0 ist die kleinste Verpackungseinheit und ist in jedem Fall zu definieren - Bei Bedarf können zusätzlich höhere Verpackungsebenen definiert werden. Packaging level 0/Verpackungsebene 0: Type/Art: [ ] Reusable packaging/Mehrwegbehälter [ ] Cardboard/Kartonage [ ] Bag/Beutel [X] Other/Sonstiges: Einweg-Palette Content quantity of packaging level 0 in pcs./Inhaltsmenge der Verpackungsebene 0 in Stk: 1 Length/Länge: 700 mm Dimensions of packaging level 0/Abmessungen der Verpackungsebene 0: Width/Breite: 700 mm Height/Höhe: 1165 mm Label on packaging level 0/Kennzeichnung der Verpackungsebene 0 mit Label: [X] [ ] Yes/Ja No/Nein Content of the label/Labelinhalt: [X] [X] Erbe article no./Erbe-Artikel Nr. Designation/Bezeichnung [X] [X] [X] Quantity/Menge Lot no. or SN/Lot- bzw. SN Expiry date or Manufacturing date/Mindesthaltbarkeitsdatum bzw. [X] Herstelldatum Barcode  Content/Inhalt: [ ] [X] Erbe article no./Erbe Artikel Nr. + Lot no. or SN/Lot- bzw. SN + UDI-Code Other/Sonstiges: FB_0526_Packaging specification/Verpackungsvorschrift Based on master template OID: 1501230, Version: 10 Version: Page: 3 2/4 Packaging specification 20180-110 SystemCarrier performance Project name Project number Change number Muli 6519007 - Document class Document number Packaging Specification D289949 Version: 000 Packaging level 1/Verpackungsebene 1: Type/Art: [ ] Reusable packaging/Mehrwegbehälter [ ] Cardboard/Kartonage [ ] Bag/Beutel [ ] Other/Sonstiges: Content quantity of packaging level 1 in pcs./Inhaltsmenge der Verpackungsebene 1 in Stk: Dimensions of packaging level 1/Abmessungen der Verpackungsebene 1: Length/Länge: mm Width/Breite: mm Height/Höhe: mm Label on packaging level 1/Kennzeichnung der Verpackungsebene 1 mit Label: [ ] [ ] Yes/Ja No/Nein Content of the label/Labelinhalt: [ ] Erbe article no./Erbe-Artikel Nr. [ ] [ ] [ ] [ ] Designation/Bezeichnung Quantity/Menge Lot no. or SN/Lot- bzw. SN Expiry date or Manufacturing date/Mindesthaltbarkeitsdatum bzw. [ ] Herstelldatum Barcode  Content/Inhalt: [ ] [ ] Erbe article no./Erbe Artikel Nr. + Lot no. or SN/Lot- bzw. SN + Other/Sonstiges: [ ] Additional packaging levels/weitere Verpackungsebenen: 4. Article/Einzelartikel Label on article/Kennzeichnung des Einzelartikel mit Label: [ ] Yes/Ja [ ] No/Nein Label content/Labelinhalt: [ ] [ ] [ ] [ ] Erbe article no./Erbe-Artikel Nr. Designation/Bezeichnung Quantity/Menge Lot no. or SN/Lot- bzw. SN [ ] bzw. Herstelldatum Expiry date or manufacturing date/Mindesthaltbarkeitsdatum FB_0526_Packaging specification/Verpackungsvorschrift Based on master template OID: 1501230, Version: 10 Version: Page: 3 3/4 Packaging specification 20180-110 SystemCarrier performance Project name Project number Change number Muli 6519007 - Document class Document number Packaging Specification D289949 Version: 000 [ ] Barcode  Content/Inhalt: [ ] [ ] Erbe article no./Erbe Artikel Nr. + Lot no. or SN/Lot- bzw. SN + Other/Sonstiges: Comments and additional information on transport and delivery conditions/Vermerke und Zusätze zu den Transport-, Lieferbedingungen: Siehe Verpackungsschritte 1-8 (Bilder Seite 1) FB_0526_Packaging specification/Verpackungsvorschrift Based on master template OID: 1501230, Version: 10 Version: Page: 3 4/4
