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

### BEISPIELE ZUR ORIENTIERUNG:
Hier sind korrekte Beispiele, wie die Extraktion aussehen muss. Nutze die Werte aus den Beispielen NICHT für das finale Dokument.

<Beispiel 1>
Eingabetext: "Vp. Vor. Lap Schlauchset 5m ohne Ventil Projektname Projektnummer ÄM‐Nummer LAP tubing set IES 3 without valve 6521600 ‐ Dokumentklasse Dokumentnummer Verpackungsvorschrift D199226 Version: 000 Verpackungsvorschrift deutsch Die Verpackungsvorschrift ist anzuwenden für: Erbe‐Artikel Nr.: 20323‐011 Bezeichnung: LAP Schlauchset IES 3 ohne Ventil 5m Abbildung der Verpackung (nicht zwingend erforderlich): FB_0526_Verpackungsvorschrift deutsch Basiert auf Dokumentvorlage OID: 1501230, Version: 10 Version: Seite: 2 1/3 Vp. Vor. Lap Schlauchset 5m ohne Ventil Projektname Projektnummer ÄM‐Nummer LAP tubing set IES 3 without valve 6521600 ‐ Dokumentklasse Dokumentnummer Verpackungsvorschrift D199226 Version: 000 Anlieferbedingungen: 1. Anlieferung auf Palette zwingend erforderlich: [X] Ja [ ] Nein Palettenabmaße: Länge: 1,2 Meter Breite: 0,8 Meter Höhe: 1,8 Meter 2. Spezifikationen Anlieferung in ESD‐Verpackung: [ ] Ja [X] Nein Anlieferung in Reinraum geeigneter Verpackung: [ ] Ja [X] Nein 3. Verpackungsebenen Verpackungsebene 0 ist die kleinste Verpackungseinheit und ist in jedem Fall zu definieren ‐ Bei Bedarf können zusätzlich höhere Verpackungsebenen definiert werden. Verpackungsebene 0: Art: [ ] Mehrwegbehälter [ ] Kartonage [X] Beutel [ ] sonstiges: Inhaltsmenge der Verpackungsebene 0 in Stk.: 1 Abmessungen der Verpackungsebene 0: Länge: 250 mm Breite: 400 mm Höhe: mm Kennzeichnung der Verpackungsebene 0 mit Label: [X] Ja [ ] Nein Labelinhalt: [X] Erbe‐Artikel Nr. [X] Bezeichnung [X] Menge [X] Lot‐ bzw. SN [X] Mindesthaltbarkeitsdatum bzw. Herstelldatum [X] Barcode  Inhalt: [X] Erbe‐Artikel Nr. + [X] Lot‐ bzw. SN + Haltbarkeitsdatum Sonstiges: [X] Verpackungsebene 1: Art: [ ] Mehrwegbehälter [X] Kartonage [ ] Beutel [ ] sonstiges: Inhaltsmenge der Verpackungsebene 1 in Stk.: 10 Abmessungen der Verpackungsebene 1: Länge: 386 mm Breite: 281 mm Höhe: 346 mm Kennzeichnung der Verpackungsebene 1 mit Label: [X] Ja [ ] Nein Labelinhalt: [X] Erbe‐Artikel Nr. [X] Bezeichnung [X] Menge [X] Lot‐ bzw. SN [X] Mindesthaltbarkeitsdatum bzw. Herstelldatum FB_0526_Verpackungsvorschrift deutsch Basiert auf Dokumentvorlage OID: 1501230, Version: 10 Version: Seite: 2 2/3 Vp. Vor. Lap Schlauchset 5m ohne Ventil Projektname Projektnummer ÄM‐Nummer LAP tubing set IES 3 without valve 6521600 ‐ Dokumentklasse Dokumentnummer Verpackungsvorschrift D199226 Version: 000 [X] Barcode  Inhalt: [X] Erbe‐Artikel Nr. + [X] Lot‐ bzw. SN + Haltbarkeitsdatum Sonstiges: [ ] weitere Verpackungsebenen: 4. Einzelartikel Kennzeichnung des Einzelartikel mit Label: [X] Ja [ ] Nein Labelinhalt: [X] Erbe‐Artikel Nr. [X] Bezeichnung [X] Menge [X] Lot‐ bzw. SN [X] Mindesthaltbarkeitsdatum bzw. Herstelldatum [X] Barcode  Inhalt: [X] Erbe‐Artikel Nr. + [X] Lot‐ bzw. SN + Haltbarkeitsdatum Sonstiges: Vermerke und Zusätze zu den Transport‐, Lieferbedingungen: FB_0526_Verpackungsvorschrift deutsch Basiert auf Dokumentvorlage OID: 1501230, Version: 10 Version: Seite: 2 3/3 LABELLING PRODUCT SPECIFICATION IDENTIFICATION PRODUIT FINI FOR034-3 A4 P. 1 / 2 REF : ONG08899ST223_IDENT Designation : LAP tubing set IES 3 - without valve 5m Verif R&D : Date : Verif QA : Date : Verif client : Date : REVISION : 04 Etat : IN PROGRESS Etiquette produit 1 Product label 1 106 72 WARNING : 5 years use-by date ATTENTION: Date de péremption de 5 ans Etiquette produit 2 Product label 2 80 40 25 50 WARNING : 5 years use-by date ATTENTION: Date de péremption de 5 ans 04 03 12/03/2025 23/01/2024 HAR HAR CE mark number change. Add importer and EC REP and label layout change acc. to PCC-GEN-23-M006- PMP Implementation of new specification format, previous version of labels in previous version of packaging specification. Removal of UK Rep acc. to the change PCC-GEN-23-M005-PMP - Rev. Date Designer Modification ou FOR021 N° FOR073 Le Copori - 9, avenue Albert II - MC 98000 MONACO - Phone : + 377.97.98.42.32 - Fax : + 377.92.05.61.50 - http://www.promepla.com Propriété PROMEPLA - Usage Interne - Ne peut être reproduit ou diffusé sans autorisation LABELLING PRODUCT SPECIFICATION IDENTIFICATION PRODUIT FINI FOR034-3 A4 P. 2 / 2 REF : ONG08899ST223_IDENT Designation : LAP tubing set IES 3 - without valve 5m Verif R&D : Date : Verif QA : Date : Verif client : Date : REVISION : 04 Etat : IN PROGRESS Etiquette carton Box label 145 97 WARNING : 5 years use-by date ATTENTION: Date de péremption de 5 ans Le Copori - 9, avenue Albert II - MC 98000 MONACO - Phone : + 377.97.98.42.32 - Fax : + 377.92.05.61.50 - http://www.promepla.com Propriété PROMEPLA - Usage Interne - Ne peut être reproduit ou diffusé sans autorisation"
Erwarteter JSON-Output:
{
  "dokumentensprache": "Deutsch",
  "artikelnummer": 20323‐011,
  "labels": [
    {
      "verpackungsebene": "Verpackungsebene 0",
      "label_inhalt": [
        "Erbe‐Artikel Nr.",
        "Bezeichnung",
        "Menge",
        "Lot‐ bzw. SN",
        "Mindesthaltbarkeitsdatum bzw. Herstelldatum",
        "Barcode"
      ]
    },
    {
      "verpackungsebene": "Verpackungsebene 1",
      "label_inhalt": [
        "Erbe‐Artikel Nr.",
        "Bezeichnung",
        "Menge",
        "Lot‐ bzw. SN",
        "Mindesthaltbarkeitsdatum bzw. Herstelldatum",
        "Barcode"
      ]
    },
    {
      "verpackungsebene": "Einzelartikel",
      "label_inhalt": [
        "Erbe‐Artikel Nr.",
        "Bezeichnung",
        "Menge",
        "Lot‐ bzw. SN",
        "Mindesthaltbarkeitsdatum bzw. Herstelldatum",
        "Barcode"
      ]
    }
  ]
}
</Beispiel 1>

