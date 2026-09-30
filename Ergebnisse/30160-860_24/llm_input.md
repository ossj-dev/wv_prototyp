# LLM-Eingabe

## Systemprompt

Du bist ein präziser Daten-Extraktions-Assistent für Etiketten und Verpackungsvorschriften. Extrahiere spezifische Informationen in ein striktes JSON-Schema.

Eingabeformat: Strukturierte Liste mit ganzzahligen räumlichen Koordinaten:
{"text": "...", "bbox": [x_links, y_oben, x_rechts, y_unten]}

LAYOUT LESEN:
- Ähnliche `y_oben`/`y_unten` (Abweichung < 5) = Zeile (nebeneinander).
- `x_links` = Spaltenposition (Key steht meist links vom Wert).
- Checkboxen (`[X]`/`[ ]`): Nutze `bbox`, um zu prüfen, welcher Text in derselben Zeile daneben steht.

REGELN & AUFGABE:
1. Analysiere Dokumente räumlich. Extrahiere AUSSCHLIESSLICH Verpackungsebenen und deren Label-Inhalte. Ignoriere andere Prüfmerkmale.
2. Mehrere Dokumente: Beginnen mit `=== DOKUMENT: ... ===`. Analysiere unabhängig, führe in ein JSON zusammen, vermeide Duplikate. Werte aus Beispielen nicht übernehmen.
3. Sprache: Verwende exakt die im Original erkannte Sprache.
4. Felder statt Werte: Bei Beispiel-Labels (z.B. "Art.Nr: 40402") das Datenfeld (z.B. "Artikelnummer") extrahieren, nicht den starren Wert.
5. Fehlende Daten: Nicht vorhandene Ebenen-Infos ignorieren.

SZENARIO A (Verpackungsvorschrift):
- Prüfe Struktur via Y-Koordinaten (von oben nach unten).
- Nur übernehmen, wenn bei der Ebene "Ja" angekreuzt ist (`[X] Ja`). Bei `[ ] Ja` oder "Nein" ignorieren. `label_inhalt` aus räumlich zugeordneten Texten/Checkboxen entnehmen.

SZENARIO B (Beispiel-Label):
- Kein Vorschriftstext/Checkboxen, sondern fertiges Etikett.
- `verpackungsebene` = "Beispiel-Label" (außer spezifische Ebene erkennbar).
- `label_inhalt` = Alle relevanten Prüffelder (Barcode, Artikel-Nr, Lot, Menge, Datum etc.).

