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

12/19 1 2 3 4 Weitergabe sowie Vervielfältigung dieses Dokuments, Verwertung und Mitteilung seines Inhalts sind verboten, soweit nicht ausdrücklich gestattet. Zuwiderhandlungen verpflichten zum Schadenersatz. Alle Rechte für den Fall der Patent-, Gebrauchsmuster- oder Geschmackmustereintragung vorbehalten. A B Company Logo, Color: Pantone Process Cyan C Schrift/Font: Calibri (prefered) Symbols: ISO 7000 Arial (alternative) 115 11,5 [X] Erbe Elektromedizin GmbH Waldhoernlestrasse 17 72072 Tuebingen, Germany [X] [X] [X] 20134-005 [X] JIS B 8246 A1 W22 R P1 = 200 bar / 2900 psi P2 = 5 bar / 72.5 psi Größe/Size: 5 pt Größe/Size: 9 pt C D [X] Erbe Elektromedizin GmbH Waldhoernlestrasse 17 72072 Tuebingen, Germany [X] [X] [X] 20134-005 [X] JIS B 8246 A1 W22 R P1 = 200 bar / 2900 psi P2 = 5 bar / 72.5 psi E Material: N/A Maßstab: Volumen: Gewicht: 1:1 N/A N/A Datum: [X] Name: [X] Titel: Label Druckminderer 20134-005 Techn. Daten F Toleranzen: ISO 8015 Allgemeintoleranzen: Vollständige Spezifikation zusammen mit 3D-Datensatz: N/A Alle Merkmale mit * wurden in dieser Version geändert. Alle Maße in mm N/A = Prüfmaß Ersteller: Prüfer und Freigeber: Elektromedizin GmbH 07.09.2023 JWAHL siehe PDF-Stempel siehe PDF-Stempel Dokumentnummer: Dokumentklasse: Sprache: 174012 Produktkennzeichung DE Status: siehe ERBE-PLM Blattgröße: A4 Version: ÄM-Nr. Blatt: 005 25030 1 / 1 KABEL PO VYZKOUŠENÍ ODPOJIT A VLOŽIT DO SÁČKU SPOLEČNĚ S VÝROBKEM DISCONNECT CABLE AFTER TESTING AND PUT IT INTO THE BAG TOGETHER WITH REGULATOR [X] 03 3 DÉLKA KABELU 100 cm LENGTH OF CABLE 100 cm [X] 03 ŠTÍTEK POZICOVAT TÍMTO MÍSTEM K OSE VENTILU LABEL POSITIONED BY THIS PLACE TO REGULATOR AXIS 56 [X] 05 2 1 [X] 03 W22 R JIS B A1 8246 W22x14 [X] POSITIONED ABOVE MARKING SO IT DOES NOT COVER IT POZICOVAT NAD ZNAČENÍ, ABY ZNAČENÍ NEZAKRÝVAL 8 5 [X] 05 DÉLKA HADICE 100 cm LENGTH OF HOSE 100 cm [X] 03 100 HOTOVÝ VENTIL POZ 1 BALIT DLE Č.V. 397303x COMPLETE VALVE ITEM 1 PACK ACCORDING TO DRAWING No. 397303x NA KRABICI LEPIT ŠTÍTEK POZ. 9; ŠTÍTEK JE ULOŽEN NA ŠABLONĚ "EAN CODE" PUT THE LABLE POS. 9; LABLE IS SAVED UNDER TEMPLATE "EAN CODE" PRO KAZDE HROMADNE BALENI TISKNOUT 1 KS COM017547, DO DOKUMENTU DOPSAT DATUM BALENI A CISLO DILENSKE OBJEDNAVKY. FOR EACH BULK PACKAGING PRINT 1 PCE OF COM017547, [X] 04 [X] 03 Polotovar Raw material Materiál Material Komentář Notice Datum vypracování Creation date Vypracoval Created Kontroloval Inspected Schválil Approved Klasifikace Item Class Index 05 26.11.2025 Reference to ISO 10524-1-2018 Datum 17.08.2023 S.Kavin Kumar Beran J Ing.K.Zmek B: Standard CHANGE GAUGE & SENSOR / ZMĚNA MĚŘIDLA A SNÍMAČE Opracování / Machining Rozměr polotovaru Dim. of raw material Materiál Material Měřítko / Scale 1:1 Ra Kritický rozměr značen Critical dimension marked Netol.rozměry / Dim. without tol. ISO 2768 m,K Popis / Description [X] -0,1 -0,3 [X] [X] +0,3 +0,1 KR Povrchová úprava Surface finish Starý výkres Old drawing ERBE,200BAR,5BAR,BLACK,RIGHT,DD,PT MR II AR W22x14 RECTUS PT S 0724266 20134-005 Č. změny / No.of change ECN-14832 List / Počet listů Sheet / Number of sheets 1 /1 S.Kavin Kumar Hmotnost Weight Autor [X] 0.858 [X] WRITE DATE OF PACKAGING AND LOT NUMBER. [ ] [X] Erbe Elektromedizin GmbH Waldhoernlestrasse 17 72072 Tuebingen, Germany [X] [X] [X] 20134-005 [X] JIS B 8246 A1 W22 R P1 = 200 bar / 2900 psi P2 = 5 bar / 72.5 psi Label Ausdruck/Rückläufer Fa. GCE
