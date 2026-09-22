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

Verpackungsvorschrift 20180-100/-101 Systemträger compact und compact plus Projektname Projektnummer ÄM-Nummer Muli 6519007 - Dokumentklasse Dokumentnummer Verpackungsvorschrift D208847 Version: 001 Verpackungsvorschrift deutsch Die Verpackungsvorschrift ist anzuwenden für: Erbe-Artikel Nr.: Bezeichnung: 20180-100 20180-101 Systemträger compact plus Systemträger compact Abbildung der Verpackung (nicht zwingend erforderlich): FB_0526_Verpackungsvorschrift deutsch Basiert auf Dokumentvorlage OID: 1501230, Version: 10 Version: Seite: 2 1/3 Verpackungsvorschrift 20180-100/-101 Systemträger compact und compact plus Projektname Projektnummer ÄM-Nummer Muli 6519007 - Dokumentklasse Dokumentnummer Verpackungsvorschrift D208847 Version: 001 Anlieferbedingungen: 1. Anlieferung auf Palette zwingend erforderlich: [X] Ja [ ] Nein Produkt wird einzeln auf produktspezifischer Einweg-Palette angeliefert. 2. Spezifikationen Anlieferung in ESD-Verpackung: [ ] Ja [X] Nein Anlieferung in Reinraum geeigneter Verpackung: [ ] Ja [X] Nein 3. Verpackungsebenen Verpackungsebene 0 ist die kleinste Verpackungseinheit und ist in jedem Fall zu definieren - Bei Bedarf können zusätzlich höhere Verpackungsebenen definiert werden. Verpackungsebene 0: Art: [ ] Mehrwegbehälter [ ] Kartonage [ ] Beutel [X] sonstiges: auf Einweg-Palette Inhaltsmenge der Verpackungsebene 0 in Stk.: 1 Länge: 700 mm Abmessungen der Verpackungsebene 0: Breite: 700 mm Höhe: 1165 mm Kennzeichnung der Verpackungsebene 0 mit Label: [X] Ja [ ] Nein Labelinhalt: Sonstiges: N/A + Herstelldatum [X] [X] [X] Erbe-Artikel Nr. Mindesthaltbarkeitsdatum bzw. Herstelldatum Barcode  [X] Bezeichnung Inhalt: [ ] Erbe-Artikel Nr. + [X] Menge [X] [X] Lot- bzw. SN + UDI-Code Lot- bzw. SN [ ] Verpackungsebene 1: Art: [ ] Mehrwegbehälter [ ] Kartonage [ ] Beutel [ ] sonstiges: Inhaltsmenge der Verpackungsebene 1 in Stk.: Länge: mm Abmessungen der Verpackungsebene 1: Breite: mm Höhe: mm Kennzeichnung der Verpackungsebene 1 mit Label: [ ] Ja [ ] Nein Labelinhalt: Sonstiges: [ ] [ ] [ ] Erbe-Artikel Nr. Mindesthaltbarkeitsdatum bzw. Herstelldatum Barcode  [ ] Bezeichnung Inhalt: [ ] Erbe-Artikel Nr. + [ ] Menge [ ] Lot- bzw. SN + [ ] Lot- bzw. SN FB_0526_Verpackungsvorschrift deutsch Basiert auf Dokumentvorlage OID: 1501230, Version: 10 Version: Seite: 2 2/3 Verpackungsvorschrift 20180-100/-101 Systemträger compact und compact plus Projektname Projektnummer ÄM-Nummer Muli 6519007 - Dokumentklasse Dokumentnummer Verpackungsvorschrift D208847 Version: 001 [ ] weitere Verpackungsebenen: 4. Einzelartikel Kennzeichnung des Einzelartikel mit Label: [ ] Ja [ ] Nein Labelinhalt: Sonstiges: [ ] [ ] [ ] Erbe-Artikel Nr. Mindesthaltbarkeitsdatum bzw. Herstelldatum Barcode  [ ] Bezeichnung Inhalt: [ ] Erbe-Artikel Nr. + [ ] Menge [ ] Lot- bzw. SN + [ ] Lot- bzw. SN Vermerke und Zusätze zu den Transport-, Lieferbedingungen: Artikel dürfen für Transport 2-lagig gestapelt werden. FB_0526_Verpackungsvorschrift deutsch Basiert auf Dokumentvorlage OID: 1501230, Version: 10 Version: Seite: 2 3/3