<Beispiel 2>
Eingabetext: "=== DOKUMENT: 800020459.pdf ===
--- SEITE 1 ---
Distributed by HSW ULTRA-JANET QUICK-LOCK, 150 ML [X] [X] rbE Keltenstrasse 1 Henke-Sass, Wolf GmbH 78532 Tuttlingen Erbe Elektromedizin GmbH Germany
Waldhoernlestrasse 17 Made in Germany 72072 Tuebingen, Germany 2024-09
REF 8300065309 [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] Johner Medical Schweiz GmbH CH REP Tafelstattstrasse 13a CH-6415 Arth Erbe Art.Nr.: 20862-089 [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X]
LOT 1234567 米 R ONLY 21 [X] [X] [X] [X] [X] [X] PAP QTY 1 MD UKCE
+60°℃ 90% (01)04035873074793 -18°C- 15% (11)240926
(10)1234567 800020459 Rev.1
--- SEITE 2 ---
HSW ULTRA-JANET QUICK-LOCK , 150ML
DE Blasenspritze Quick-Lock -Anschluss, 150ml EN Bladder syringe Quick lock connection, 150ml FR Seringue à vessie Raccord Quick-Lock, 150ml NO Bleresprøyte Quick-Lock-làs, 150 ml DA Blæresprøjte Quick-Lock-fatning, 150ml FI Virtsarakkoruisku, quick-lock-lukitus, 150 ml SV Blâsspruta med Quick-Lock-anslutning, 150 ml SL Brizga za mehur, priključek Quick-Lock, 150 ml IT Attacco Quick-Lock della siringa per vescica, 150ml ES Jeringa vesical conexión Quick-Lock, 150ml PT Seringa para irrigação vesical com conector Quick Lock, 150ml NL Blaasspuit quick-lock-aansluiting, 150 ml PL Strzykawka cewnikowa złącze quick-lock, 150ml EL Σúριγγα oupοδóχου κστη με σvδεση Quick-Lοck, 150ml CS Lavážní stříkačka s připojením Quick-Lock, 150 ml HU Hólyagfecskendő Quick-Lock csatlakozóval, 150ml - , 150 HR Quick-lock priključak štrcaljke za mjehur, 150 ml ET Quick-Lock-liitmikuga põiesüstal, 150 ml LV ŠJirce ar Quick-Lock savienojumu, 150 ml LT Šlapimo pūslės švirkšto Quick-Lock jungtis, 150 ml RO Seringå pentru vezica urinară conectare tip Quick-Lock, 150 ml SK Injekčná striekačka na močový mechúr, s uzáverom Quick-Lock, 150ml 800020460 Rev.1
=== DOKUMENT: 800020800.pdf ===
--- SEITE 1 ---
[X] [X] [X] [X] [X] [X] [X] [X]
[X] [X] [X] [X]
[X]"

