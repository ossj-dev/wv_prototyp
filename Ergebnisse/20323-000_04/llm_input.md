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

Größe B=148 x H=95mm Alle mit * gekennzeichneten Zeichnungsobjekte haben sich gegenüber der Vorgängerversion geändert! . . . 1 : 1 . Werkstoff, Bezeichnung, Lieferant Werkstoff-Nr. Volumen cm³ Maßstab Status Gültig 20323-000 ERBE-Nr. 24809 ÄM-Nr. Bearb. Gepr. 06.02.2023 06.02.2023 Datum JMAKOWE E7243 Name Titel: Label Hauptfilterkassette 20323- 000 Dokumentklasse Dokumentnummer: Version: Größe: Produktkennzeichnung Oberflächenbeschaffenheit nach ISO 1302 Maße ohne Toleranzangabe ISO 2768 - mH Elektromedizin GmbH D147679 003 Urspr.: Ers.für: Blatt: 1 / 1 Hauptfilterkassette IES 3 Projektname Projektnummer ÄM‐Nummer ‐ Dokumentklasse Dokumentnummer Verpackungsvorschrift D163142 Version: 000 Verpackungsvorschrift deutsch Die Verpackungsvorschrift ist anzuwenden für: Erbe‐Artikel Nr.: 20323‐000 Bezeichnung: Hauptfilterkassette IES 3 Abbildung der Verpackung (nicht zwingend erforderlich): FB_0526_Verpackungsvorschrift deutsch Basiert auf Dokumentvorlage OID: 1501230, Version: 10 Version: Seite: 2 1/3 Hauptfilterkassette IES 3 Projektname Projektnummer ÄM‐Nummer ‐ Dokumentklasse Dokumentnummer Verpackungsvorschrift D163142 Version: 000 Anlieferbedingungen: 1. Anlieferung auf Palette zwingend erforderlich: [X] Ja [ ] Nein Palettenabmaße: Länge: 1,20 Meter Breite: 0,80 Meter Höhe: 1,45 Meter 2. Spezifikationen Anlieferung in ESD‐Verpackung: [ ] Ja [X] Nein Anlieferung in Reinraum geeigneter Verpackung: [ ] Ja [X] Nein 3. Verpackungsebenen Verpackungsebene 0 ist die kleinste Verpackungseinheit und ist in jedem Fall zu definieren ‐ Bei Bedarf können zusätzlich höhere Verpackungsebenen definiert werden. Verpackungsebene 0: Art: [ ] Mehrwegbehälter [ ] Kartonage [ ] Beutel [X] sonstiges: Palettenkarton Inhaltsmenge der Verpackungsebene 0 in Stk.: 90 (6 Lagen à 15 Stück) Abmessungen der Verpackungsebene 0: Länge: 1200 mm Breite: 800 mm Höhe: 1450 mm Kennzeichnung der Verpackungsebene 0 mit Label: [X] Ja [ ] Nein Labelinhalt: [X] Erbe‐Artikel Nr. [X] Bezeichnung [X] Menge [X] Lot‐ bzw. SN [ ] Mindesthaltbarkeitsdatum bzw. Herstelldatum [X] Barcode  Inhalt: [X] Erbe‐Artikel Nr. + [X] Lot‐ bzw. SN + Sonstiges: Leerräume m. Wellpappe auffüllen [ ] Verpackungsebene 1: Art: [ ] Mehrwegbehälter [ ] Kartonage [ ] Beutel [ ] sonstiges: Inhaltsmenge der Verpackungsebene 1 in Stk.: Abmessungen der Verpackungsebene 1: Länge: mm Breite: mm Höhe: mm Kennzeichnung der Verpackungsebene 1 mit Label: [ ] Ja [ ] Nein Labelinhalt: [ ] Erbe‐Artikel Nr. [ ] Bezeichnung [ ] Menge [ ] Lot‐ bzw. SN [ ] Mindesthaltbarkeitsdatum bzw. Herstelldatum [ ] Barcode  Inhalt: [ ] Erbe‐Artikel Nr. + [ ] Lot‐ bzw. SN + Sonstiges: FB_0526_Verpackungsvorschrift deutsch Basiert auf Dokumentvorlage OID: 1501230, Version: 10 Version: Seite: 2 2/3 Hauptfilterkassette IES 3 Projektname Projektnummer ÄM‐Nummer ‐ Dokumentklasse Dokumentnummer Verpackungsvorschrift D163142 Version: 000 [ ] weitere Verpackungsebenen: 4. Einzelartikel Kennzeichnung des Einzelartikel mit Label: [X] Ja [ ] Nein Labelinhalt: [X] Erbe‐Artikel Nr. [X] Bezeichnung [X] Menge [X] Lot‐ bzw. SN [X] Mindesthaltbarkeitsdatum bzw. Herstelldatum [X] Barcode  Inhalt: [X] Erbe‐Artikel Nr. + [X] Lot‐ bzw. SN + Sonstiges: Vermerke und Zusätze zu den Transport‐, Lieferbedingungen: FB_0526_Verpackungsvorschrift deutsch Basiert auf Dokumentvorlage OID: 1501230, Version: 10 Version: Seite: 2 3/3