OUTPUT-FORMAT:
Antworte AUSSCHLIESSLICH mit einem validen JSON-Objekt. Kein Begleittext, kein Markdown (kein ```json). Schema:
{
  "dokumentensprache": "...",
  "artikelnummer": "...",
  "labels": [
    {
      "verpackungsebene": "...",
      "label_inhalt": ["...", "..."]
    }
  ]
}

BEISPIELE ZUR ORIENTIERUNG:
Nutze die Werte aus den Beispielen NICHT für das finale Dokument.

<Beispiel 1>
Eingabedaten: 
[
  {
    "file": "D199226_DE_000.pdf",
    "page": 1,
    "elements": [
      {"text": "Projektname Projektnummer ÄM-Nummer", "bbox": [20, 40, 57, 47]},
      {"text": "LAP tubing set IES 3 without valve", "bbox": [20, 53, 116, 60]},
      {"text": "6521600", "bbox": [145, 53, 169, 60]},
      {"text": "-", "bbox": [261, 53, 263, 60]},
      {"text": "Dokumentklasse Dokumentnummer", "bbox": [20, 64, 68, 71]},
      {"text": "Verpackungsvorschrift D199226 Version: 000", "bbox": [20, 77, 84, 84]},
      {"text": "Verpackungsvorschrift deutsch", "bbox": [62, 115, 267, 131]},
      {"text": "Die Verpackungsvorschrift ist anzuwenden für:", "bbox": [62, 161, 285, 172]},
      {"text": "Erbe-Artikel Nr.:", "bbox": [62, 175, 135, 186]},
      {"text": "Bezeichnung:", "bbox": [62, 188, 122, 199]},
      {"text": "20323-011", "bbox": [169, 175, 217, 186]},
      {"text": "LAP Schlauchset IES 3 ohne Ventil 5m", "bbox": [169, 188, 335, 199]},
      {"text": "Abbildung der Verpackung (nicht zwingend erforderlich):", "bbox": [62, 336, 334, 347]}
    ]
  },
  {
    "file": "D199226_DE_000.pdf",
    "page": 2,
    "elements": [
      {"text": "Anlieferbedingungen:", "bbox": [62, 114, 166, 126]},
      {"text": "[X]", "bbox": [311, 142, 322, 153]},
      {"text": "[ ]", "bbox": [351, 142, 362, 153]},
      {"text": "Anlieferung auf Palette zwingend erforderlich:", "bbox": [62, 143, 302, 155]},
      {"text": "Ja", "bbox": [326, 143, 335, 154]},
      {"text": "Nein", "bbox": [366, 143, 387, 154]},
      {"text": "Verpackungsebene 0:", "bbox": [98, 367, 201, 379]},
      {"text": "[X]", "bbox": [347, 478, 358, 489]},
      {"text": "Kennzeichnung der Verpackungsebene 0 mit Label:", "bbox": [97, 479, 325, 490]},
      {"text": "Ja", "bbox": [361, 479, 370, 490]},
      {"text": "[X]", "bbox": [163, 504, 174, 516]},
      {"text": "Labelinhalt: Erbe-Artikel Nr. Bezeichnung Menge", "bbox": [97, 506, 393, 517]}
    ]
  }
]

Erwarteter JSON-Output:
{
  "dokumentensprache": "Deutsch",
  "artikelnummer": "20323-011",
  "labels": [
    {
      "verpackungsebene": "Verpackungsebene 0",
      "label_inhalt": [
        "Erbe-Artikel Nr.",
        "Bezeichnung",
        "Menge",
        "Lot- bzw. SN",
        "Mindesthaltbarkeitsdatum bzw. Herstelldatum",
        "Barcode"
      ]
    },
    {
      "verpackungsebene": "Verpackungsebene 1",
      "label_inhalt": [
        "Erbe-Artikel Nr.",
        "Bezeichnung",
        "Menge",
        "Lot- bzw. SN",
        "Mindesthaltbarkeitsdatum bzw. Herstelldatum",
        "Barcode"
      ]
    },
    {
      "verpackungsebene": "Einzelartikel",
      "label_inhalt": [
        "Erbe-Artikel Nr.",
        "Bezeichnung",
        "Menge",
        "Lot- bzw. SN",
        "Mindesthaltbarkeitsdatum bzw. Herstelldatum",
        "Barcode"
      ]
    }
  ]
}
</Beispiel 1>

<Beispiel 2>
Eingabedaten:
=== DOKUMENT: 800020459.pdf ===
[
  {
    "file": "800020459.pdf",
    "page": 1,
    "elements": [
      {"text": "HSW ULTRA-JANET QUICK-LOCK, 150 ML", "bbox": [253, 256, 563, 273]},
      {"text": "REF", "bbox": [30, 375, 79, 394]},
      {"text": "8300065309", "bbox": [70, 373, 193, 394]},
      {"text": "Erbe Art.Nr.: 20862-089", "bbox": [28, 405, 243, 423]},
      {"text": "LOT 1234567", "bbox": [31, 432, 157, 452]},
      {"text": "QTY 1", "bbox": [33, 462, 85, 479]}
    ]
  }
]

Erwarteter JSON-Output:
{
  "dokumentensprache": "Deutsch",
  "artikelnummer": "20862-089",
  "labels": [
    {
      "verpackungsebene": "Beispiel-Label",
      "label_inhalt": [
        "REF",
        "Erbe-Art.Nr.",
        "Lot",
        "Menge",
        "Barcode"
      ]
    }
  ]
}
</Beispiel 2>

## Benutzereingabe

[
  {
    "file": "D108713_DE_001.pdf",
    "page": 1,
    "elements": [
      {
        "text": "REF-Nr.ERBE",
        "bbox": [
          81,
          57,
          142,
          68
        ]
      },
      {
        "text": " Etikettenwerkstoff.PolyesterfoliemitAcrylatkleber",
        "bbox": [
          75,
          380,
          342,
          395
        ]
      },
      {
        "text": " BeiPlatzmangelkanndasLabelgeteiltwerden",
        "bbox": [
          75,
          410,
          318,
          425
        ]
      },
      {
        "text": " LabelgrößekannvomZuliefererbestimmtwerden",
        "bbox": [
          75,
          440,
          337,
          455
        ]
      },
      {
        "text": " Mindestschriftgröße2mm",
        "bbox": [
          75,
          470,
          220,
          485
        ]
      },
      {
        "text": " DasSymbolREFkannauchnuralsTextdargestelltwerden",
        "bbox": [
          75,
          500,
          376,
          515
        ]
      },
      {
        "text": " DieLOT-NummerundderStatusistentsprechenddemArbeitsauftrageinzutragen",
        "bbox": [
          75,
          530,
          493,
          545
        ]
      },
      {
        "text": " DemZuliefererwirdfreigestelltdenDatamatrixcodemiteineralphanumerischenTrennung zwischen REF-Nr. und LOT (z.B. 12345-678OP123456) oder ohne Trennung (z.B. 12345-678123456) auszuführen",
        "bbox": [
          75,
          560,
          574,
          604
        ]
      },
      {
        "text": " MindestgrößeDatamatrixcode6x6mm",
        "bbox": [
          75,
          619,
          289,
          634
        ]
      },
      {
        "text": "| Alle mit * gekennzeichneten Zeichnungsobjekte haben . | Alle mit * gekennzeichneten Zeichnungsobjekte haben . | Alle mit * gekennzeichneten Zeichnungsobjekte haben . | sich gegenüber der . | sich gegenüber der . | Vorgängerversion . 2:1 . | Vorgängerversion . 2:1 . | geändert! | |---------------------------------------------------------|---------------------------------------------------------|---------------------------------------------------------|------------------------|------------------------|----------------------------|----------------------------|----------------| | Werkstoff, Bezeichnung, Lieferant | Werkstoff, Bezeichnung, Lieferant | Werkstoff, Bezeichnung, Lieferant | Werkstoff-Nr. | Werkstoff-Nr. | Volumencm³ Maßstab | Volumencm³ Maßstab | geändert! | | Status | ERBE-Nr. | ÄM-Nr. | | Datum | Name Titel: | | | | Gültig | 30135-804 | 20023 | Bearb. | 07.06.2016 | UWED Labellayout | Chargenpflicht | Chargenpflicht | | | | | Gepr. | 07.06.2016 | LAURAS 2D-Code | | | | Dokumentklasse | Dokumentklasse | | | | Dokumentnummer: | Version: | Größe: | | Produktkennzeichnung | Produktkennzeichnung | | | | | | | | Oberflächenbeschaffenheit nach ISO 1302 | Oberflächenbeschaffenheit nach ISO 1302 | | | | D108713 | 001 | | | Maße ohne Toleranzangabe ISO 2768 - mH | Maße ohne Toleranzangabe ISO 2768 - mH | | Elektromedizin GmbH | Elektromedizin GmbH | | | | | | | | Urspr.: | Urspr.: | Ers.für: | Blatt: | 1 / 1 |",
        "bbox": [
          55,
          663,
          581,
          801
        ]
      }
    ]
  },
  {
    "file": "D230936_007_Assembly.pdf",
    "page": 1,
    "elements": [
      {
        "text": "1",
        "bbox": [
          4,
          112,
          10,
          121
        ]
      },
      {
        "text": "1",
        "bbox": [
          1180,
          112,
          1186,
          121
        ]
      },
      {
        "text": "2",
        "bbox": [
          4,
          315,
          10,
          324
        ]
      },
      {
        "text": "2",
        "bbox": [
          1180,
          315,
          1186,
          324
        ]
      },
      {
        "text": "3",
        "bbox": [
          4,
          519,
          10,
          528
        ]
      },
      {
        "text": "3",
        "bbox": [
          1180,
          519,
          1186,
          528
        ]
      },
      {
        "text": "4",
        "bbox": [
          4,
          722,
          10,
          731
        ]
      },
      {
        "text": "4",
        "bbox": [
          1180,
          722,
          1186,
          731
        ]
      },
      {
        "text": "A",
        "bbox": [
          156,
          3,
          163,
          12
        ]
      },
      {
        "text": "A",
        "bbox": [
          156,
          831,
          163,
          840
        ]
      },
      {
        "text": "Realistic View",
        "bbox": [
          173,
          40,
          238,
          49
        ]
      },
      {
        "text": "B",
        "bbox": [
          447,
          3,
          453,
          12
        ]
      },
      {
        "text": "B",
        "bbox": [
          447,
          831,
          453,
          840
        ]
      },
      {
        "text": "C",
        "bbox": [
          737,
          3,
          744,
          12
        ]
      },
      {
        "text": "Status",
        "bbox": [
          696,
          747,
          717,
          753
        ]
      },
      {
        "text": "Document type",
        "bbox": [
          696,
          775,
          747,
          782
        ]
      },
      {
        "text": "Drawing",
        "bbox": [
          696,
          786,
          729,
          794
        ]
      },
      {
        "text": "No part of this document may be reproduced or transmitted in any form or by",
        "bbox": [
          696,
          801,
          849,
          805
        ]
      },
      {
        "text": "any means, electronic or mechanical, including photocopying, recording or",
        "bbox": [
          696,
          807,
          844,
          811
        ]
      },
      {
        "text": "otherwise, without prior written permission. Any infringement shall give rise",
        "bbox": [
          696,
          812,
          845,
          816
        ]
      },
      {
        "text": "to an obligation to pay damages. All rights reserved in the event of patent,",
        "bbox": [
          696,
          817,
          843,
          821
        ]
      },
      {
        "text": "utility model or design registration.",
        "bbox": [
          696,
          822,
          764,
          826
        ]
      },
      {
        "text": "C",
        "bbox": [
          737,
          831,
          744,
          840
        ]
      },
      {
        "text": "Created Date Name",
        "bbox": [
          852,
          761,
          879,
          767
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887,
          761,
          925,
          767
        ]
      },
      {
        "text": "T. Ripplinger",
        "bbox": [
          930,
          761,
          972,
          767
        ]
      },
      {
        "text": "Checked",
        "bbox": [
          852,
          775,
          882,
          782
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887,
          775,
          925,
          782
        ]
      },
      {
        "text": "D.Sauter",
        "bbox": [
          930,
          775,
          960,
          781
        ]
      },
      {
        "text": "Elektromedizin GmbH",
        "bbox": [
          871,
          817,
          958,
          825
        ]
      },
      {
        "text": "Project",
        "bbox": [
          980,
          747,
          1003,
          753
        ]
      },
      {
        "text": "PB HW",
        "bbox": [
          980,
          760,
          1009,
          768
        ]
      },
      {
        "text": "Title",
        "bbox": [
          980,
          775,
          994,
          782
        ]
      },
      {
        "text": "Assembly Drawing",
        "bbox": [
          980,
          789,
          1054,
          797
        ]
      },
      {
        "text": "Schematic Revision",
        "bbox": [
          979,
          803,
          1045,
          810
        ]
      },
      {
        "text": "004",
        "bbox": [
          1063,
          803,
          1076,
          810
        ]
      },
      {
        "text": "Layout Revision EENr Assy EENr PCB",
        "bbox": [
          979,
          818,
          1033,
          824
        ]
      },
      {
        "text": "30160-860 40160-860",
        "bbox": [
          1095,
          761,
          1173,
          767
        ]
      },
      {
        "text": "Size",
        "bbox": [
          1136,
          775,
          1150,
          782
        ]
      },
      {
        "text": "A3",
        "bbox": [
          1150,
          789,
          1161,
          797
        ]
      },
      {
        "text": "Sheet",
        "bbox": [
          1136,
          803,
          1155,
          810
        ]
      },
      {
        "text": "04.04.2023",
        "bbox": [
          1063,
          818,
          1101,
          824
        ]
      },
      {
        "text": "1 of 7",
        "bbox": [
          1146,
          818,
          1165,
          824
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027,
          831,
          1035,
          840
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027,
          3,
          1035,
          12
        ]
      }
    ]
  },
  {
    "file": "D230936_007_Assembly.pdf",
    "page": 2,
    "elements": [
      {
        "text": "1",
        "bbox": [
          4,
          112,
          10,
          121
        ]
      },
      {
        "text": "1",
        "bbox": [
          1180,
          112,
          1186,
          121
        ]
      },
      {
        "text": "2",
        "bbox": [
          4,
          315,
          10,
          324
        ]
      },
      {
        "text": "2",
        "bbox": [
          1180,
          315,
          1186,
          324
        ]
      },
      {
        "text": "3",
        "bbox": [
          4,
          519,
          10,
          528
        ]
      },
      {
        "text": "3",
        "bbox": [
          1180,
          519,
          1186,
          528
        ]
      },
      {
        "text": "4",
        "bbox": [
          4,
          722,
          10,
          731
        ]
      },
      {
        "text": "4",
        "bbox": [
          1180,
          722,
          1186,
          731
        ]
      },
      {
        "text": "A",
        "bbox": [
          156,
          3,
          163,
          12
        ]
      },
      {
        "text": "A",
        "bbox": [
          156,
          831,
          163,
          840
        ]
      },
      {
        "text": "View from Top side (Scale 1:1)",
        "bbox": [
          184,
          17,
          327,
          27
        ]
      },
      {
        "text": "B",
        "bbox": [
          447,
          3,
          453,
          12
        ]
      },
      {
        "text": "B",
        "bbox": [
          447,
          831,
          453,
          840
        ]
      },
      {
        "text": "C",
        "bbox": [
          737,
          3,
          744,
          12
        ]
      },
      {
        "text": "Status",
        "bbox": [
          696,
          747,
          717,
          753
        ]
      },
      {
        "text": "Document type",
        "bbox": [
          696,
          775,
          747,
          782
        ]
      },
      {
        "text": "Drawing",
        "bbox": [
          696,
          786,
          729,
          794
        ]
      },
      {
        "text": "No part of this document may be reproduced or transmitted in any form or by",
        "bbox": [
          696,
          801,
          849,
          805
        ]
      },
      {
        "text": "any means, electronic or mechanical, including photocopying, recording or",
        "bbox": [
          696,
          807,
          844,
          811
        ]
      },
      {
        "text": "otherwise, without prior written permission. Any infringement shall give rise",
        "bbox": [
          696,
          812,
          845,
          816
        ]
      },
      {
        "text": "to an obligation to pay damages. All rights reserved in the event of patent,",
        "bbox": [
          696,
          817,
          843,
          821
        ]
      },
      {
        "text": "utility model or design registration.",
        "bbox": [
          696,
          822,
          764,
          826
        ]
      },
      {
        "text": "C",
        "bbox": [
          737,
          831,
          744,
          840
        ]
      },
      {
        "text": "Created Date Name",
        "bbox": [
          852,
          761,
          879,
          767
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887,
          761,
          925,
          767
        ]
      },
      {
        "text": "T. Ripplinger",
        "bbox": [
          930,
          761,
          972,
          767
        ]
      },
      {
        "text": "Checked",
        "bbox": [
          852,
          775,
          882,
          782
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887,
          775,
          925,
          782
        ]
      },
      {
        "text": "D.Sauter",
        "bbox": [
          930,
          775,
          960,
          781
        ]
      },
      {
        "text": "Elektromedizin GmbH",
        "bbox": [
          871,
          817,
          958,
          825
        ]
      },
      {
        "text": "Project",
        "bbox": [
          980,
          747,
          1003,
          753
        ]
      },
      {
        "text": "PB HW",
        "bbox": [
          980,
          760,
          1009,
          768
        ]
      },
      {
        "text": "Title",
        "bbox": [
          980,
          775,
          994,
          782
        ]
      },
      {
        "text": "Assembly Drawing",
        "bbox": [
          980,
          789,
          1054,
          797
        ]
      },
      {
        "text": "Schematic Revision",
        "bbox": [
          979,
          803,
          1045,
          810
        ]
      },
      {
        "text": "004",
        "bbox": [
          1063,
          803,
          1076,
          810
        ]
      },
      {
        "text": "Layout Revision EENr Assy EENr PCB",
        "bbox": [
          979,
          818,
          1033,
          824
        ]
      },
      {
        "text": "30160-860 40160-860",
        "bbox": [
          1095,
          761,
          1173,
          767
        ]
      },
      {
        "text": "Size",
        "bbox": [
          1136,
          775,
          1150,
          782
        ]
      },
      {
        "text": "A3",
        "bbox": [
          1150,
          789,
          1161,
          797
        ]
      },
      {
        "text": "Sheet",
        "bbox": [
          1136,
          803,
          1155,
          810
        ]
      },
      {
        "text": "04.04.2023",
        "bbox": [
          1063,
          818,
          1101,
          824
        ]
      },
      {
        "text": "2 of 7",
        "bbox": [
          1146,
          818,
          1165,
          824
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027,
          831,
          1035,
          840
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027,
          3,
          1035,
          12
        ]
      }
    ]
  },
  {
    "file": "D230936_007_Assembly.pdf",
    "page": 3,
    "elements": [
      {
        "text": "1",
        "bbox": [
          4,
          112,
          10,
          121
        ]
      },
      {
        "text": "1",
        "bbox": [
          1180,
          112,
          1186,
          121
        ]
      },
      {
        "text": "2",
        "bbox": [
          4,
          315,
          10,
          324
        ]
      },
      {
        "text": "2",
        "bbox": [
          1180,
          315,
          1186,
          324
        ]
      },
      {
        "text": "3",
        "bbox": [
          4,
          519,
          10,
          528
        ]
      },
      {
        "text": "3",
        "bbox": [
          1180,
          519,
          1186,
          528
        ]
      },
      {
        "text": "4",
        "bbox": [
          4,
          722,
          10,
          731
        ]
      },
      {
        "text": "4",
        "bbox": [
          1180,
          722,
          1186,
          731
        ]
      },
      {
        "text": "A",
        "bbox": [
          156,
          3,
          163,
          12
        ]
      },
      {
        "text": "A",
        "bbox": [
          156,
          831,
          163,
          840
        ]
      },
      {
        "text": "Realistic View Bottom",
        "bbox": [
          244,
          54,
          345,
          63
        ]
      },
      {
        "text": "B",
        "bbox": [
          447,
          3,
          453,
          12
        ]
      },
      {
        "text": "B",
        "bbox": [
          447,
          831,
          453,
          840
        ]
      },
      {
        "text": "C",
        "bbox": [
          737,
          3,
          744,
          12
        ]
      },
      {
        "text": "Vorzugsrichtung Wellenlötung auf der LS",
        "bbox": [
          533,
          39,
          798,
          51
        ]
      },
      {
        "text": "Status",
        "bbox": [
          696,
          747,
          717,
          753
        ]
      },
      {
        "text": "Document type",
        "bbox": [
          696,
          775,
          747,
          782
        ]
      },
      {
        "text": "Drawing",
        "bbox": [
          696,
          786,
          729,
          794
        ]
      },
      {
        "text": "No part of this document may be reproduced or transmitted in any form or by",
        "bbox": [
          696,
          801,
          849,
          805
        ]
      },
      {
        "text": "any means, electronic or mechanical, including photocopying, recording or",
        "bbox": [
          696,
          807,
          844,
          811
        ]
      },
      {
        "text": "otherwise, without prior written permission. Any infringement shall give rise",
        "bbox": [
          696,
          812,
          845,
          816
        ]
      },
      {
        "text": "to an obligation to pay damages. All rights reserved in the event of patent,",
        "bbox": [
          696,
          817,
          843,
          821
        ]
      },
      {
        "text": "utility model or design registration.",
        "bbox": [
          696,
          822,
          764,
          826
        ]
      },
      {
        "text": "C",
        "bbox": [
          737,
          831,
          744,
          840
        ]
      },
      {
        "text": "Created Date Name",
        "bbox": [
          852,
          761,
          879,
          767
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887,
          761,
          925,
          767
        ]
      },
      {
        "text": "T. Ripplinger",
        "bbox": [
          930,
          761,
          972,
          767
        ]
      },
      {
        "text": "Checked",
        "bbox": [
          852,
          775,
          882,
          782
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887,
          775,
          925,
          782
        ]
      },
      {
        "text": "D.Sauter",
        "bbox": [
          930,
          775,
          960,
          781
        ]
      },
      {
        "text": "Elektromedizin GmbH",
        "bbox": [
          871,
          817,
          958,
          825
        ]
      },
      {
        "text": "Project",
        "bbox": [
          980,
          747,
          1003,
          753
        ]
      },
      {
        "text": "PB HW",
        "bbox": [
          980,
          760,
          1009,
          768
        ]
      },
      {
        "text": "Title",
        "bbox": [
          980,
          775,
          994,
          782
        ]
      },
      {
        "text": "Assembly Drawing",
        "bbox": [
          980,
          789,
          1054,
          797
        ]
      },
      {
        "text": "Schematic Revision",
        "bbox": [
          979,
          803,
          1045,
          810
        ]
      },
      {
        "text": "004",
        "bbox": [
          1063,
          803,
          1076,
          810
        ]
      },
      {
        "text": "Layout Revision EENr Assy EENr PCB",
        "bbox": [
          979,
          818,
          1033,
          824
        ]
      },
      {
        "text": "30160-860 40160-860",
        "bbox": [
          1095,
          761,
          1173,
          767
        ]
      },
      {
        "text": "Size",
        "bbox": [
          1136,
          775,
          1150,
          782
        ]
      },
      {
        "text": "A3",
        "bbox": [
          1150,
          789,
          1161,
          797
        ]
      },
      {
        "text": "Sheet",
        "bbox": [
          1136,
          803,
          1155,
          810
        ]
      },
      {
        "text": "04.04.2023",
        "bbox": [
          1063,
          818,
          1101,
          824
        ]
      },
      {
        "text": "3 of 7",
        "bbox": [
          1146,
          818,
          1165,
          824
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027,
          831,
          1035,
          840
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027,
          3,
          1035,
          12
        ]
      }
    ]
  },
  {
    "file": "D230936_007_Assembly.pdf",
    "page": 4,
    "elements": [
      {
        "text": "1",
        "bbox": [
          4,
          112,
          10,
          121
        ]
      },
      {
        "text": "1",
        "bbox": [
          1180,
          112,
          1186,
          121
        ]
      },
      {
        "text": "2",
        "bbox": [
          4,
          315,
          10,
          324
        ]
      },
      {
        "text": "2",
        "bbox": [
          1180,
          315,
          1186,
          324
        ]
      },
      {
        "text": "3",
        "bbox": [
          4,
          519,
          10,
          528
        ]
      },
      {
        "text": "3",
        "bbox": [
          1180,
          519,
          1186,
          528
        ]
      },
      {
        "text": "4",
        "bbox": [
          4,
          722,
          10,
          731
        ]
      },
      {
        "text": "4",
        "bbox": [
          1180,
          722,
          1186,
          731
        ]
      },
      {
        "text": "A",
        "bbox": [
          156,
          3,
          163,
          12
        ]
      },
      {
        "text": "A",
        "bbox": [
          156,
          831,
          163,
          840
        ]
      },
      {
        "text": "View from Bottom side (Scale 2:3)",
        "bbox": [
          271,
          78,
          430,
          87
        ]
      },
      {
        "text": "B",
        "bbox": [
          447,
          3,
          453,
          12
        ]
      },
      {
        "text": "B",
        "bbox": [
          447,
          831,
          453,
          840
        ]
      },
      {
        "text": "C",
        "bbox": [
          737,
          3,
          744,
          12
        ]
      },
      {
        "text": "Status",
        "bbox": [
          696,
          747,
          717,
          753
        ]
      },
      {
        "text": "Document type",
        "bbox": [
          696,
          775,
          747,
          782
        ]
      },
      {
        "text": "Drawing",
        "bbox": [
          696,
          786,
          729,
          794
        ]
      },
      {
        "text": "No part of this document may be reproduced or transmitted in any form or by",
        "bbox": [
          696,
          801,
          849,
          805
        ]
      },
      {
        "text": "any means, electronic or mechanical, including photocopying, recording or",
        "bbox": [
          696,
          807,
          844,
          811
        ]
      },
      {
        "text": "otherwise, without prior written permission. Any infringement shall give rise",
        "bbox": [
          696,
          812,
          845,
          816
        ]
      },
      {
        "text": "to an obligation to pay damages. All rights reserved in the event of patent,",
        "bbox": [
          696,
          817,
          843,
          821
        ]
      },
      {
        "text": "utility model or design registration.",
        "bbox": [
          696,
          822,
          764,
          826
        ]
      },
      {
        "text": "C",
        "bbox": [
          737,
          831,
          744,
          840
        ]
      },
      {
        "text": "Created Date Name",
        "bbox": [
          852,
          761,
          879,
          767
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887,
          761,
          925,
          767
        ]
      },
      {
        "text": "T. Ripplinger",
        "bbox": [
          930,
          761,
          972,
          767
        ]
      },
      {
        "text": "Checked",
        "bbox": [
          852,
          775,
          882,
          782
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887,
          775,
          925,
          782
        ]
      },
      {
        "text": "D.Sauter",
        "bbox": [
          930,
          775,
          960,
          781
        ]
      },
      {
        "text": "Elektromedizin GmbH",
        "bbox": [
          871,
          817,
          958,
          825
        ]
      },
      {
        "text": "Project",
        "bbox": [
          980,
          747,
          1003,
          753
        ]
      },
      {
        "text": "PB HW",
        "bbox": [
          980,
          760,
          1009,
          768
        ]
      },
      {
        "text": "Title",
        "bbox": [
          980,
          775,
          994,
          782
        ]
      },
      {
        "text": "Assembly Drawing",
        "bbox": [
          980,
          789,
          1054,
          797
        ]
      },
      {
        "text": "Schematic Revision",
        "bbox": [
          979,
          803,
          1045,
          810
        ]
      },
      {
        "text": "004",
        "bbox": [
          1063,
          803,
          1076,
          810
        ]
      },
      {
        "text": "Layout Revision EENr Assy EENr PCB",
        "bbox": [
          979,
          818,
          1033,
          824
        ]
      },
      {
        "text": "30160-860 40160-860",
        "bbox": [
          1095,
          761,
          1173,
          767
        ]
      },
      {
        "text": "Size",
        "bbox": [
          1136,
          775,
          1150,
          782
        ]
      },
      {
        "text": "A3",
        "bbox": [
          1150,
          789,
          1161,
          797
        ]
      },
      {
        "text": "Sheet",
        "bbox": [
          1136,
          803,
          1155,
          810
        ]
      },
      {
        "text": "04.04.2023",
        "bbox": [
          1063,
          818,
          1101,
          824
        ]
      },
      {
        "text": "4 of 7",
        "bbox": [
          1146,
          818,
          1165,
          824
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027,
          831,
          1035,
          840
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027,
          3,
          1035,
          12
        ]
      }
    ]
  },
  {
    "file": "D230936_007_Assembly.pdf",
    "page": 5,
    "elements": [
      {
        "text": "[X]",
        "bbox": [
          314,
          104,
          325,
          116
        ]
      },
      {
        "text": "1",
        "bbox": [
          4,
          112,
          10,
          121
        ]
      },
      {
        "text": "1",
        "bbox": [
          1180,
          112,
          1186,
          121
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          644,
          185,
          653,
          193
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          702,
          243,
          710,
          251
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          114,
          284,
          129,
          299
        ]
      },
      {
        "text": "2",
        "bbox": [
          4,
          315,
          10,
          324
        ]
      },
      {
        "text": "2",
        "bbox": [
          1180,
          315,
          1186,
          324
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          564,
          492,
          579,
          507
        ]
      },
      {
        "text": "3",
        "bbox": [
          4,
          519,
          10,
          528
        ]
      },
      {
        "text": "3",
        "bbox": [
          1180,
          519,
          1186,
          528
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          657,
          666,
          677,
          691
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          635,
          666,
          660,
          691
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          639,
          666,
          664,
          691
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          642,
          666,
          667,
          691
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          646,
          666,
          671,
          691
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          649,
          666,
          674,
          691
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          653,
          666,
          678,
          691
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          660,
          666,
          685,
          691
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          663,
          666,
          688,
          691
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          667,
          666,
          692,
          691
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          671,
          666,
          695,
          691
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          674,
          666,
          699,
          691
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          388,
          700,
          400,
          711
        ]
      },
      {
        "text": "4",
        "bbox": [
          4,
          722,
          10,
          731
        ]
      },
      {
        "text": "4",
        "bbox": [
          1180,
          722,
          1186,
          731
        ]
      },
      {
        "text": "L301",
        "bbox": [
          146,
          378,
          154,
          398
        ]
      },
      {
        "text": "K300",
        "bbox": [
          137,
          475,
          158,
          483
        ]
      },
      {
        "text": "C318",
        "bbox": [
          133,
          508,
          154,
          516
        ]
      },
      {
        "text": "L300",
        "bbox": [
          136,
          552,
          155,
          560
        ]
      },
      {
        "text": "C317",
        "bbox": [
          133,
          598,
          154,
          606
        ]
      },
      {
        "text": "J301",
        "bbox": [
          130,
          644,
          149,
          652
        ]
      },
      {
        "text": "SW300",
        "bbox": [
          141,
          715,
          149,
          744
        ]
      },
      {
        "text": "SW300",
        "bbox": [
          141,
          715,
          149,
          744
        ]
      },
      {
        "text": "A",
        "bbox": [
          156,
          3,
          163,
          12
        ]
      },
      {
        "text": "View from Top side (Scale 1:1)",
        "bbox": [
          105,
          86,
          248,
          95
        ]
      },
      {
        "text": "Designator11",
        "bbox": [
          144,
          242,
          148,
          265
        ]
      },
      {
        "text": "C301",
        "bbox": [
          204,
          277,
          225,
          285
        ]
      },
      {
        "text": "C302",
        "bbox": [
          204,
          331,
          225,
          339
        ]
      },
      {
        "text": "J300",
        "bbox": [
          219,
          514,
          227,
          534
        ]
      },
      {
        "text": "J1000",
        "bbox": [
          223,
          700,
          231,
          724
        ]
      },
      {
        "text": "A",
        "bbox": [
          156,
          831,
          163,
          840
        ]
      },
      {
        "text": "RV300",
        "bbox": [
          182,
          644,
          190,
          671
        ]
      },
      {
        "text": "R318",
        "bbox": [
          194,
          544,
          202,
          566
        ]
      },
      {
        "text": "J1103",
        "bbox": [
          273,
          258,
          281,
          282
        ]
      },
      {
        "text": "C404",
        "bbox": [
          287,
          406,
          309,
          418
        ]
      },
      {
        "text": "HS403",
        "bbox": [
          315,
          440,
          342,
          448
        ]
      },
      {
        "text": "D401",
        "bbox": [
          333,
          433,
          341,
          454
        ]
      },
      {
        "text": "J1500",
        "bbox": [
          355,
          257,
          363,
          281
        ]
      },
      {
        "text": "HS400",
        "bbox": [
          361,
          440,
          388,
          448
        ]
      },
      {
        "text": "D402",
        "bbox": [
          379,
          433,
          387,
          454
        ]
      },
      {
        "text": "HS402 HS401",
        "bbox": [
          315,
          487,
          388,
          495
        ]
      },
      {
        "text": "D405",
        "bbox": [
          333,
          480,
          341,
          501
        ]
      },
      {
        "text": "D403",
        "bbox": [
          379,
          480,
          387,
          501
        ]
      },
      {
        "text": "T400",
        "bbox": [
          349,
          586,
          357,
          606
        ]
      },
      {
        "text": "L402",
        "bbox": [
          313,
          689,
          332,
          696
        ]
      },
      {
        "text": "R401",
        "bbox": [
          398,
          446,
          406,
          467
        ]
      },
      {
        "text": "R400",
        "bbox": [
          401,
          584,
          409,
          605
        ]
      },
      {
        "text": "L1201",
        "bbox": [
          410,
          124,
          435,
          132
        ]
      },
      {
        "text": "JP1203",
        "bbox": [
          412,
          121,
          415,
          134
        ]
      },
      {
        "text": "JP1202",
        "bbox": [
          427,
          121,
          430,
          134
        ]
      },
      {
        "text": "JP1201",
        "bbox": [
          416,
          121,
          419,
          134
        ]
      },
      {
        "text": "JP1200",
        "bbox": [
          431,
          121,
          434,
          134
        ]
      },
      {
        "text": "C1204",
        "bbox": [
          421,
          203,
          429,
          229
        ]
      },
      {
        "text": "B",
        "bbox": [
          447,
          3,
          453,
          12
        ]
      },
      {
        "text": "C401",
        "bbox": [
          451,
          342,
          472,
          350
        ]
      },
      {
        "text": "L403",
        "bbox": [
          446,
          405,
          466,
          413
        ]
      },
      {
        "text": "L404",
        "bbox": [
          430,
          487,
          438,
          507
        ]
      },
      {
        "text": "L400",
        "bbox": [
          493,
          487,
          501,
          507
        ]
      },
      {
        "text": "C206",
        "bbox": [
          449,
          617,
          464,
          639
        ]
      },
      {
        "text": "C206",
        "bbox": [
          449,
          617,
          464,
          639
        ]
      },
      {
        "text": "B",
        "bbox": [
          447,
          831,
          453,
          840
        ]
      },
      {
        "text": "Q200",
        "bbox": [
          471,
          660,
          487,
          683
        ]
      },
      {
        "text": "R1301",
        "bbox": [
          520,
          376,
          531,
          403
        ]
      },
      {
        "text": "C200",
        "bbox": [
          517,
          575,
          540,
          590
        ]
      },
      {
        "text": "C200",
        "bbox": [
          517,
          575,
          540,
          590
        ]
      },
      {
        "text": "T1200",
        "bbox": [
          542,
          195,
          550,
          220
        ]
      },
      {
        "text": "T200",
        "bbox": [
          545,
          639,
          566,
          654
        ]
      },
      {
        "text": "T200",
        "bbox": [
          545,
          639,
          566,
          654
        ]
      },
      {
        "text": "K1204",
        "bbox": [
          567,
          333,
          577,
          359
        ]
      },
      {
        "text": "K1203",
        "bbox": [
          604,
          337,
          614,
          363
        ]
      },
      {
        "text": "K1202",
        "bbox": [
          641,
          342,
          651,
          368
        ]
      },
      {
        "text": "C1201",
        "bbox": [
          666,
          120,
          693,
          138
        ]
      },
      {
        "text": "L1200",
        "bbox": [
          674,
          206,
          682,
          230
        ]
      },
      {
        "text": "K1205",
        "bbox": [
          677,
          355,
          687,
          381
        ]
      },
      {
        "text": "C216",
        "bbox": [
          647,
          553,
          662,
          576
        ]
      },
      {
        "text": "C215 C214",
        "bbox": [
          625,
          590,
          685,
          623
        ]
      },
      {
        "text": "J1104",
        "bbox": [
          663,
          667,
          671,
          691
        ]
      },
      {
        "text": "L203",
        "bbox": [
          700,
          548,
          715,
          569
        ]
      },
      {
        "text": "J1102",
        "bbox": [
          690,
          676,
          714,
          684
        ]
      },
      {
        "text": "C",
        "bbox": [
          737,
          3,
          744,
          12
        ]
      },
      {
        "text": "R1200",
        "bbox": [
          738,
          121,
          764,
          140
        ]
      },
      {
        "text": "R1201",
        "bbox": [
          735,
          171,
          761,
          191
        ]
      },
      {
        "text": "C1203",
        "bbox": [
          737,
          244,
          744,
          270
        ]
      },
      {
        "text": "C1200",
        "bbox": [
          769,
          244,
          776,
          270
        ]
      },
      {
        "text": "C1202",
        "bbox": [
          735,
          305,
          761,
          312
        ]
      },
      {
        "text": "K1201",
        "bbox": [
          760,
          357,
          770,
          383
        ]
      },
      {
        "text": "C213",
        "bbox": [
          739,
          539,
          762,
          554
        ]
      },
      {
        "text": "J1101",
        "bbox": [
          759,
          659,
          767,
          683
        ]
      },
      {
        "text": "Status",
        "bbox": [
          696,
          747,
          717,
          753
        ]
      },
      {
        "text": "Document type",
        "bbox": [
          696,
          775,
          747,
          782
        ]
      },
      {
        "text": "Drawing",
        "bbox": [
          696,
          786,
          729,
          794
        ]
      },
      {
        "text": "No part of this document may be reproduced or transmitted in any form or by",
        "bbox": [
          696,
          801,
          849,
          805
        ]
      },
      {
        "text": "any means, electronic or mechanical, including photocopying, recording or",
        "bbox": [
          696,
          807,
          844,
          811
        ]
      },
      {
        "text": "otherwise, without prior written permission. Any infringement shall give rise",
        "bbox": [
          696,
          812,
          845,
          816
        ]
      },
      {
        "text": "to an obligation to pay damages. All rights reserved in the event of patent,",
        "bbox": [
          696,
          817,
          843,
          821
        ]
      },
      {
        "text": "utility model or design registration.",
        "bbox": [
          696,
          822,
          764,
          826
        ]
      },
      {
        "text": "C",
        "bbox": [
          737,
          831,
          744,
          840
        ]
      },
      {
        "text": "K1200",
        "bbox": [
          722,
          353,
          733,
          379
        ]
      },
      {
        "text": "J1600",
        "bbox": [
          803,
          133,
          810,
          157
        ]
      },
      {
        "text": "J1601",
        "bbox": [
          803,
          139,
          810,
          163
        ]
      },
      {
        "text": "J1401",
        "bbox": [
          803,
          227,
          811,
          251
        ]
      },
      {
        "text": "J1400",
        "bbox": [
          803,
          475,
          810,
          499
        ]
      },
      {
        "text": "J1100",
        "bbox": [
          808,
          622,
          815,
          646
        ]
      },
      {
        "text": "Created",
        "bbox": [
          852,
          761,
          879,
          767
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027,
          3,
          1035,
          12
        ]
      },
      {
        "text": "Footprint J1100 für",
        "bbox": [
          919,
          566,
          1107,
          585
        ]
      },
      {
        "text": "Einpressbauteil in der",
        "bbox": [
          919,
          591,
          1135,
          611
        ]
      },
      {
        "text": "Montagelinie!",
        "bbox": [
          919,
          617,
          1052,
          637
        ]
      },
      {
        "text": "Pins beim Wellenlöten",
        "bbox": [
          919,
          643,
          1141,
          663
        ]
      },
      {
        "text": "abdecken!",
        "bbox": [
          919,
          669,
          1022,
          689
        ]
      },
      {
        "text": "Date Name Project",
        "bbox": [
          887,
          747,
          903,
          753
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887,
          761,
          925,
          767
        ]
      },
      {
        "text": "T. Ripplinger",
        "bbox": [
          930,
          761,
          972,
          767
        ]
      },
      {
        "text": "Checked",
        "bbox": [
          852,
          775,
          882,
          782
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887,
          775,
          925,
          782
        ]
      },
      {
        "text": "D.Sauter",
        "bbox": [
          930,
          775,
          960,
          781
        ]
      },
      {
        "text": "Elektromedizin GmbH",
        "bbox": [
          871,
          817,
          958,
          825
        ]
      },
      {
        "text": "PB HW",
        "bbox": [
          980,
          760,
          1009,
          768
        ]
      },
      {
        "text": "Title",
        "bbox": [
          980,
          775,
          994,
          782
        ]
      },
      {
        "text": "Assembly Drawing",
        "bbox": [
          980,
          789,
          1054,
          797
        ]
      },
      {
        "text": "Schematic Revision",
        "bbox": [
          979,
          803,
          1045,
          810
        ]
      },
      {
        "text": "004",
        "bbox": [
          1063,
          803,
          1076,
          810
        ]
      },
      {
        "text": "Layout Revision EENr Assy EENr PCB",
        "bbox": [
          979,
          818,
          1033,
          824
        ]
      },
      {
        "text": "30160-860 40160-860",
        "bbox": [
          1095,
          761,
          1173,
          767
        ]
      },
      {
        "text": "Size",
        "bbox": [
          1136,
          775,
          1150,
          782
        ]
      },
      {
        "text": "A3",
        "bbox": [
          1150,
          789,
          1161,
          797
        ]
      },
      {
        "text": "Sheet",
        "bbox": [
          1136,
          803,
          1155,
          810
        ]
      },
      {
        "text": "04.04.2023",
        "bbox": [
          1063,
          818,
          1101,
          824
        ]
      },
      {
        "text": "5 of 7",
        "bbox": [
          1146,
          818,
          1165,
          824
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027,
          831,
          1035,
          840
        ]
      }
    ]
  },
  {
    "file": "D230936_007_Assembly.pdf",
    "page": 6,
    "elements": [
      {
        "text": "[X]",
        "bbox": [
          607,
          45,
          618,
          56
        ]
      },
      {
        "text": "1",
        "bbox": [
          4,
          112,
          10,
          121
        ]
      },
      {
        "text": "1",
        "bbox": [
          1180,
          112,
          1186,
          121
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          279,
          125,
          288,
          134
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          446,
          149,
          458,
          164
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          478,
          150,
          490,
          164
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          509,
          150,
          520,
          164
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          463,
          150,
          474,
          164
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          493,
          150,
          505,
          164
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          614,
          166,
          623,
          174
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          222,
          183,
          230,
          191
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          607,
          199,
          621,
          216
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          803,
          225,
          818,
          240
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          448,
          299,
          457,
          307
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          482,
          299,
          491,
          308
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          599,
          307,
          613,
          325
        ]
      },
      {
        "text": "2",
        "bbox": [
          4,
          315,
          10,
          324
        ]
      },
      {
        "text": "2",
        "bbox": [
          1180,
          315,
          1186,
          324
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          429,
          378,
          450,
          400
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          148,
          380,
          156,
          388
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          484,
          385,
          500,
          400
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          298,
          404,
          310,
          417
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          353,
          432,
          368,
          447
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          735,
          494,
          750,
          505
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          298,
          504,
          316,
          525
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          323,
          505,
          331,
          516
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          735,
          510,
          750,
          522
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          317,
          516,
          338,
          536
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          276,
          518,
          297,
          538
        ]
      },
      {
        "text": "3",
        "bbox": [
          4,
          519,
          10,
          528
        ]
      },
      {
        "text": "3",
        "bbox": [
          1180,
          519,
          1186,
          528
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          312,
          549,
          327,
          565
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          450,
          574,
          459,
          585
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          460,
          577,
          471,
          589
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          344,
          579,
          352,
          588
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          435,
          586,
          450,
          602
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          549,
          590,
          563,
          604
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          430,
          602,
          438,
          613
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          436,
          605,
          444,
          616
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          483,
          613,
          491,
          623
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          465,
          620,
          485,
          638
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          421,
          621,
          434,
          636
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          442,
          632,
          466,
          651
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          414,
          637,
          427,
          653
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          532,
          641,
          544,
          652
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          437,
          645,
          460,
          664
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          474,
          645,
          483,
          653
        ]
      },
      {
        "text": "4",
        "bbox": [
          4,
          722,
          10,
          731
        ]
      },
      {
        "text": "4",
        "bbox": [
          1180,
          722,
          1186,
          731
        ]
      },
      {
        "text": "C1100",
        "bbox": [
          117,
          519,
          128,
          522
        ]
      },
      {
        "text": "C1101",
        "bbox": [
          128,
          513,
          131,
          524
        ]
      },
      {
        "text": "R1100",
        "bbox": [
          117,
          526,
          121,
          537
        ]
      },
      {
        "text": "U1100",
        "bbox": [
          121,
          524,
          132,
          528
        ]
      },
      {
        "text": "C1104",
        "bbox": [
          128,
          528,
          131,
          539
        ]
      },
      {
        "text": "C1103",
        "bbox": [
          133,
          528,
          136,
          539
        ]
      },
      {
        "text": "R1101",
        "bbox": [
          121,
          528,
          125,
          539
        ]
      },
      {
        "text": "R1105",
        "bbox": [
          132,
          509,
          136,
          520
        ]
      },
      {
        "text": "C1102",
        "bbox": [
          132,
          518,
          136,
          529
        ]
      },
      {
        "text": "R1108R1104",
        "bbox": [
          136,
          510,
          140,
          529
        ]
      },
      {
        "text": "A",
        "bbox": [
          156,
          3,
          163,
          12
        ]
      },
      {
        "text": "View from Bottom side (Scale 1:1)",
        "bbox": [
          105,
          26,
          263,
          36
        ]
      },
      {
        "text": "R1107",
        "bbox": [
          141,
          352,
          152,
          356
        ]
      },
      {
        "text": "R1106",
        "bbox": [
          142,
          357,
          153,
          360
        ]
      },
      {
        "text": "R1103",
        "bbox": [
          142,
          361,
          153,
          365
        ]
      },
      {
        "text": "R1102",
        "bbox": [
          142,
          366,
          153,
          369
        ]
      },
      {
        "text": "R1210",
        "bbox": [
          244,
          359,
          255,
          362
        ]
      },
      {
        "text": "R908",
        "bbox": [
          248,
          396,
          251,
          405
        ]
      },
      {
        "text": "U1201",
        "bbox": [
          276,
          350,
          302,
          358
        ]
      },
      {
        "text": "R1211",
        "bbox": [
          259,
          367,
          270,
          370
        ]
      },
      {
        "text": "R1212",
        "bbox": [
          267,
          375,
          278,
          378
        ]
      },
      {
        "text": "C900",
        "bbox": [
          262,
          399,
          271,
          402
        ]
      },
      {
        "text": "R314",
        "bbox": [
          790,
          395,
          799,
          398
        ]
      },
      {
        "text": "R308",
        "bbox": [
          799,
          395,
          808,
          398
        ]
      },
      {
        "text": "C316",
        "bbox": [
          790,
          399,
          799,
          402
        ]
      },
      {
        "text": "R900",
        "bbox": [
          253,
          401,
          262,
          404
        ]
      },
      {
        "text": "R906",
        "bbox": [
          246,
          408,
          254,
          411
        ]
      },
      {
        "text": "R910",
        "bbox": [
          244,
          412,
          253,
          415
        ]
      },
      {
        "text": "C907",
        "bbox": [
          253,
          412,
          262,
          416
        ]
      },
      {
        "text": "C904",
        "bbox": [
          246,
          418,
          249,
          426
        ]
      },
      {
        "text": "C918",
        "bbox": [
          245,
          434,
          249,
          443
        ]
      },
      {
        "text": "U900",
        "bbox": [
          258,
          404,
          261,
          413
        ]
      },
      {
        "text": "R902",
        "bbox": [
          251,
          418,
          255,
          427
        ]
      },
      {
        "text": "C906",
        "bbox": [
          257,
          419,
          260,
          429
        ]
      },
      {
        "text": "U902",
        "bbox": [
          250,
          436,
          259,
          440
        ]
      },
      {
        "text": "R913",
        "bbox": [
          250,
          444,
          259,
          447
        ]
      },
      {
        "text": "R1214",
        "bbox": [
          294,
          372,
          297,
          384
        ]
      },
      {
        "text": "R1215",
        "bbox": [
          298,
          373,
          302,
          384
        ]
      },
      {
        "text": "R1213",
        "bbox": [
          289,
          373,
          293,
          384
        ]
      },
      {
        "text": "R912",
        "bbox": [
          273,
          396,
          276,
          405
        ]
      },
      {
        "text": "L900",
        "bbox": [
          265,
          404,
          269,
          412
        ]
      },
      {
        "text": "C908",
        "bbox": [
          264,
          414,
          273,
          418
        ]
      },
      {
        "text": "D900",
        "bbox": [
          275,
          406,
          278,
          415
        ]
      },
      {
        "text": "C909",
        "bbox": [
          264,
          421,
          273,
          424
        ]
      },
      {
        "text": "R904",
        "bbox": [
          264,
          428,
          272,
          431
        ]
      },
      {
        "text": "C917",
        "bbox": [
          260,
          435,
          264,
          444
        ]
      },
      {
        "text": "C913",
        "bbox": [
          280,
          396,
          284,
          405
        ]
      },
      {
        "text": "D901",
        "bbox": [
          281,
          406,
          284,
          415
        ]
      },
      {
        "text": "C914",
        "bbox": [
          291,
          399,
          295,
          408
        ]
      },
      {
        "text": "C905",
        "bbox": [
          281,
          420,
          290,
          423
        ]
      },
      {
        "text": "R903",
        "bbox": [
          281,
          425,
          290,
          428
        ]
      },
      {
        "text": "C902",
        "bbox": [
          280,
          430,
          290,
          434
        ]
      },
      {
        "text": "R905",
        "bbox": [
          273,
          436,
          282,
          439
        ]
      },
      {
        "text": "C910",
        "bbox": [
          267,
          443,
          276,
          447
        ]
      },
      {
        "text": "R914",
        "bbox": [
          298,
          399,
          307,
          402
        ]
      },
      {
        "text": "D902",
        "bbox": [
          286,
          397,
          290,
          406
        ]
      },
      {
        "text": "C915",
        "bbox": [
          293,
          408,
          296,
          417
        ]
      },
      {
        "text": "U903",
        "bbox": [
          302,
          404,
          307,
          417
        ]
      },
      {
        "text": "R911",
        "bbox": [
          292,
          419,
          296,
          428
        ]
      },
      {
        "text": "R909",
        "bbox": [
          302,
          422,
          311,
          425
        ]
      },
      {
        "text": "R907",
        "bbox": [
          296,
          420,
          300,
          429
        ]
      },
      {
        "text": "U901",
        "bbox": [
          295,
          432,
          304,
          436
        ]
      },
      {
        "text": "C903",
        "bbox": [
          292,
          428,
          296,
          437
        ]
      },
      {
        "text": "C911",
        "bbox": [
          290,
          437,
          293,
          446
        ]
      },
      {
        "text": "C912",
        "bbox": [
          284,
          437,
          287,
          447
        ]
      },
      {
        "text": "C212",
        "bbox": [
          269,
          518,
          279,
          524
        ]
      },
      {
        "text": "L202",
        "bbox": [
          278,
          522,
          295,
          534
        ]
      },
      {
        "text": "R901",
        "bbox": [
          304,
          427,
          307,
          436
        ]
      },
      {
        "text": "L901",
        "bbox": [
          296,
          440,
          304,
          443
        ]
      },
      {
        "text": "C901",
        "bbox": [
          306,
          436,
          309,
          445
        ]
      },
      {
        "text": "R223",
        "bbox": [
          308,
          494,
          315,
          503
        ]
      },
      {
        "text": "R222",
        "bbox": [
          313,
          496,
          320,
          506
        ]
      },
      {
        "text": "U203",
        "bbox": [
          301,
          506,
          314,
          524
        ]
      },
      {
        "text": "R211",
        "bbox": [
          304,
          528,
          314,
          534
        ]
      },
      {
        "text": "R207",
        "bbox": [
          329,
          510,
          335,
          519
        ]
      },
      {
        "text": "C220",
        "bbox": [
          317,
          505,
          324,
          515
        ]
      },
      {
        "text": "C210",
        "bbox": [
          324,
          505,
          331,
          515
        ]
      },
      {
        "text": "C217",
        "bbox": [
          311,
          520,
          317,
          529
        ]
      },
      {
        "text": "D206",
        "bbox": [
          303,
          533,
          313,
          539
        ]
      },
      {
        "text": "R212",
        "bbox": [
          312,
          531,
          319,
          540
        ]
      },
      {
        "text": "C211",
        "bbox": [
          297,
          530,
          304,
          540
        ]
      },
      {
        "text": "Q201",
        "bbox": [
          318,
          521,
          336,
          533
        ]
      },
      {
        "text": "D201",
        "bbox": [
          315,
          550,
          325,
          565
        ]
      },
      {
        "text": "Q300",
        "bbox": [
          790,
          406,
          799,
          409
        ]
      },
      {
        "text": "R306",
        "bbox": [
          799,
          405,
          808,
          409
        ]
      },
      {
        "text": "R305",
        "bbox": [
          799,
          409,
          808,
          413
        ]
      },
      {
        "text": "C307",
        "bbox": [
          794,
          415,
          803,
          418
        ]
      },
      {
        "text": "C309",
        "bbox": [
          794,
          421,
          803,
          425
        ]
      },
      {
        "text": "D302",
        "bbox": [
          807,
          414,
          810,
          423
        ]
      },
      {
        "text": "C308",
        "bbox": [
          794,
          428,
          803,
          431
        ]
      },
      {
        "text": "C312",
        "bbox": [
          806,
          423,
          810,
          432
        ]
      },
      {
        "text": "C322 C321",
        "bbox": [
          770,
          443,
          807,
          449
        ]
      },
      {
        "text": "L302",
        "bbox": [
          787,
          454,
          790,
          463
        ]
      },
      {
        "text": "R317 R316",
        "bbox": [
          773,
          527,
          801,
          530
        ]
      },
      {
        "text": "C319",
        "bbox": [
          770,
          542,
          786,
          548
        ]
      },
      {
        "text": "C320",
        "bbox": [
          790,
          542,
          806,
          548
        ]
      },
      {
        "text": "C1207",
        "bbox": [
          154,
          374,
          165,
          377
        ]
      },
      {
        "text": "Q1200",
        "bbox": [
          146,
          383,
          158,
          386
        ]
      },
      {
        "text": "R1203",
        "bbox": [
          143,
          378,
          146,
          389
        ]
      },
      {
        "text": "R1202",
        "bbox": [
          158,
          377,
          161,
          388
        ]
      },
      {
        "text": "C1205",
        "bbox": [
          146,
          392,
          157,
          395
        ]
      },
      {
        "text": "R1208",
        "bbox": [
          146,
          398,
          157,
          401
        ]
      },
      {
        "text": "C501",
        "bbox": [
          145,
          403,
          148,
          412
        ]
      },
      {
        "text": "R506",
        "bbox": [
          151,
          403,
          154,
          412
        ]
      },
      {
        "text": "C1002",
        "bbox": [
          159,
          388,
          162,
          399
        ]
      },
      {
        "text": "R504",
        "bbox": [
          155,
          403,
          159,
          412
        ]
      },
      {
        "text": "R319",
        "bbox": [
          146,
          452,
          149,
          461
        ]
      },
      {
        "text": "A",
        "bbox": [
          156,
          831,
          163,
          840
        ]
      },
      {
        "text": "L1100",
        "bbox": [
          167,
          571,
          178,
          575
        ]
      },
      {
        "text": "C1105",
        "bbox": [
          166,
          582,
          177,
          585
        ]
      },
      {
        "text": "C1107",
        "bbox": [
          219,
          602,
          230,
          606
        ]
      },
      {
        "text": "C1210",
        "bbox": [
          307,
          338,
          318,
          342
        ]
      },
      {
        "text": "C1211",
        "bbox": [
          307,
          344,
          318,
          347
        ]
      },
      {
        "text": "C202",
        "bbox": [
          344,
          569,
          350,
          579
        ]
      },
      {
        "text": "R1308",
        "bbox": [
          359,
          368,
          362,
          379
        ]
      },
      {
        "text": "Q1303",
        "bbox": [
          366,
          367,
          370,
          379
        ]
      },
      {
        "text": "R1304",
        "bbox": [
          374,
          353,
          378,
          364
        ]
      },
      {
        "text": "C1302",
        "bbox": [
          379,
          353,
          382,
          364
        ]
      },
      {
        "text": "Q1301",
        "bbox": [
          372,
          366,
          383,
          370
        ]
      },
      {
        "text": "R1306",
        "bbox": [
          373,
          374,
          384,
          377
        ]
      },
      {
        "text": "L200",
        "bbox": [
          359,
          496,
          369,
          502
        ]
      },
      {
        "text": "R202",
        "bbox": [
          348,
          571,
          358,
          577
        ]
      },
      {
        "text": "U201",
        "bbox": [
          344,
          579,
          351,
          589
        ]
      },
      {
        "text": "C203",
        "bbox": [
          354,
          579,
          364,
          586
        ]
      },
      {
        "text": "R205",
        "bbox": [
          346,
          575,
          356,
          581
        ]
      },
      {
        "text": "C201",
        "bbox": [
          351,
          583,
          358,
          592
        ]
      },
      {
        "text": "R203",
        "bbox": [
          355,
          584,
          362,
          594
        ]
      },
      {
        "text": "R200",
        "bbox": [
          366,
          582,
          376,
          588
        ]
      },
      {
        "text": "U200",
        "bbox": [
          371,
          592,
          393,
          607
        ]
      },
      {
        "text": "R204",
        "bbox": [
          396,
          602,
          403,
          611
        ]
      },
      {
        "text": "C204",
        "bbox": [
          400,
          603,
          406,
          613
        ]
      },
      {
        "text": "R201",
        "bbox": [
          362,
          587,
          368,
          597
        ]
      },
      {
        "text": "R1300",
        "bbox": [
          388,
          361,
          391,
          372
        ]
      },
      {
        "text": "Q1300",
        "bbox": [
          410,
          299,
          417,
          326
        ]
      },
      {
        "text": "C1301",
        "bbox": [
          407,
          329,
          418,
          332
        ]
      },
      {
        "text": "U1301",
        "bbox": [
          411,
          335,
          417,
          354
        ]
      },
      {
        "text": "R1303",
        "bbox": [
          398,
          328,
          408,
          338
        ]
      },
      {
        "text": "C1300",
        "bbox": [
          393,
          357,
          404,
          361
        ]
      },
      {
        "text": "U1300",
        "bbox": [
          391,
          366,
          402,
          369
        ]
      },
      {
        "text": "R1305",
        "bbox": [
          402,
          362,
          406,
          373
        ]
      },
      {
        "text": "R1302",
        "bbox": [
          411,
          357,
          422,
          361
        ]
      },
      {
        "text": "R1307",
        "bbox": [
          408,
          362,
          411,
          373
        ]
      },
      {
        "text": "Q1302",
        "bbox": [
          414,
          361,
          418,
          373
        ]
      },
      {
        "text": "R610",
        "bbox": [
          438,
          290,
          441,
          299
        ]
      },
      {
        "text": "C601",
        "bbox": [
          438,
          302,
          441,
          311
        ]
      },
      {
        "text": "C603",
        "bbox": [
          448,
          288,
          457,
          291
        ]
      },
      {
        "text": "C604",
        "bbox": [
          449,
          293,
          458,
          296
        ]
      },
      {
        "text": "U601",
        "bbox": [
          451,
          299,
          454,
          307
        ]
      },
      {
        "text": "R603",
        "bbox": [
          442,
          290,
          446,
          299
        ]
      },
      {
        "text": "R606",
        "bbox": [
          443,
          301,
          446,
          309
        ]
      },
      {
        "text": "C608",
        "bbox": [
          447,
          312,
          450,
          321
        ]
      },
      {
        "text": "C1510",
        "bbox": [
          455,
          128,
          466,
          131
        ]
      },
      {
        "text": "C1513",
        "bbox": [
          455,
          138,
          466,
          141
        ]
      },
      {
        "text": "C1512",
        "bbox": [
          486,
          128,
          498,
          131
        ]
      },
      {
        "text": "C1511",
        "bbox": [
          518,
          128,
          529,
          131
        ]
      },
      {
        "text": "C1509",
        "bbox": [
          486,
          138,
          498,
          141
        ]
      },
      {
        "text": "C1508",
        "bbox": [
          518,
          140,
          529,
          143
        ]
      },
      {
        "text": "D1506",
        "bbox": [
          427,
          152,
          435,
          178
        ]
      },
      {
        "text": "D1500",
        "bbox": [
          532,
          154,
          540,
          180
        ]
      },
      {
        "text": "D1505",
        "bbox": [
          450,
          150,
          454,
          164
        ]
      },
      {
        "text": "D1503",
        "bbox": [
          482,
          150,
          486,
          164
        ]
      },
      {
        "text": "D1501",
        "bbox": [
          513,
          150,
          517,
          164
        ]
      },
      {
        "text": "D1504",
        "bbox": [
          467,
          150,
          471,
          164
        ]
      },
      {
        "text": "D1502",
        "bbox": [
          497,
          150,
          501,
          164
        ]
      },
      {
        "text": "C1504",
        "bbox": [
          472,
          175,
          483,
          179
        ]
      },
      {
        "text": "C1507",
        "bbox": [
          472,
          186,
          483,
          189
        ]
      },
      {
        "text": "C1506",
        "bbox": [
          503,
          176,
          514,
          179
        ]
      },
      {
        "text": "C1503",
        "bbox": [
          503,
          186,
          514,
          189
        ]
      },
      {
        "text": "R600",
        "bbox": [
          451,
          271,
          460,
          274
        ]
      },
      {
        "text": "R621 R619",
        "bbox": [
          459,
          282,
          464,
          301
        ]
      },
      {
        "text": "R617",
        "bbox": [
          459,
          302,
          462,
          310
        ]
      },
      {
        "text": "C612",
        "bbox": [
          452,
          311,
          455,
          320
        ]
      },
      {
        "text": "C614",
        "bbox": [
          457,
          311,
          461,
          320
        ]
      },
      {
        "text": "L401",
        "bbox": [
          431,
          382,
          447,
          398
        ]
      },
      {
        "text": "R206",
        "bbox": [
          444,
          570,
          453,
          582
        ]
      },
      {
        "text": "R607",
        "bbox": [
          498,
          274,
          506,
          277
        ]
      },
      {
        "text": "R602",
        "bbox": [
          475,
          271,
          483,
          274
        ]
      },
      {
        "text": "R618",
        "bbox": [
          466,
          282,
          469,
          291
        ]
      },
      {
        "text": "C600",
        "bbox": [
          476,
          288,
          485,
          291
        ]
      },
      {
        "text": "R604",
        "bbox": [
          476,
          293,
          485,
          296
        ]
      },
      {
        "text": "C607",
        "bbox": [
          469,
          296,
          478,
          300
        ]
      },
      {
        "text": "R611",
        "bbox": [
          498,
          283,
          506,
          286
        ]
      },
      {
        "text": "R614",
        "bbox": [
          464,
          290,
          467,
          299
        ]
      },
      {
        "text": "C606",
        "bbox": [
          464,
          302,
          467,
          311
        ]
      },
      {
        "text": "C610",
        "bbox": [
          464,
          312,
          467,
          321
        ]
      },
      {
        "text": "C611",
        "bbox": [
          469,
          302,
          478,
          305
        ]
      },
      {
        "text": "R609",
        "bbox": [
          488,
          288,
          497,
          292
        ]
      },
      {
        "text": "R601",
        "bbox": [
          488,
          294,
          497,
          297
        ]
      },
      {
        "text": "U600",
        "bbox": [
          482,
          302,
          491,
          305
        ]
      },
      {
        "text": "C613",
        "bbox": [
          469,
          306,
          478,
          309
        ]
      },
      {
        "text": "R616",
        "bbox": [
          477,
          311,
          486,
          314
        ]
      },
      {
        "text": "C602",
        "bbox": [
          493,
          298,
          497,
          307
        ]
      },
      {
        "text": "R620",
        "bbox": [
          489,
          310,
          498,
          314
        ]
      },
      {
        "text": "U602",
        "bbox": [
          469,
          315,
          478,
          318
        ]
      },
      {
        "text": "C605",
        "bbox": [
          477,
          315,
          486,
          318
        ]
      },
      {
        "text": "C609",
        "bbox": [
          475,
          321,
          478,
          330
        ]
      },
      {
        "text": "C400",
        "bbox": [
          466,
          385,
          476,
          388
        ]
      },
      {
        "text": "C207",
        "bbox": [
          451,
          574,
          458,
          585
        ]
      },
      {
        "text": "D200",
        "bbox": [
          438,
          587,
          448,
          602
        ]
      },
      {
        "text": "C209",
        "bbox": [
          431,
          602,
          438,
          613
        ]
      },
      {
        "text": "R218",
        "bbox": [
          432,
          626,
          439,
          635
        ]
      },
      {
        "text": "C208",
        "bbox": [
          437,
          605,
          444,
          615
        ]
      },
      {
        "text": "D205",
        "bbox": [
          423,
          621,
          433,
          636
        ]
      },
      {
        "text": "D203",
        "bbox": [
          416,
          638,
          426,
          653
        ]
      },
      {
        "text": "C205",
        "bbox": [
          462,
          578,
          469,
          588
        ]
      },
      {
        "text": "R209",
        "bbox": [
          467,
          606,
          477,
          613
        ]
      },
      {
        "text": "C218",
        "bbox": [
          462,
          615,
          468,
          625
        ]
      },
      {
        "text": "D208",
        "bbox": [
          436,
          631,
          443,
          641
        ]
      },
      {
        "text": "R217",
        "bbox": [
          424,
          645,
          430,
          654
        ]
      },
      {
        "text": "R208",
        "bbox": [
          465,
          610,
          475,
          617
        ]
      },
      {
        "text": "C219",
        "bbox": [
          458,
          624,
          465,
          633
        ]
      },
      {
        "text": "D207",
        "bbox": [
          432,
          642,
          438,
          652
        ]
      },
      {
        "text": "C222",
        "bbox": [
          443,
          634,
          465,
          649
        ]
      },
      {
        "text": "C221",
        "bbox": [
          437,
          647,
          459,
          662
        ]
      },
      {
        "text": "B",
        "bbox": [
          447,
          831,
          453,
          840
        ]
      },
      {
        "text": "D202",
        "bbox": [
          474,
          611,
          480,
          621
        ]
      },
      {
        "text": "C402",
        "bbox": [
          515,
          532,
          524,
          536
        ]
      },
      {
        "text": "R214",
        "bbox": [
          506,
          592,
          512,
          601
        ]
      },
      {
        "text": "C226",
        "bbox": [
          479,
          610,
          486,
          620
        ]
      },
      {
        "text": "U202",
        "bbox": [
          466,
          623,
          483,
          635
        ]
      },
      {
        "text": "R224",
        "bbox": [
          484,
          614,
          491,
          623
        ]
      },
      {
        "text": "C224",
        "bbox": [
          486,
          624,
          493,
          633
        ]
      },
      {
        "text": "C225",
        "bbox": [
          490,
          625,
          497,
          635
        ]
      },
      {
        "text": "R221",
        "bbox": [
          487,
          635,
          497,
          642
        ]
      },
      {
        "text": "C223",
        "bbox": [
          482,
          633,
          489,
          643
        ]
      },
      {
        "text": "D204",
        "bbox": [
          473,
          646,
          483,
          652
        ]
      },
      {
        "text": "R210",
        "bbox": [
          466,
          650,
          475,
          657
        ]
      },
      {
        "text": "R225",
        "bbox": [
          485,
          640,
          495,
          646
        ]
      },
      {
        "text": "R213",
        "bbox": [
          514,
          595,
          520,
          604
        ]
      },
      {
        "text": "R220 R216",
        "bbox": [
          499,
          607,
          510,
          628
        ]
      },
      {
        "text": "R219 R215",
        "bbox": [
          505,
          610,
          518,
          635
        ]
      },
      {
        "text": "NT600",
        "bbox": [
          499,
          289,
          511,
          293
        ]
      },
      {
        "text": "R605",
        "bbox": [
          498,
          294,
          507,
          297
        ]
      },
      {
        "text": "R608",
        "bbox": [
          498,
          299,
          507,
          302
        ]
      },
      {
        "text": "R612",
        "bbox": [
          498,
          304,
          507,
          308
        ]
      },
      {
        "text": "R615",
        "bbox": [
          498,
          309,
          507,
          312
        ]
      },
      {
        "text": "R402",
        "bbox": [
          510,
          296,
          517,
          313
        ]
      },
      {
        "text": "R613",
        "bbox": [
          489,
          315,
          498,
          318
        ]
      },
      {
        "text": "L405",
        "bbox": [
          484,
          390,
          500,
          396
        ]
      },
      {
        "text": "B",
        "bbox": [
          447,
          3,
          453,
          12
        ]
      },
      {
        "text": "C403",
        "bbox": [
          531,
          442,
          535,
          452
        ]
      },
      {
        "text": "C1500",
        "bbox": [
          539,
          229,
          550,
          232
        ]
      },
      {
        "text": "C1502",
        "bbox": [
          539,
          238,
          550,
          241
        ]
      },
      {
        "text": "C1505",
        "bbox": [
          539,
          247,
          550,
          250
        ]
      },
      {
        "text": "C1501",
        "bbox": [
          539,
          256,
          550,
          259
        ]
      },
      {
        "text": "C1206",
        "bbox": [
          549,
          318,
          553,
          329
        ]
      },
      {
        "text": "C916",
        "bbox": [
          539,
          346,
          542,
          355
        ]
      },
      {
        "text": "L201",
        "bbox": [
          549,
          595,
          563,
          600
        ]
      },
      {
        "text": "C700",
        "bbox": [
          593,
          157,
          602,
          160
        ]
      },
      {
        "text": "R704 R702",
        "bbox": [
          600,
          161,
          603,
          180
        ]
      },
      {
        "text": "C703",
        "bbox": [
          593,
          181,
          602,
          185
        ]
      },
      {
        "text": "C705",
        "bbox": [
          594,
          190,
          597,
          199
        ]
      },
      {
        "text": "R707",
        "bbox": [
          599,
          188,
          602,
          197
        ]
      },
      {
        "text": "R706",
        "bbox": [
          604,
          188,
          607,
          197
        ]
      },
      {
        "text": "U702",
        "bbox": [
          592,
          203,
          601,
          207
        ]
      },
      {
        "text": "C702 C701",
        "bbox": [
          606,
          161,
          609,
          180
        ]
      },
      {
        "text": "C710",
        "bbox": [
          610,
          165,
          614,
          174
        ]
      },
      {
        "text": "U700",
        "bbox": [
          617,
          166,
          621,
          175
        ]
      },
      {
        "text": "C704",
        "bbox": [
          615,
          178,
          624,
          181
        ]
      },
      {
        "text": "C709",
        "bbox": [
          605,
          184,
          614,
          188
        ]
      },
      {
        "text": "R705",
        "bbox": [
          608,
          188,
          612,
          197
        ]
      },
      {
        "text": "R700",
        "bbox": [
          622,
          188,
          625,
          197
        ]
      },
      {
        "text": "C708",
        "bbox": [
          602,
          199,
          606,
          208
        ]
      },
      {
        "text": "C802",
        "bbox": [
          594,
          212,
          603,
          215
        ]
      },
      {
        "text": "R801",
        "bbox": [
          595,
          216,
          604,
          219
        ]
      },
      {
        "text": "R703",
        "bbox": [
          613,
          188,
          616,
          197
        ]
      },
      {
        "text": "R701",
        "bbox": [
          618,
          188,
          621,
          197
        ]
      },
      {
        "text": "U701",
        "bbox": [
          611,
          200,
          617,
          216
        ]
      },
      {
        "text": "R1206",
        "bbox": [
          594,
          261,
          598,
          272
        ]
      },
      {
        "text": "C1209",
        "bbox": [
          602,
          258,
          613,
          261
        ]
      },
      {
        "text": "U1200",
        "bbox": [
          605,
          261,
          609,
          272
        ]
      },
      {
        "text": "C1208",
        "bbox": [
          593,
          272,
          604,
          275
        ]
      },
      {
        "text": "R1205",
        "bbox": [
          602,
          272,
          614,
          275
        ]
      },
      {
        "text": "R1209",
        "bbox": [
          593,
          277,
          604,
          281
        ]
      },
      {
        "text": "R802",
        "bbox": [
          598,
          284,
          602,
          293
        ]
      },
      {
        "text": "R800",
        "bbox": [
          593,
          295,
          596,
          304
        ]
      },
      {
        "text": "C800",
        "bbox": [
          597,
          295,
          600,
          304
        ]
      },
      {
        "text": "R1207",
        "bbox": [
          604,
          276,
          607,
          287
        ]
      },
      {
        "text": "R1204",
        "bbox": [
          610,
          276,
          613,
          287
        ]
      },
      {
        "text": "C801",
        "bbox": [
          604,
          292,
          608,
          302
        ]
      },
      {
        "text": "R804",
        "bbox": [
          611,
          292,
          614,
          301
        ]
      },
      {
        "text": "U800",
        "bbox": [
          603,
          307,
          610,
          325
        ]
      },
      {
        "text": "R803",
        "bbox": [
          600,
          329,
          609,
          332
        ]
      },
      {
        "text": "C707 C706",
        "bbox": [
          622,
          197,
          625,
          216
        ]
      },
      {
        "text": "C1106",
        "bbox": [
          628,
          197,
          639,
          201
        ]
      },
      {
        "text": "D1100",
        "bbox": [
          628,
          203,
          639,
          206
        ]
      },
      {
        "text": "Q1100",
        "bbox": [
          625,
          211,
          636,
          214
        ]
      },
      {
        "text": "R1110",
        "bbox": [
          632,
          220,
          635,
          231
        ]
      },
      {
        "text": "R1109",
        "bbox": [
          632,
          230,
          635,
          241
        ]
      },
      {
        "text": "C502",
        "bbox": [
          619,
          257,
          623,
          267
        ]
      },
      {
        "text": "R505",
        "bbox": [
          626,
          256,
          629,
          265
        ]
      },
      {
        "text": "C500",
        "bbox": [
          620,
          268,
          624,
          277
        ]
      },
      {
        "text": "C305",
        "bbox": [
          619,
          280,
          628,
          284
        ]
      },
      {
        "text": "R304",
        "bbox": [
          619,
          286,
          627,
          289
        ]
      },
      {
        "text": "C300",
        "bbox": [
          619,
          291,
          628,
          294
        ]
      },
      {
        "text": "R315",
        "bbox": [
          619,
          297,
          627,
          300
        ]
      },
      {
        "text": "R313",
        "bbox": [
          619,
          305,
          627,
          308
        ]
      },
      {
        "text": "C315",
        "bbox": [
          619,
          310,
          628,
          313
        ]
      },
      {
        "text": "C311",
        "bbox": [
          619,
          315,
          628,
          319
        ]
      },
      {
        "text": "R1112",
        "bbox": [
          637,
          220,
          641,
          231
        ]
      },
      {
        "text": "R1111",
        "bbox": [
          637,
          230,
          641,
          241
        ]
      },
      {
        "text": "U501",
        "bbox": [
          632,
          268,
          653,
          276
        ]
      },
      {
        "text": "U301",
        "bbox": [
          634,
          283,
          655,
          291
        ]
      },
      {
        "text": "U305",
        "bbox": [
          634,
          296,
          655,
          304
        ]
      },
      {
        "text": "U304",
        "bbox": [
          634,
          309,
          655,
          317
        ]
      },
      {
        "text": "R502",
        "bbox": [
          665,
          266,
          674,
          269
        ]
      },
      {
        "text": "C503",
        "bbox": [
          666,
          270,
          670,
          279
        ]
      },
      {
        "text": "R501",
        "bbox": [
          671,
          271,
          674,
          280
        ]
      },
      {
        "text": "R300",
        "bbox": [
          660,
          284,
          669,
          288
        ]
      },
      {
        "text": "C304",
        "bbox": [
          664,
          295,
          667,
          304
        ]
      },
      {
        "text": "C303",
        "bbox": [
          680,
          294,
          684,
          303
        ]
      },
      {
        "text": "U300",
        "bbox": [
          669,
          297,
          677,
          301
        ]
      },
      {
        "text": "R307",
        "bbox": [
          661,
          307,
          664,
          316
        ]
      },
      {
        "text": "U303",
        "bbox": [
          665,
          307,
          674,
          310
        ]
      },
      {
        "text": "C314",
        "bbox": [
          675,
          306,
          684,
          310
        ]
      },
      {
        "text": "C306",
        "bbox": [
          665,
          313,
          674,
          316
        ]
      },
      {
        "text": "D303",
        "bbox": [
          656,
          318,
          659,
          327
        ]
      },
      {
        "text": "C313",
        "bbox": [
          660,
          318,
          663,
          327
        ]
      },
      {
        "text": "R311",
        "bbox": [
          664,
          318,
          667,
          327
        ]
      },
      {
        "text": "U302",
        "bbox": [
          669,
          316,
          673,
          325
        ]
      },
      {
        "text": "R310",
        "bbox": [
          659,
          328,
          668,
          331
        ]
      },
      {
        "text": "R309",
        "bbox": [
          659,
          331,
          668,
          335
        ]
      },
      {
        "text": "C310",
        "bbox": [
          656,
          327,
          659,
          336
        ]
      },
      {
        "text": "D404",
        "bbox": [
          651,
          510,
          672,
          517
        ]
      },
      {
        "text": "D400",
        "bbox": [
          644,
          537,
          665,
          545
        ]
      },
      {
        "text": "R312",
        "bbox": [
          674,
          311,
          683,
          314
        ]
      },
      {
        "text": "D304",
        "bbox": [
          674,
          314,
          683,
          323
        ]
      },
      {
        "text": "R303",
        "bbox": [
          683,
          432,
          686,
          441
        ]
      },
      {
        "text": "R302",
        "bbox": [
          683,
          449,
          686,
          458
        ]
      },
      {
        "text": "R301",
        "bbox": [
          683,
          465,
          686,
          474
        ]
      },
      {
        "text": "L1000",
        "bbox": [
          685,
          657,
          688,
          667
        ]
      },
      {
        "text": "C1001 C1000",
        "bbox": [
          685,
          647,
          688,
          677
        ]
      },
      {
        "text": "R500",
        "bbox": [
          676,
          259,
          685,
          262
        ]
      },
      {
        "text": "U500",
        "bbox": [
          675,
          267,
          684,
          270
        ]
      },
      {
        "text": "C504",
        "bbox": [
          675,
          275,
          683,
          279
        ]
      },
      {
        "text": "R503",
        "bbox": [
          674,
          280,
          683,
          283
        ]
      },
      {
        "text": "R508",
        "bbox": [
          685,
          258,
          689,
          267
        ]
      },
      {
        "text": "R507",
        "bbox": [
          685,
          266,
          689,
          275
        ]
      },
      {
        "text": "C",
        "bbox": [
          737,
          3,
          744,
          12
        ]
      },
      {
        "text": "D300",
        "bbox": [
          735,
          498,
          749,
          503
        ]
      },
      {
        "text": "D301",
        "bbox": [
          735,
          514,
          749,
          519
        ]
      },
      {
        "text": "Status",
        "bbox": [
          696,
          747,
          717,
          753
        ]
      },
      {
        "text": "Document type",
        "bbox": [
          696,
          775,
          747,
          782
        ]
      },
      {
        "text": "Drawing",
        "bbox": [
          696,
          786,
          729,
          794
        ]
      },
      {
        "text": "No part of this document may be reproduced or transmitted in any form or by",
        "bbox": [
          696,
          801,
          849,
          805
        ]
      },
      {
        "text": "any means, electronic or mechanical, including photocopying, recording or",
        "bbox": [
          696,
          807,
          844,
          811
        ]
      },
      {
        "text": "otherwise, without prior written permission. Any infringement shall give rise",
        "bbox": [
          696,
          812,
          845,
          816
        ]
      },
      {
        "text": "to an obligation to pay damages. All rights reserved in the event of patent,",
        "bbox": [
          696,
          817,
          843,
          821
        ]
      },
      {
        "text": "utility model or design registration.",
        "bbox": [
          696,
          822,
          764,
          826
        ]
      },
      {
        "text": "C",
        "bbox": [
          737,
          831,
          744,
          840
        ]
      },
      {
        "text": "Created Date Name",
        "bbox": [
          852,
          761,
          879,
          767
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887,
          761,
          925,
          767
        ]
      },
      {
        "text": "T. Ripplinger",
        "bbox": [
          930,
          761,
          972,
          767
        ]
      },
      {
        "text": "Checked",
        "bbox": [
          852,
          775,
          882,
          782
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887,
          775,
          925,
          782
        ]
      },
      {
        "text": "D.Sauter",
        "bbox": [
          930,
          775,
          960,
          781
        ]
      },
      {
        "text": "Elektromedizin GmbH",
        "bbox": [
          871,
          817,
          958,
          825
        ]
      },
      {
        "text": "Project",
        "bbox": [
          980,
          747,
          1003,
          753
        ]
      },
      {
        "text": "PB HW",
        "bbox": [
          980,
          760,
          1009,
          768
        ]
      },
      {
        "text": "Title",
        "bbox": [
          980,
          775,
          994,
          782
        ]
      },
      {
        "text": "Assembly Drawing",
        "bbox": [
          980,
          789,
          1054,
          797
        ]
      },
      {
        "text": "Schematic Revision",
        "bbox": [
          979,
          803,
          1045,
          810
        ]
      },
      {
        "text": "004",
        "bbox": [
          1063,
          803,
          1076,
          810
        ]
      },
      {
        "text": "Layout Revision EENr Assy EENr PCB",
        "bbox": [
          979,
          818,
          1033,
          824
        ]
      },
      {
        "text": "30160-860 40160-860",
        "bbox": [
          1095,
          761,
          1173,
          767
        ]
      },
      {
        "text": "Size",
        "bbox": [
          1136,
          775,
          1150,
          782
        ]
      },
      {
        "text": "A3",
        "bbox": [
          1150,
          789,
          1161,
          797
        ]
      },
      {
        "text": "Sheet",
        "bbox": [
          1136,
          803,
          1155,
          810
        ]
      },
      {
        "text": "04.04.2023",
        "bbox": [
          1063,
          818,
          1101,
          824
        ]
      },
      {
        "text": "6 of 7",
        "bbox": [
          1146,
          818,
          1165,
          824
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027,
          831,
          1035,
          840
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027,
          3,
          1035,
          12
        ]
      }
    ]
  },
  {
    "file": "D230936_007_Assembly.pdf",
    "page": 7,
    "elements": [
      {
        "text": "[X]",
        "bbox": [
          826,
          68,
          835,
          77
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          421,
          74,
          433,
          85
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          449,
          76,
          457,
          84
        ]
      },
      {
        "text": "1",
        "bbox": [
          4,
          112,
          10,
          121
        ]
      },
      {
        "text": "1",
        "bbox": [
          1180,
          112,
          1186,
          121
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          752,
          155,
          760,
          163
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          809,
          212,
          818,
          221
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          222,
          254,
          237,
          269
        ]
      },
      {
        "text": "2",
        "bbox": [
          4,
          315,
          10,
          324
        ]
      },
      {
        "text": "2",
        "bbox": [
          1180,
          315,
          1186,
          324
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          831,
          449,
          839,
          459
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          821,
          461,
          831,
          470
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          671,
          461,
          686,
          476
        ]
      },
      {
        "text": "3",
        "bbox": [
          4,
          519,
          10,
          528
        ]
      },
      {
        "text": "3",
        "bbox": [
          1180,
          519,
          1186,
          528
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          764,
          636,
          784,
          661
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          741,
          636,
          766,
          661
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          745,
          636,
          770,
          661
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          748,
          636,
          773,
          661
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          752,
          636,
          777,
          661
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          755,
          636,
          780,
          661
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          759,
          636,
          784,
          661
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          769,
          636,
          794,
          661
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          773,
          636,
          798,
          661
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          776,
          636,
          801,
          661
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          780,
          636,
          805,
          661
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          783,
          636,
          808,
          661
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          496,
          670,
          507,
          681
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          236,
          713,
          245,
          722
        ]
      },
      {
        "text": "4",
        "bbox": [
          4,
          722,
          10,
          731
        ]
      },
      {
        "text": "4",
        "bbox": [
          1180,
          722,
          1186,
          731
        ]
      },
      {
        "text": "A",
        "bbox": [
          156,
          3,
          163,
          12
        ]
      },
      {
        "text": "A",
        "bbox": [
          156,
          831,
          163,
          840
        ]
      },
      {
        "text": "Labeling Top side (Scale 1:1)",
        "bbox": [
          212,
          56,
          349,
          65
        ]
      },
      {
        "text": "Designator11",
        "bbox": [
          252,
          212,
          255,
          234
        ]
      },
      {
        "text": "C301",
        "bbox": [
          311,
          247,
          332,
          255
        ]
      },
      {
        "text": "C302",
        "bbox": [
          311,
          300,
          332,
          308
        ]
      },
      {
        "text": "J300",
        "bbox": [
          326,
          484,
          334,
          503
        ]
      },
      {
        "text": "J1000",
        "bbox": [
          330,
          669,
          338,
          693
        ]
      },
      {
        "text": "L301",
        "bbox": [
          254,
          348,
          261,
          368
        ]
      },
      {
        "text": "K300",
        "bbox": [
          245,
          445,
          265,
          453
        ]
      },
      {
        "text": "C318",
        "bbox": [
          240,
          477,
          261,
          485
        ]
      },
      {
        "text": "L300",
        "bbox": [
          243,
          522,
          263,
          530
        ]
      },
      {
        "text": "C317",
        "bbox": [
          241,
          568,
          262,
          575
        ]
      },
      {
        "text": "J301",
        "bbox": [
          237,
          614,
          256,
          622
        ]
      },
      {
        "text": "SW300",
        "bbox": [
          249,
          684,
          256,
          713
        ]
      },
      {
        "text": "SW300",
        "bbox": [
          249,
          684,
          256,
          713
        ]
      },
      {
        "text": "FID100",
        "bbox": [
          234,
          716,
          247,
          720
        ]
      },
      {
        "text": "RV300",
        "bbox": [
          290,
          613,
          297,
          640
        ]
      },
      {
        "text": "R318",
        "bbox": [
          301,
          514,
          309,
          535
        ]
      },
      {
        "text": "J1103",
        "bbox": [
          380,
          227,
          388,
          251
        ]
      },
      {
        "text": "C404",
        "bbox": [
          395,
          375,
          417,
          387
        ]
      },
      {
        "text": "B",
        "bbox": [
          447,
          3,
          453,
          12
        ]
      },
      {
        "text": "FID101",
        "bbox": [
          452,
          74,
          455,
          86
        ]
      },
      {
        "text": "HS403",
        "bbox": [
          422,
          410,
          449,
          417
        ]
      },
      {
        "text": "D401",
        "bbox": [
          441,
          402,
          448,
          424
        ]
      },
      {
        "text": "J1500",
        "bbox": [
          463,
          226,
          470,
          250
        ]
      },
      {
        "text": "HS400",
        "bbox": [
          469,
          410,
          495,
          418
        ]
      },
      {
        "text": "D402",
        "bbox": [
          487,
          403,
          494,
          424
        ]
      },
      {
        "text": "HS402 HS401",
        "bbox": [
          422,
          457,
          495,
          465
        ]
      },
      {
        "text": "D405",
        "bbox": [
          441,
          450,
          448,
          471
        ]
      },
      {
        "text": "D403",
        "bbox": [
          487,
          450,
          494,
          471
        ]
      },
      {
        "text": "T400",
        "bbox": [
          456,
          555,
          464,
          575
        ]
      },
      {
        "text": "L402",
        "bbox": [
          420,
          658,
          440,
          666
        ]
      },
      {
        "text": "B",
        "bbox": [
          447,
          831,
          453,
          840
        ]
      },
      {
        "text": "R401",
        "bbox": [
          505,
          416,
          513,
          437
        ]
      },
      {
        "text": "R400",
        "bbox": [
          508,
          554,
          516,
          575
        ]
      },
      {
        "text": "L1201",
        "bbox": [
          518,
          93,
          542,
          101
        ]
      },
      {
        "text": "JP1203",
        "bbox": [
          519,
          90,
          523,
          103
        ]
      },
      {
        "text": "JP1202",
        "bbox": [
          534,
          90,
          537,
          103
        ]
      },
      {
        "text": "JP1201",
        "bbox": [
          523,
          90,
          527,
          103
        ]
      },
      {
        "text": "JP1200",
        "bbox": [
          538,
          90,
          541,
          103
        ]
      },
      {
        "text": "C1204",
        "bbox": [
          528,
          173,
          536,
          199
        ]
      },
      {
        "text": "C401",
        "bbox": [
          558,
          311,
          579,
          319
        ]
      },
      {
        "text": "L403",
        "bbox": [
          554,
          374,
          573,
          382
        ]
      },
      {
        "text": "L404",
        "bbox": [
          538,
          457,
          545,
          476
        ]
      },
      {
        "text": "L400",
        "bbox": [
          601,
          457,
          609,
          476
        ]
      },
      {
        "text": "C206",
        "bbox": [
          556,
          587,
          571,
          609
        ]
      },
      {
        "text": "C206",
        "bbox": [
          556,
          587,
          571,
          609
        ]
      },
      {
        "text": "Q200",
        "bbox": [
          579,
          630,
          594,
          653
        ]
      },
      {
        "text": "R1301",
        "bbox": [
          628,
          346,
          638,
          373
        ]
      },
      {
        "text": "C200",
        "bbox": [
          625,
          544,
          647,
          559
        ]
      },
      {
        "text": "C200",
        "bbox": [
          625,
          544,
          647,
          559
        ]
      },
      {
        "text": "T1200",
        "bbox": [
          650,
          165,
          657,
          190
        ]
      },
      {
        "text": "T200",
        "bbox": [
          652,
          608,
          674,
          623
        ]
      },
      {
        "text": "T200",
        "bbox": [
          652,
          608,
          674,
          623
        ]
      },
      {
        "text": "K1204",
        "bbox": [
          674,
          302,
          685,
          328
        ]
      },
      {
        "text": "K1203",
        "bbox": [
          711,
          307,
          722,
          333
        ]
      },
      {
        "text": "C",
        "bbox": [
          737,
          3,
          744,
          12
        ]
      },
      {
        "text": "K1202",
        "bbox": [
          748,
          311,
          759,
          337
        ]
      },
      {
        "text": "C1201",
        "bbox": [
          773,
          90,
          800,
          108
        ]
      },
      {
        "text": "L1200",
        "bbox": [
          781,
          175,
          789,
          200
        ]
      },
      {
        "text": "K1205",
        "bbox": [
          784,
          325,
          795,
          351
        ]
      },
      {
        "text": "C216",
        "bbox": [
          755,
          523,
          770,
          545
        ]
      },
      {
        "text": "C215 C214",
        "bbox": [
          732,
          559,
          792,
          593
        ]
      },
      {
        "text": "J1104",
        "bbox": [
          771,
          636,
          779,
          660
        ]
      },
      {
        "text": "Status",
        "bbox": [
          696,
          747,
          717,
          753
        ]
      },
      {
        "text": "Document type",
        "bbox": [
          696,
          775,
          747,
          782
        ]
      },
      {
        "text": "Drawing",
        "bbox": [
          696,
          786,
          729,
          794
        ]
      },
      {
        "text": "No part of this document may be reproduced or transmitted in any form or by",
        "bbox": [
          696,
          801,
          849,
          805
        ]
      },
      {
        "text": "any means, electronic or mechanical, including photocopying, recording or",
        "bbox": [
          696,
          807,
          844,
          811
        ]
      },
      {
        "text": "otherwise, without prior written permission. Any infringement shall give rise",
        "bbox": [
          696,
          812,
          845,
          816
        ]
      },
      {
        "text": "to an obligation to pay damages. All rights reserved in the event of patent,",
        "bbox": [
          696,
          817,
          843,
          821
        ]
      },
      {
        "text": "utility model or design registration.",
        "bbox": [
          696,
          822,
          764,
          826
        ]
      },
      {
        "text": "C",
        "bbox": [
          737,
          831,
          744,
          840
        ]
      },
      {
        "text": "L203",
        "bbox": [
          808,
          518,
          822,
          539
        ]
      },
      {
        "text": "J1102",
        "bbox": [
          798,
          646,
          822,
          654
        ]
      },
      {
        "text": "FID102",
        "bbox": [
          829,
          66,
          832,
          79
        ]
      },
      {
        "text": "K1200",
        "bbox": [
          830,
          322,
          841,
          348
        ]
      },
      {
        "text": "R1200",
        "bbox": [
          845,
          90,
          872,
          110
        ]
      },
      {
        "text": "R1201",
        "bbox": [
          842,
          141,
          868,
          161
        ]
      },
      {
        "text": "C1203",
        "bbox": [
          844,
          213,
          852,
          239
        ]
      },
      {
        "text": "C1200",
        "bbox": [
          876,
          213,
          884,
          239
        ]
      },
      {
        "text": "C1202",
        "bbox": [
          842,
          274,
          868,
          282
        ]
      },
      {
        "text": "K1201",
        "bbox": [
          867,
          327,
          878,
          353
        ]
      },
      {
        "text": "C213",
        "bbox": [
          847,
          508,
          869,
          524
        ]
      },
      {
        "text": "J1101",
        "bbox": [
          866,
          629,
          874,
          653
        ]
      },
      {
        "text": "Created J1600",
        "bbox": [
          852,
          761,
          879,
          767
        ]
      },
      {
        "text": "J1601",
        "bbox": [
          910,
          109,
          918,
          133
        ]
      },
      {
        "text": "J1401",
        "bbox": [
          910,
          196,
          918,
          220
        ]
      },
      {
        "text": "J1400",
        "bbox": [
          910,
          444,
          918,
          468
        ]
      },
      {
        "text": "J1100",
        "bbox": [
          915,
          591,
          923,
          615
        ]
      },
      {
        "text": "Date Name",
        "bbox": [
          887,
          747,
          903,
          753
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887,
          761,
          925,
          767
        ]
      },
      {
        "text": "T. Ripplinger",
        "bbox": [
          930,
          761,
          972,
          767
        ]
      },
      {
        "text": "Checked",
        "bbox": [
          852,
          775,
          882,
          782
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887,
          775,
          925,
          782
        ]
      },
      {
        "text": "D.Sauter",
        "bbox": [
          930,
          775,
          960,
          781
        ]
      },
      {
        "text": "Elektromedizin GmbH",
        "bbox": [
          871,
          817,
          958,
          825
        ]
      },
      {
        "text": "Project",
        "bbox": [
          980,
          747,
          1003,
          753
        ]
      },
      {
        "text": "PB HW",
        "bbox": [
          980,
          760,
          1009,
          768
        ]
      },
      {
        "text": "Title",
        "bbox": [
          980,
          775,
          994,
          782
        ]
      },
      {
        "text": "Assembly Drawing",
        "bbox": [
          980,
          789,
          1054,
          797
        ]
      },
      {
        "text": "Schematic Revision",
        "bbox": [
          979,
          803,
          1045,
          810
        ]
      },
      {
        "text": "004",
        "bbox": [
          1063,
          803,
          1076,
          810
        ]
      },
      {
        "text": "Layout Revision EENr Assy EENr PCB",
        "bbox": [
          979,
          818,
          1033,
          824
        ]
      },
      {
        "text": "30160-860 40160-860",
        "bbox": [
          1095,
          761,
          1173,
          767
        ]
      },
      {
        "text": "Size",
        "bbox": [
          1136,
          775,
          1150,
          782
        ]
      },
      {
        "text": "A3",
        "bbox": [
          1150,
          789,
          1161,
          797
        ]
      },
      {
        "text": "Sheet",
        "bbox": [
          1136,
          803,
          1155,
          810
        ]
      },
      {
        "text": "04.04.2023",
        "bbox": [
          1063,
          818,
          1101,
          824
        ]
      },
      {
        "text": "7 of 7",
        "bbox": [
          1146,
          818,
          1165,
          824
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027,
          831,
          1035,
          840
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027,
          3,
          1035,
          12
        ]
      }
    ]
  },
  {
    "file": "D275036_DE_000.pdf",
    "page": 1,
    "elements": [
      {
        "text": "Aurora Project number",
        "bbox": [
          20,
          54,
          39,
          60
        ]
      },
      {
        "text": "6520001",
        "bbox": [
          144,
          54,
          169,
          60
        ]
      },
      {
        "text": "25241",
        "bbox": [
          261,
          54,
          278,
          60
        ]
      },
      {
        "text": "Document class Document number",
        "bbox": [
          20,
          65,
          65,
          70
        ]
      },
      {
        "text": "Packaging Specification D275036 Version: 000",
        "bbox": [
          20,
          77,
          86,
          83
        ]
      },
      {
        "text": "Packaging specification/Verpackungsvorschrift",
        "bbox": [
          62,
          110,
          372,
          123
        ]
      },
      {
        "text": "This packaging specification applies to/Diese Verpackungsvorschrift ist anzuwenden für:",
        "bbox": [
          62,
          155,
          482,
          164
        ]
      },
      {
        "text": "Erbe article no./Erbe Artikel Nr.:",
        "bbox": [
          62,
          183,
          205,
          192
        ]
      },
      {
        "text": "Designation/Bezeichnung:",
        "bbox": [
          62,
          196,
          179,
          205
        ]
      },
      {
        "text": "30160-860",
        "bbox": [
          239,
          183,
          287,
          192
        ]
      },
      {
        "text": "PB HW VIO 3n PowerBoard",
        "bbox": [
          239,
          196,
          361,
          205
        ]
      },
      {
        "text": "Image of packaging (not mandatory)/Abbildung der Verpackung (nicht zwingend erforderlich):",
        "bbox": [
          62,
          304,
          512,
          313
        ]
      }
    ]
  },
  {
    "file": "D275036_DE_000.pdf",
    "page": 2,
    "elements": [
      {
        "text": "Project name",
        "bbox": [
          20,
          41,
          58,
          47
        ]
      },
      {
        "text": "Aurora Project number Change number",
        "bbox": [
          20,
          54,
          39,
          60
        ]
      },
      {
        "text": "6520001",
        "bbox": [
          144,
          54,
          169,
          60
        ]
      },
      {
        "text": "25241",
        "bbox": [
          261,
          54,
          278,
          60
        ]
      },
      {
        "text": "Document class Document number",
        "bbox": [
          20,
          65,
          65,
          70
        ]
      },
      {
        "text": "Packaging Specification D275036 Version: 000",
        "bbox": [
          20,
          77,
          86,
          83
        ]
      },
      {
        "text": "Delivery conditions/Anlieferbedingungen:",
        "bbox": [
          62,
          109,
          263,
          118
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          453,
          135,
          464,
          146
        ]
      },
      {
        "text": "Delivery on pallet mandatory/Anlieferung auf Palette zwingend erforderlich:",
        "bbox": [
          62,
          137,
          445,
          147
        ]
      },
      {
        "text": "Yes/Ja",
        "bbox": [
          468,
          137,
          496,
          146
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          453,
          149,
          464,
          160
        ]
      },
      {
        "text": "No/Nein",
        "bbox": [
          468,
          152,
          506,
          160
        ]
      },
      {
        "text": "Pallet dimensions/Palettenabmaße:",
        "bbox": [
          82,
          165,
          242,
          174
        ]
      },
      {
        "text": "Length/Länge: 1,2 Meter(s)",
        "bbox": [
          82,
          178,
          224,
          187
        ]
      },
      {
        "text": "Width/Breite:",
        "bbox": [
          82,
          192,
          143,
          201
        ]
      },
      {
        "text": "0,8 Meter(s)",
        "bbox": [
          169,
          192,
          224,
          201
        ]
      },
      {
        "text": "Height/Höhe:",
        "bbox": [
          82,
          205,
          142,
          214
        ]
      },
      {
        "text": "1,4 Meter(s)",
        "bbox": [
          169,
          205,
          224,
          214
        ]
      },
      {
        "text": "Specifications/Spezifikationen",
        "bbox": [
          62,
          234,
          224,
          243
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          417,
          261,
          429,
          272
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          474,
          261,
          486,
          272
        ]
      },
      {
        "text": "To be supplied in ESD packaging/Anlieferung in ESD-Verpackung:",
        "bbox": [
          80,
          263,
          369,
          272
        ]
      },
      {
        "text": "Yes/Ja No/Nein",
        "bbox": [
          432,
          263,
          527,
          272
        ]
      },
      {
        "text": "To be supplied in cleanroom compatible packaging/Anlieferung in Reinraum-geeigneter Verpackung:",
        "bbox": [
          80,
          277,
          373,
          300
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          417,
          289,
          429,
          300
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          474,
          289,
          486,
          300
        ]
      },
      {
        "text": "Packaging levels/Verpackungsebenen",
        "bbox": [
          62,
          319,
          260,
          328
        ]
      },
      {
        "text": "Packaging level 0 is the smallest packing unit and must always be defined. If required, higher packaging levels can be defined.",
        "bbox": [
          80,
          347,
          493,
          370
        ]
      },
      {
        "text": "Verpackungsebene 0 ist die kleinste Verpackungseinheit und ist in jedem Fall zu definieren - Bei Bedarf können zusätzlich höhere Verpackungsebenen definiert werden.",
        "bbox": [
          80,
          375,
          502,
          398
        ]
      },
      {
        "text": "Packaging level 0/Verpackungsebene 0:",
        "bbox": [
          98,
          417,
          287,
          427
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          170,
          429,
          181,
          441
        ]
      },
      {
        "text": "Type/Art:",
        "bbox": [
          98,
          432,
          140,
          441
        ]
      },
      {
        "text": "Reusable packaging/Mehrwegbehälter",
        "bbox": [
          185,
          432,
          357,
          441
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          170,
          444,
          181,
          455
        ]
      },
      {
        "text": "Cardboard/Kartonage",
        "bbox": [
          185,
          446,
          283,
          455
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          170,
          457,
          181,
          469
        ]
      },
      {
        "text": "Bag/Beutel",
        "bbox": [
          185,
          460,
          234,
          469
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          170,
          471,
          181,
          483
        ]
      },
      {
        "text": "Other/Sonstiges:",
        "bbox": [
          185,
          474,
          260,
          483
        ]
      },
      {
        "text": "Content quantity of packaging level 0 in pcs./Inhaltsmenge der Verpackungsebene 0 in Stk: 4",
        "bbox": [
          98,
          502,
          510,
          511
        ]
      },
      {
        "text": "Dimensions of packaging level 0/Abmessungen der Verpackungsebene 0:",
        "bbox": [
          98,
          530,
          422,
          539
        ]
      },
      {
        "text": "Length/Länge: 400 mm Width/Breite: 300 mm Height/Höhe: 320 mm",
        "bbox": [
          98,
          543,
          489,
          552
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          453,
          568,
          464,
          579
        ]
      },
      {
        "text": "Label on packaging level 0/Kennzeichnung der Verpackungsebene 0 mit Label:",
        "bbox": [
          98,
          570,
          444,
          579
        ]
      },
      {
        "text": "Yes/Ja",
        "bbox": [
          468,
          570,
          496,
          579
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          453,
          581,
          464,
          592
        ]
      },
      {
        "text": "No/Nein",
        "bbox": [
          468,
          584,
          506,
          592
        ]
      },
      {
        "text": "Yes/Ja No/Nein",
        "bbox": [
          432,
          291,
          527,
          300
        ]
      },
      {
        "text": "Content of the label/Labelinhalt:",
        "bbox": [
          98,
          610,
          243,
          619
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          163,
          621,
          174,
          633
        ]
      },
      {
        "text": "Erbe article no./Erbe-Artikel Nr.",
        "bbox": [
          178,
          624,
          318,
          633
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          163,
          635,
          174,
          646
        ]
      },
      {
        "text": "Designation/Bezeichnung",
        "bbox": [
          178,
          637,
          291,
          646
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          163,
          648,
          174,
          660
        ]
      },
      {
        "text": "Quantity/Menge",
        "bbox": [
          178,
          651,
          252,
          660
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          163,
          662,
          174,
          673
        ]
      },
      {
        "text": "Lot no. or SN/Lot- bzw. SN",
        "bbox": [
          178,
          664,
          295,
          673
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          163,
          675,
          174,
          686
        ]
      },
      {
        "text": "Expiry date or Manufacturing date/Mindesthaltbarkeitsdatum bzw.",
        "bbox": [
          178,
          677,
          478,
          686
        ]
      },
      {
        "text": "Herstelldatum",
        "bbox": [
          177,
          691,
          240,
          700
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          163,
          702,
          174,
          713
        ]
      },
      {
        "text": "Barcode",
        "bbox": [
          178,
          704,
          214,
          713
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          276,
          718,
          287,
          729
        ]
      },
      {
        "text": " Content/Inhalt:",
        "bbox": [
          179,
          720,
          262,
          730
        ]
      },
      {
        "text": "Erbe article no./Erbe Artikel Nr. +",
        "bbox": [
          291,
          719,
          440,
          730
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          276,
          735,
          287,
          747
        ]
      },
      {
        "text": "Other/Sonstiges:",
        "bbox": [
          162,
          752,
          237,
          761
        ]
      },
      {
        "text": "Lot no. or SN/Lot- bzw. SN +",
        "bbox": [
          291,
          736,
          420,
          747
        ]
      },
      {
        "text": "FB_0526_Packaging specification/Verpackungsvorschrift",
        "bbox": [
          310,
          784,
          567,
          793
        ]
      },
      {
        "text": "Page:",
        "bbox": [
          515,
          799,
          530,
          804
        ]
      }
    ]
  },
  {
    "file": "D275036_DE_000.pdf",
    "page": 3,
    "elements": [
      {
        "text": "Project name",
        "bbox": [
          20,
          41,
          58,
          47
        ]
      },
      {
        "text": "Aurora Project number Change number",
        "bbox": [
          20,
          54,
          39,
          60
        ]
      },
      {
        "text": "6520001",
        "bbox": [
          144,
          54,
          169,
          60
        ]
      },
      {
        "text": "25241",
        "bbox": [
          261,
          54,
          278,
          60
        ]
      },
      {
        "text": "Document class Document number",
        "bbox": [
          20,
          65,
          65,
          70
        ]
      },
      {
        "text": "Packaging Specification D275036 Version: 000",
        "bbox": [
          20,
          77,
          86,
          83
        ]
      },
      {
        "text": "Packaging level 1/Verpackungsebene 1:",
        "bbox": [
          98,
          123,
          287,
          132
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          170,
          135,
          181,
          146
        ]
      },
      {
        "text": "Type/Art:",
        "bbox": [
          98,
          137,
          140,
          146
        ]
      },
      {
        "text": "Reusable packaging/Mehrwegbehälter",
        "bbox": [
          185,
          137,
          357,
          146
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          170,
          149,
          181,
          160
        ]
      },
      {
        "text": "Cardboard/Kartonage",
        "bbox": [
          185,
          152,
          283,
          160
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          170,
          163,
          181,
          174
        ]
      },
      {
        "text": "Bag/Beutel",
        "bbox": [
          185,
          165,
          234,
          174
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          170,
          177,
          181,
          188
        ]
      },
      {
        "text": "Other/Sonstiges:",
        "bbox": [
          185,
          179,
          260,
          188
        ]
      },
      {
        "text": "Content quantity of packaging level 1 in pcs./Inhaltsmenge der Verpackungsebene 1 in Stk:",
        "bbox": [
          98,
          207,
          502,
          216
        ]
      },
      {
        "text": "Dimensions of packaging level 1/Abmessungen der Verpackungsebene 1:",
        "bbox": [
          98,
          236,
          422,
          244
        ]
      },
      {
        "text": "Length/Länge:",
        "bbox": [
          98,
          249,
          162,
          258
        ]
      },
      {
        "text": "mm Width/Breite:",
        "bbox": [
          198,
          249,
          301,
          258
        ]
      },
      {
        "text": "mm Height/Höhe:",
        "bbox": [
          340,
          249,
          441,
          258
        ]
      },
      {
        "text": "mm",
        "bbox": [
          482,
          249,
          499,
          258
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          453,
          273,
          464,
          285
        ]
      },
      {
        "text": "Label on packaging level 1/Kennzeichnung der Verpackungsebene 1 mit Label:",
        "bbox": [
          98,
          276,
          444,
          285
        ]
      },
      {
        "text": "Yes/Ja",
        "bbox": [
          468,
          276,
          496,
          285
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          453,
          287,
          464,
          298
        ]
      },
      {
        "text": "No/Nein",
        "bbox": [
          468,
          289,
          506,
          298
        ]
      },
      {
        "text": "Content of the label/Labelinhalt:",
        "bbox": [
          98,
          316,
          243,
          325
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          163,
          327,
          174,
          338
        ]
      },
      {
        "text": "Erbe article no./Erbe-Artikel Nr.",
        "bbox": [
          178,
          329,
          318,
          338
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          163,
          341,
          174,
          352
        ]
      },
      {
        "text": "Designation/Bezeichnung",
        "bbox": [
          178,
          343,
          291,
          352
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          163,
          354,
          174,
          365
        ]
      },
      {
        "text": "Quantity/Menge",
        "bbox": [
          178,
          356,
          252,
          365
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          163,
          367,
          174,
          379
        ]
      },
      {
        "text": "Lot no. or SN/Lot- bzw. SN",
        "bbox": [
          178,
          370,
          295,
          379
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          163,
          381,
          174,
          392
        ]
      },
      {
        "text": "Expiry date or Manufacturing date/Mindesthaltbarkeitsdatum bzw. Herstelldatum",
        "bbox": [
          177,
          383,
          478,
          406
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          163,
          408,
          174,
          419
        ]
      },
      {
        "text": "Barcode",
        "bbox": [
          178,
          410,
          214,
          419
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          276,
          424,
          287,
          435
        ]
      },
      {
        "text": " Content/Inhalt:",
        "bbox": [
          179,
          426,
          262,
          435
        ]
      },
      {
        "text": "Erbe article no./Erbe Artikel Nr. +",
        "bbox": [
          291,
          424,
          440,
          436
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          276,
          441,
          287,
          452
        ]
      },
      {
        "text": "Other/Sonstiges:",
        "bbox": [
          162,
          458,
          237,
          467
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          99,
          483,
          110,
          494
        ]
      },
      {
        "text": "Additional packaging levels/weitere Verpackungsebenen:",
        "bbox": [
          116,
          485,
          390,
          495
        ]
      },
      {
        "text": "Article/Einzelartikel",
        "bbox": [
          62,
          634,
          175,
          644
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          417,
          646,
          429,
          657
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          479,
          646,
          491,
          657
        ]
      },
      {
        "text": "Label on article/Kennzeichnung des Einzelartikel mit Label:",
        "bbox": [
          98,
          648,
          358,
          657
        ]
      },
      {
        "text": "Yes/Ja",
        "bbox": [
          432,
          648,
          461,
          657
        ]
      },
      {
        "text": "No/Nein",
        "bbox": [
          494,
          648,
          532,
          657
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          234,
          672,
          245,
          684
        ]
      },
      {
        "text": "Label content/Labelinhalt:",
        "bbox": [
          97,
          675,
          215,
          684
        ]
      },
      {
        "text": "Erbe article no./Erbe-Artikel Nr.",
        "bbox": [
          248,
          675,
          389,
          684
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          234,
          686,
          245,
          697
        ]
      },
      {
        "text": "Designation/Bezeichnung",
        "bbox": [
          248,
          688,
          362,
          697
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          234,
          699,
          245,
          711
        ]
      },
      {
        "text": "Quantity/Menge",
        "bbox": [
          248,
          702,
          323,
          711
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          234,
          713,
          245,
          724
        ]
      },
      {
        "text": "Lot no. or SN/Lot- bzw. SN",
        "bbox": [
          248,
          715,
          366,
          724
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          234,
          726,
          245,
          737
        ]
      },
      {
        "text": "Expiry date or manufacturing date/Mindesthaltbarkeitsdatum bzw. Herstelldatum",
        "bbox": [
          247,
          729,
          525,
          751
        ]
      },
      {
        "text": "Lot no. or SN/Lot- bzw. SN +",
        "bbox": [
          291,
          442,
          420,
          453
        ]
      },
      {
        "text": "FB_0526_Packaging specification/Verpackungsvorschrift",
        "bbox": [
          310,
          784,
          567,
          793
        ]
      },
      {
        "text": "Page:",
        "bbox": [
          515,
          799,
          530,
          804
        ]
      }
    ]
  },
  {
    "file": "D275036_DE_000.pdf",
    "page": 4,
    "elements": [
      {
        "text": "Aurora Project number",
        "bbox": [
          20,
          54,
          39,
          60
        ]
      },
      {
        "text": "6520001",
        "bbox": [
          144,
          54,
          169,
          60
        ]
      },
      {
        "text": "25241",
        "bbox": [
          261,
          54,
          278,
          60
        ]
      },
      {
        "text": "Document class Document number",
        "bbox": [
          20,
          65,
          65,
          70
        ]
      },
      {
        "text": "Packaging Specification D275036 Version: 000",
        "bbox": [
          20,
          77,
          86,
          83
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          234,
          106,
          245,
          117
        ]
      },
      {
        "text": "Barcode",
        "bbox": [
          248,
          108,
          285,
          117
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          347,
          122,
          358,
          133
        ]
      },
      {
        "text": " Content/Inhalt:",
        "bbox": [
          250,
          124,
          332,
          134
        ]
      },
      {
        "text": "Erbe article no./Erbe Artikel Nr. +",
        "bbox": [
          362,
          123,
          511,
          134
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          347,
          139,
          358,
          150
        ]
      },
      {
        "text": "Other/Sonstiges:",
        "bbox": [
          233,
          156,
          308,
          165
        ]
      },
      {
        "text": "Comments and additional information on transport and delivery conditions/Vermerke und Zusätze zu den Transport-, Lieferbedingungen:",
        "bbox": [
          62,
          198,
          494,
          221
        ]
      },
      {
        "text": "Pendelverpackung KLT ESD EG43/32 Schaumstoffeinlage inkl. Tray Deckel",
        "bbox": [
          62,
          239,
          226,
          261
        ]
      },
      {
        "text": "Lot no. or SN/Lot- bzw. SN +",
        "bbox": [
          362,
          140,
          490,
          151
        ]
      }
    ]
  }
]