Erwarteter JSON-Output:
{
  "dokumentensprache": "Deutsch",
  "artikelnummer": 20862-089,
  "labels": [
    {
      "verpackungsebene": "Beispiel-Label",
      "label_inhalt": [
        "REF / Erbe-Art.Nr.",
        "Lot",
        "Menge",
        "Barcode"
      ]
    }
  ]
}
</Beispiel 2>

## Benutzereingabe

=== DOKUMENT: D108713_DE_001.pdf ===
--- SEITE 1 ---
REF-Nr.ERBE
 Etikettenwerkstoff.PolyesterfoliemitAcrylatkleber
 BeiPlatzmangelkanndasLabelgeteiltwerden
 LabelgrößekannvomZuliefererbestimmtwerden
 Mindestschriftgröße2mm
 DasSymbolREFkannauchnuralsTextdargestelltwerden
 DieLOT-NummerundderStatusistentsprechenddemArbeitsauftrageinzutragen
 DemZuliefererwirdfreigestelltdenDatamatrixcodemiteineralphanumerischenTrennung zwischen REF-Nr. und LOT (z.B. 12345-678OP123456) oder ohne Trennung (z.B. 12345-678123456) auszuführen
 MindestgrößeDatamatrixcode6x6mm
| Alle mit * gekennzeichneten Zeichnungsobjekte haben . | Alle mit * gekennzeichneten Zeichnungsobjekte haben . | Alle mit * gekennzeichneten Zeichnungsobjekte haben . | sich gegenüber der . | sich gegenüber der . | Vorgängerversion . 2:1 . | Vorgängerversion . 2:1 . | geändert! | |---------------------------------------------------------|---------------------------------------------------------|---------------------------------------------------------|------------------------|------------------------|----------------------------|----------------------------|----------------| | Werkstoff, Bezeichnung, Lieferant | Werkstoff, Bezeichnung, Lieferant | Werkstoff, Bezeichnung, Lieferant | Werkstoff-Nr. | Werkstoff-Nr. | Volumencm³ Maßstab | Volumencm³ Maßstab | geändert! | | Status | ERBE-Nr. | ÄM-Nr. | | Datum | Name Titel: | | | | Gültig | 30135-804 | 20023 | Bearb. | 07.06.2016 | UWED Labellayout | Chargenpflicht | Chargenpflicht | | | | | Gepr. | 07.06.2016 | LAURAS 2D-Code | | | | Dokumentklasse | Dokumentklasse | | | | Dokumentnummer: | Version: | Größe: | | Produktkennzeichnung | Produktkennzeichnung | | | | | | | | Oberflächenbeschaffenheit nach ISO 1302 | Oberflächenbeschaffenheit nach ISO 1302 | | | | D108713 | 001 | | | Maße ohne Toleranzangabe ISO 2768 - mH | Maße ohne Toleranzangabe ISO 2768 - mH | | Elektromedizin GmbH | Elektromedizin GmbH | | | | | | | | Urspr.: | Urspr.: | Ers.für: | Blatt: | 1 / 1 |
=== DOKUMENT: D230937_007_Assembly.pdf ===
--- SEITE 1 ---
1 1
2 2
3 3
4 4 A
A Realistic View B B C Status Document type Drawing No part of this document may be reproduced or transmitted in any form or by any means, electronic or mechanical, including photocopying, recording or otherwise, without prior written permission. Any infringement shall give rise to an obligation to pay damages. All rights reserved in the event of patent, utility model or design registration. C Created Date Name 05.08.2026 T. Ripplinger Checked 05.08.2026 D.Sauter Elektromedizin GmbH Project PB HW Title Assembly Drawing Schematic Revision 004 Layout Revision EENr Assy EENr PCB 30160-875 40160-860 Size A3 Sheet 04.04.2023 1 of 7 D D
--- SEITE 2 ---
1 1
2 2
3 3
4 4 A
A View from Top side (Scale 1:1) B B C Status Document type Drawing No part of this document may be reproduced or transmitted in any form or by any means, electronic or mechanical, including photocopying, recording or otherwise, without prior written permission. Any infringement shall give rise to an obligation to pay damages. All rights reserved in the event of patent, utility model or design registration. C Created Date Name 05.08.2026 T. Ripplinger Checked 05.08.2026 D.Sauter Elektromedizin GmbH Project PB HW Title Assembly Drawing Schematic Revision 004 Layout Revision EENr Assy EENr PCB 30160-875 40160-860 Size A3 Sheet 04.04.2023 2 of 7 D D
--- SEITE 3 ---
1 1
2 2
3 3
4 4 A
A Realistic View Bottom B B C Vorzugsrichtung Wellenlötung auf der LS Status Document type Drawing No part of this document may be reproduced or transmitted in any form or by any means, electronic or mechanical, including photocopying, recording or otherwise, without prior written permission. Any infringement shall give rise to an obligation to pay damages. All rights reserved in the event of patent, utility model or design registration. C Created Date Name 05.08.2026 T. Ripplinger Checked 05.08.2026 D.Sauter Elektromedizin GmbH Project PB HW Title Assembly Drawing Schematic Revision 004 Layout Revision EENr Assy EENr PCB 30160-875 40160-860 Size A3 Sheet 04.04.2023 3 of 7 D D
--- SEITE 4 ---
1 1
2 2
3 3
4 4 A
A View from Bottom side (Scale 2:3) B B C Status Document type Drawing No part of this document may be reproduced or transmitted in any form or by any means, electronic or mechanical, including photocopying, recording or otherwise, without prior written permission. Any infringement shall give rise to an obligation to pay damages. All rights reserved in the event of patent, utility model or design registration. C Created Date Name 05.08.2026 T. Ripplinger Checked 05.08.2026 D.Sauter Elektromedizin GmbH Project PB HW Title Assembly Drawing Schematic Revision 004 Layout Revision EENr Assy EENr PCB 30160-875 40160-860 Size A3 Sheet 04.04.2023 4 of 7 D D
--- SEITE 5 ---
[X] 1 1
[X]
[X]
[X]
[X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] 2 2
[X]
3 3
[X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X]
[ ]
4 4 L301 K300 C318 L300 C317 J301 SW300 SW300 A View from Top side (Scale 1:1) Designator11 C301 C302 J300 J1000
A RV300 R318 J1103 C404 HS403 D401 J1500 HS400 D402 HS402 HS401 D405 D403 T400 L402 R401 R400 L1201 JP1203 JP1202 JP1201 JP1200 C1204 B C401 L403 L404 L400 C206 C206 B Q200 R1301 C200 C200 T1200 T200 T200 K1204 K1203 K1202 C1201 L1200 K1205 C216 C215 C214 J1104 L203 J1102 C R1200 R1201 C1203 C1200 C1202 K1201 C213 J1101 Status Document type Drawing No part of this document may be reproduced or transmitted in any form or by any means, electronic or mechanical, including photocopying, recording or otherwise, without prior written permission. Any infringement shall give rise to an obligation to pay damages. All rights reserved in the event of patent, utility model or design registration. C K1200 J1600 J1601 J1401 J1400 J1100 Created D Footprint J1100 für Einpressbauteil in der Montagelinie! Pins beim Wellenlöten abdecken! Date Name Project EENr Assy EENr PCB 05.08.2026 T. Ripplinger Checked 05.08.2026 D.Sauter Elektromedizin GmbH PB HW Title Assembly Drawing Schematic Revision 004 Layout Revision 30160-875 40160-860 Size A3 Sheet 04.04.2023 5 of 7 D
--- SEITE 6 ---
[X]
1 1
[ ]
[X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X]
[X]
[X]
[X]
[X]
[X] [X] [X] 2 2
[X] [X] [X]
[X]
[X]
[X] [X] [X] [X] [X] [X] 3 3
[X]
[X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [ ] [X] [X]
4 4 C1100 C1101 R1100 U1100 C1104 C1103 R1101 R1105 C1102 R1108R1104 A View from Bottom side (Scale 1:1) R1107 R1106 R1103 R1102 R1210 R908 U1201 R1211 R1212 C900 R314 R308 C316 R900 R906 R910 C907 C904 C918 U900 R902 C906 U902 R913 R1214 R1215 R1213 R912 L900 C908 D900 C909 R904 C917 C913 D901 C914 C905 R903 C902 R905 C910 R914 D902 C915 U903 R911 R909 R907 U901 C903 C911 C912 C212 L202 R901 L901 C901 R223 R222 U203 R211 R207 C220 C210 C217 D206 R212 C211 Q201 D201 Q300 R306 R305 C307 C309 D302 C308 C312 C322 C321 L302 R317 R316 C319 C320 C1207 Q1200 R1203 R1202 C1205 R1208 C501 R506 C1002 R504 R319
A L1100 C1105 C1107 C1210 C1211 C202 R1308 Q1303 R1304 C1302 Q1301 R1306 L200 R202 U201 C203 R205 C201 R203 R200 U200 R204 C204 R201 R1300 Q1300 C1301 U1301 R1303 C1300 U1300 R1305 R1302 R1307 Q1302 R610 C601 C603 C604 U601 R603 R606 C608 C1510 C1513 C1512 C1511 C1509 C1508 D1506 D1500 D1505 D1503 D1501 D1504 D1502 C1504 C1507 C1506 C1503 R600 R621 R619 R617 C612 C614 L401 R206 R607 R602 R618 C600 R604 C607 R611 R614 C606 C610 C611 R609 R601 U600 C613 R616 C602 R620 U602 C605 C609 C400 C207 D200 C209 R218 C208 D205 D203 C205 R209 C218 D208 R217 R208 C219 D207 C222 C221 B D202 C402 R214 C226 U202 R224 C224 C225 R221 C223 D204 R210 R225 R213 R220 R216 R219 R215 NT600 R605 R608 R612 R615 R402 R613 L405 B C403 C1500 C1502 C1505 C1501 C1206 C916 L201 C700 R704 R702 C703 C705 R707 R706 U702 C702 C701 C710 U700 C704 C709 R705 R700 C708 C802 R801 R703 R701 U701 R1206 C1209 U1200 C1208 R1205 R1209 R802 R800 C800 R1207 R1204 C801 R804 U800 R803 C707 C706 C1106 D1100 Q1100 R1110 R1109 C502 R505 C500 C305 R304 C300 R315 R313 C315 C311 R1112 R1111 U501 U301 U305 U304 R502 C503 R501 R300 C304 C303 U300 R307 U303 C314 C306 D303 C313 R311 U302 R310 R309 C310 D404 D400 R312 D304 R303 R302 R301 L1000 C1001 C1000 R500 U500 C504 R503 R508 R507 C D300 D301 Status Document type Drawing No part of this document may be reproduced or transmitted in any form or by any means, electronic or mechanical, including photocopying, recording or otherwise, without prior written permission. Any infringement shall give rise to an obligation to pay damages. All rights reserved in the event of patent, utility model or design registration. C Created Date Name 05.08.2026 T. Ripplinger Checked 05.08.2026 D.Sauter Elektromedizin GmbH Project PB HW Title Assembly Drawing Schematic Revision 004 Layout Revision EENr Assy EENr PCB 30160-875 40160-860 Size A3 Sheet 04.04.2023 6 of 7 D D
--- SEITE 7 ---
[X] [ ] [X]
1 1
[X]
[X]
[X]
[X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X]
2 2
[X]
[X] [X]
3 3
[X] [ ] [X] [X] [X] [X] [X] [X] [X] [X] [X] [X]
[X]
[X] 4 4 A
A Labeling Top side (Scale 1:1) Designator11 C301 C302 J300 J1000 L301 K300 C318 L300 C317 J301 SW300 SW300 FID100 RV300 R318 J1103 C404 B FID101 HS403 D401 J1500 HS400 D402 HS402 HS401 D405 D403 T400 L402 B R401 R400 L1201 JP1203 JP1202 JP1201 JP1200 C1204 C401 L403 L404 L400 C206 C206 Q200 R1301 C200 C200 T1200 T200 T200 K1204 K1203 C K1202 C1201 L1200 K1205 C216 C215 C214 J1104 Status Document type Drawing No part of this document may be reproduced or transmitted in any form or by any means, electronic or mechanical, including photocopying, recording or otherwise, without prior written permission. Any infringement shall give rise to an obligation to pay damages. All rights reserved in the event of patent, utility model or design registration. C L203 J1102 FID102 K1200 R1200 R1201 C1203 C1200 C1202 K1201 C213 J1101 Created J1600 J1601 J1401 J1400 J1100 Date Name 05.08.2026 T. Ripplinger Checked 05.08.2026 D.Sauter Elektromedizin GmbH Project PB HW Title Assembly Drawing Schematic Revision 004 Layout Revision EENr Assy EENr PCB 30160-875 40160-860 Size A3 Sheet 04.04.2023 7 of 7 D D
=== DOKUMENT: D275038_DE_000.pdf ===
--- SEITE 1 ---
VIO sv Project number 6519013 25241
Document class Document number
Packaging Specification D275038 Version: 000
Packaging specification/Verpackungsvorschrift
This packaging specification applies to/Diese Verpackungsvorschrift ist anzuwenden für:
Erbe article no./Erbe Artikel Nr.:
Designation/Bezeichnung: 30160-875 PB HW VIO seal PowerBoard
Image of packaging (not mandatory)/Abbildung der Verpackung (nicht zwingend erforderlich):
--- SEITE 2 ---
Project name
VIO sv Project number Change number 6519013 25241
Document class Document number
Packaging Specification D275038 Version: 000
Delivery conditions/Anlieferbedingungen:
[ ] Delivery on pallet mandatory/Anlieferung auf Palette zwingend erforderlich: Yes/Ja
[X] No/Nein
Pallet dimensions/Palettenabmaße:
Length/Länge: 1,2 Meter(s)
Width/Breite: 0,8 Meter(s)
Height/Höhe: 1,4 Meter(s)
Specifications/Spezifikationen
[X] [ ] To be supplied in ESD packaging/Anlieferung in ESD-Verpackung: Yes/Ja No/Nein
To be supplied in cleanroom compatible packaging/Anlieferung in Reinraum-geeigneter Verpackung: [ ] [X]
Packaging levels/Verpackungsebenen
Packaging level 0 is the smallest packing unit and must always be defined. If required, higher packaging levels can be defined.
Verpackungsebene 0 ist die kleinste Verpackungseinheit und ist in jedem Fall zu definieren - Bei Bedarf können zusätzlich höhere Verpackungsebenen definiert werden.
Packaging level 0/Verpackungsebene 0:
[X] Type/Art: Reusable packaging/Mehrwegbehälter
[ ] Cardboard/Kartonage
[ ] Bag/Beutel
[ ] Other/Sonstiges:
Content quantity of packaging level 0 in pcs./Inhaltsmenge der Verpackungsebene 0 in Stk: 4
Dimensions of packaging level 0/Abmessungen der Verpackungsebene 0:
Length/Länge: 400 mm Width/Breite: 300 mm Height/Höhe: 320 mm
[X] Label on packaging level 0/Kennzeichnung der Verpackungsebene 0 mit Label: Yes/Ja
[ ] No/Nein Yes/Ja No/Nein
Content of the label/Labelinhalt:
[X] Erbe article no./Erbe-Artikel Nr.
[X] Designation/Bezeichnung
[X] Quantity/Menge
[ ] Lot no. or SN/Lot- bzw. SN
[ ] Expiry date or Manufacturing date/Mindesthaltbarkeitsdatum bzw.
Herstelldatum
[ ] Barcode
[ ]  Content/Inhalt: Erbe article no./Erbe Artikel Nr. +
[ ]
Other/Sonstiges: Lot no. or SN/Lot- bzw. SN +
FB_0526_Packaging specification/Verpackungsvorschrift
Page:
--- SEITE 3 ---
Project name
VIO sv Project number Change number 6519013 25241
Document class Document number
Packaging Specification D275038 Version: 000
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
[X] [ ] Label on article/Kennzeichnung des Einzelartikel mit Label: Yes/Ja No/Nein
[X] Label content/Labelinhalt: Erbe article no./Erbe-Artikel Nr.
[ ] Designation/Bezeichnung
[ ] Quantity/Menge
[X] Lot no. or SN/Lot- bzw. SN
[ ] Expiry date or manufacturing date/Mindesthaltbarkeitsdatum bzw. Herstelldatum Lot no. or SN/Lot- bzw. SN +
FB_0526_Packaging specification/Verpackungsvorschrift
Page:
--- SEITE 4 ---
VIO sv Project number 6519013 25241
Document class Document number
Packaging Specification D275038 Version: 000
[X] Barcode
[X]  Content/Inhalt: Erbe article no./Erbe Artikel Nr. +
[X]
Other/Sonstiges:
Comments and additional information on transport and delivery conditions/Vermerke und Zusätze zu den Transport-, Lieferbedingungen:
Pendelverpackung KLT ESD EG43/32 Schaumstoffeinlage inkl. Tray Deckel Lot no. or SN/Lot- bzw. SN +
