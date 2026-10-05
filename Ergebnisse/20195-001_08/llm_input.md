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

1 2 3 4 A Außen Karton: E-Welle einseitig außen weiß, Stärke ca. 1,4mm Label (Etikett) rechtsseitig zentriert aufgeklebt 1 X Erbesiegel: Verpackung Art. Nr. 989101, 989102, 989103 B C Innen Schaumstoff: zweiteilig PU-Schaum anthrazit 2 x Erbesiegel: Verpackung Art. Nr. 989104 Nur gültig für REF: 78 XX XX SGE (Premium Pinzetten): Trockenmittelbeutel staubdicht: 85x40x8mm, Art. Nr. TMB1-6 (Lieferant Ratioform) PE-Kammernbeutel, transparent: 60x360x0,07mm, Artikelnummer L44603606 (Lieferant Papke) D Zu verwendende Verpackung gemäß Anlage 001: Art. Nr. 989101 (klein), Außenmaß ca. 160x65x26, Innenmaß ca. 145x60x24, 1 x Erbesiegel (82003-110) mittig Art. Nr. 989102 (mittel), Außenmaß ca. 250x65x26, Innenmaß ca. 235x60x24, 1x Erbesiegel (82003 -110) mittig Art. Nr. 989103 (groß), Außenmaß ca. 295x65x26, Innenmaß ca. 280x60x24, 1 x Erbesiegel (82003-110) mittig Art. Nr. 989104 (übergroß), Außenmaß ca. 365x65x26, Innenmaß ca. 350x60x24, 2 x Erbesiegel (82003-110) (Innenmaße ohne Schaumstoff) auf 1/3 und 2/3 der Verpackungslänge Stapelung der Verwendungshinweise (Blockstapelung) bei 6 Verwendungshinweisen E Stapelung der Verwendungshinweise (Blockstapelung) bei 5 Verwendungshinweisen Stapelung der Verwendungshinweise (Blockstapelung) bei 4 Verwendungshinweisen F Weitergabe sowie Vervielfältigung dieses Verwertung und Mitteilung seines Inhalts oder Geschmacksmustereintragung soweit nicht ausdrücklich gestattet. Zuwiderhandlungen verpflichten Allle Rechte für den Fall der Patent-, Gebrauchsmuster zu Schadenersatz. sind verboten, vorbehalten. Dokuments, Verantwortliche Abt.: Technische Referenz: Erstellt durch: Genehmigt von: Dokumentenstatus: Weitkamp Weitkamp freigegeben VW Dichmann Dokumentenart: Titel, zusätzl. Titel: Pinzettenverpackung und Labelplatzierung (Zeichnung nur für die Fa. Erbe) 8.100 35 Artikelzeichnung Änd.: D D PE-Schaum in PU korrigiert 24.09.20 dw Toleranz: Ausgabedatum: Ersterstellung am: DIN ISO 2768-f 24.09.2020 26.02.2015 Werkstoff: Maßstab - Größe: ohne - A4 (gilt nur für Original) siehe oben Oberfläche: siehe oben C A B Aktualisierung des Textes um Trocken- mittelbeutel und PE-Kammernbeutel 14.08.15 Erbesiegel und Hinweise zur Anbringung hinzugefügt Hinweise zur Stapelung der GAWs hinzugefügt 24.10.18 28.06.18 mag mag td Datei: Zeichnung_Label _Kartonverpackung_1_ERBE Art.Nr.: s. oben Mat.Nr.: Blatt: 1/1 Spr.: de Änd. Änderung Datum Name
