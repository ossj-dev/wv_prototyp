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
        "REF"
        "Erbe-Art.Nr."
        "Lot"
        "Menge"
        "Barcode"
      ]
    }
  ]
}
</Beispiel 2>

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
