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

=== DOKUMENT: 174012_DE_005 20134-005_V5.pdf ===
--- SEITE 1 ---
12/19
A
B
[X] [X] [X] [X]
[X]
C
[X] [X] [X] [X]
D [X]
E
[X] [X]
F Material: N/A Toleranzen: ISO 8015 Allgemeintoleranzen: N/A
Vollständige Spezifikation zusammen mit 3D-Datensatz: N/A
Alle Maße in mm = Prüfmaß
Alle Merkmale mit * wurden in dieser Version geändert. Status: ERBE-PLM siehe Blattgröße: A4 1 2 3 4 Weitergabe sowie Vervielfältigung dieses Dokuments, Verwertung und Mitteilung seines Inhalts sind verboten, soweit nicht ausdrücklich gestattet. Zuwiderhandlungen verpflichten zum Schadenersatz. Alle Rechte für den Fall der Patent-, Gebrauchsmuster- oder Geschmackmustereintragung vorbehalten. Company Logo, Color: Pantone Process Cyan C Erbe Elektromedizin GmbH Waldhoernlestrasse 17 72072 Tuebingen, Germany Größe/Size: 5 pt Erbe Elektromedizin GmbH Waldhoernlestrasse 17 72072 Tuebingen, Germany Maßstab: 1:1 Volumen: Gewicht: Ersteller: Prüfer und Freigeber: N/A N/A Datum: 07.09.2023 JWAHL siehe PDF-Stempel siehe PDF-Stempel Elektromedizin GmbH Schrift/Font: Calibri (prefered) Arial (alternative) Symbols: ISO 7000 115 P1 = 200 bar / 2900 psi P2 = 5 bar / 72.5 psi 20134-005 JIS B 8246 A1 W22 R Größe/Size: 9 pt P1 = 200 bar / 2900 psi P2 = 5 bar / 72.5 psi JIS B 8246 A1 W22 R 11,5 20134-005 Titel: Label Druckminderer 20134-005 Techn. Daten Dokumentnummer: 174012 Dokumentklasse: Produktkennzeichung Sprache: DE Name: Version: 005 ÄM-Nr. 25030 Blatt: 1 / 1
=== DOKUMENT: 20134-005-1.pdf ===
--- SEITE 1 ---
KABEL PO VYZKOUŠENÍ ODPOJIT A VLOŽIT DO SÁČKU
SPOLEČNĚ S VÝROBKEM
DISCONNECT CABLE AFTER TESTING AND PUT IT INTO
THE BAG TOGETHER WITH REGULATOR [X] 03
DÉLKA KABELU 100 cm
LENGTH OF CABLE 100 cm [X] 03
56
[X] 05 2
1
[X]
JIS B 8246 A1 W22 R W22x14 [X]
[X] 5 03
DÉLKA HADICE 100 cm
LENGTH OF HOSE 100 cm [X] 03
NA KRABICI LEPIT ŠTÍTEK POZ. 9; ŠTÍTEK JE ULOŽEN NA ŠABLONĚ "EAN CODE" [X] PUT THE LABLE POS. 9; LABLE IS SAVED UNDER TEMPLATE "EAN CODE"
[X] [X] HOTOVÝ VENTIL POZ 1 BALIT DLE Č.V. 397303x
COMPLETE VALVE ITEM 1 PACK ACCORDING TO DRAWING No. 397303x
PRO KAZDE HROMADNE BALENI TISKNOUT 1 KS COM017547, [X] [X] DO DOKUMENTU DOPSAT DATUM BALENI A CISLO DILENSKE OBJEDNAVKY.
[X] [X] FOR EACH BULK PACKAGING PRINT 1 PCE OF COM017547,
WRITE DATE OF PACKAGING AND LOT NUMBER. 04 100 03 05 3 ŠTÍTEK POZICOVAT TÍMTO MÍSTEM K OSE VENTILU LABEL POSITIONED BY THIS PLACE TO REGULATOR AXIS POZICOVAT NAD ZNAČENÍ, ABY ZNAČENÍ NEZAKRÝVAL POSITIONED ABOVE MARKING SO IT DOES NOT COVER IT 8 05 26.11.2025 CHANGE GAUGE & SENSOR / ZMĚNA MĚŘIDLA A SNÍMAČE ECN-14832 S.Kavin Kumar Index Datum Popis / Description Č. změny / No.of change Autor Polotovar Raw material Materiál Material Komentář Notice Rozměr polotovaru Dim. of raw material Materiál Material Reference to ISO 10524-1-2018 Datum vypracování Opracování / Machining Creation date Vypracoval Created Kontroloval Inspected Schválil Approved Klasifikace Item Class Ra Měřítko / Scale 1:1 17.08.2023 S.Kavin Kumar Beran J Ing.K.Zmek B: Standard Kritický rozměr značen Critical dimension marked KR Netol.rozměry / Dim. without tol. ISO 2768 m,K -0,1 -0,3 +0,3 +0,1 Povrchová úprava Surface finish Starý výkres Old drawing Hmotnost Weight 0.858 0724266 Sheet / Number of sheets 1 /1 MR II AR W22x14 RECTUS PT S ERBE,200BAR,5BAR,BLACK,RIGHT,DD,PT 20134-005 List / Počet listů [ ]
=== DOKUMENT: 20134-005_SLV.pdf ===
--- SEITE 1 ---
[X] [X] [X] [X]
[X]
=== DOKUMENT: D111190_DE_002.pdf ===
--- SEITE 1 ---
Label Ausdruck/Rückläufer
Fa. GCE
