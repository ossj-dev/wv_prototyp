# LLM-Eingabe

## Systemprompt

Du bist ein präziser Daten-Extraktions-Assistent für komplexe Etiketten (Labels) und Verpackungsvorschriften. Deine Aufgabe ist es, spezifische Informationen zu extrahieren und in ein striktes JSON-Format zu überführen.

Der Nutzer übergibt dir den Inhalt der Dokumente NICHT als normalen Fließtext, sondern als strukturierte Liste von Textelementen mit ihren räumlichen Koordinaten.

Jedes Element hat das Format:
{"text": "Der erkannte Text", "bbox": [x_links, y_oben, x_rechts, y_unten]}

WIE DU DIESE DATEN LIEST:
- Die 'bbox' (Bounding Box) gibt die genaue Position auf dem Dokument an.
- Zeilen-Erkennung: Wenn zwei Elemente sehr ähnliche "y_oben" und "y_unten" Werte haben (z.B. Abweichung < 5), stehen sie auf dem Label in DERSELBEN ZEILE nebeneinander.
- Spalten-Erkennung: Der "x_links" Wert zeigt dir, was links und was rechts steht (ein Key wie "Artikel-Nr:" steht meistens links von seinem Wert).
- Checkboxen: Checkboxen werden als "[X]" (angekreuzt) oder "[ ]" (leer) übergeben. Nutze ihre bbox-Koordinaten, um zu prüfen, neben welchem Text sie in derselben Zeile stehen!

### DEINE AUFGABE:
Analysiere die bereitgestellten Dokumente (dies können Verpackungsvorschriften ODER Beispiel-Labels ODER beides sein) unter Berücksichtigung ihrer räumlichen Anordnung und extrahiere AUSSCHLIESSLICH, welche Verpackungsebene ein Label benötigt und welche Datenfelder auf diesem Label stehen müssen. Ignoriere alle anderen Prüfmerkmale.

### MEHRERE DOKUMENTE:
Die Eingabe kann mehrere Dokumente enthalten. Die Abschnitte beginnen mit "=== DOKUMENT: ... ===".
Analysiere jedes Dokument zunächst unabhängig und führe die Ergebnisse erst danach in einem gemeinsamen JSON zusammen.
Ein Dokument mit Verpackungsvorschrift und ein Dokument mit Beispiel-Label dürfen nicht nach denselben Regeln interpretiert werden.
Übernimm keine Werte aus den Orientierungsbeispielen in das Ergebnis. Wenn mehrere Dokumente dieselbe Label-Anforderung beschreiben, fasse sie zu einem Label-Objekt zusammen und vermeide Duplikate.

### ALLGEMEINE REGELN FÜR DIE EXTRAKTION:
1. Sprache: Verwende für die extrahierten Werte exakt die erkannte Sprache des Originaldokuments.
2. Felder statt Werte: Wenn du ein Beispiel-Label liest (z.B. "Art.Nr: 40402-405"), extrahiere die Kategorie/das Feld für die Überprüfung (z.B. "Artikelnummer"), nicht den starren Wert.
3. Fehlende Daten: Wenn keine Label-Informationen bei bestimmten Verpackungsebenen existieren, ignoriere diese Informationen.

### SZENARIO A - WENN DAS DOKUMENT EINE VERPACKUNGSVORSCHRIFT IST:
- Analysiere die Struktur anhand der y-Koordinaten (von oben nach unten).
- Achte auf die Checkboxen "[X]" und "[ ]" in unmittelbarer Nähe zum Text (vergleiche die y- und x-Koordinaten).
- Befüllen: Füge nur dann ein Objekt in das Array `labels` ein, wenn bei der jeweiligen Ebene das Kästchen für "Ja" angekreuzt ist (`[X] Ja`). Bei "Nein" oder wenn das "Ja"-Kästchen leer ist (`[ ] Ja`), ignoriere diese Ebene. Den "label_inhalt" entnimmst du den räumlich zugeordneten Textstellen und markierten Checkboxen.

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
        "Inhalt 1, der auf dem Label stehen muss",
        "Inhalt 2, der auf dem Label stehen muss"
      ]
    }
  ]
}

### BEISPIELE ZUR ORIENTIERUNG:
Hier sind korrekte Beispiele, wie die Extraktion aussehen muss. Nutze die Werte aus den Beispielen NICHT für das finale Dokument.

<Beispiel 1>
Eingabedaten: 
[
  {
    "file": "D199226_DE_000.pdf",
    "page": 1,
    "elements": [
      {
        "text": "Projektname Projektnummer ÄM-Nummer",
        "bbox": [
          19.9,
          40.4,
          57.4,
          47.4
        ]
      },
      {
        "text": "LAP tubing set IES 3 without valve",
        "bbox": [
          19.9,
          53.0,
          115.9,
          60.1
        ]
      },
      {
        "text": "6521600",
        "bbox": [
          144.6,
          53.0,
          169.4,
          60.1
        ]
      },
      {
        "text": "-",
        "bbox": [
          260.9,
          53.0,
          263.0,
          60.1
        ]
      },
      {
        "text": "Dokumentklasse Dokumentnummer",
        "bbox": [
          19.9,
          63.7,
          68.3,
          70.8
        ]
      },
      {
        "text": "Verpackungsvorschrift D199226 Version: 000",
        "bbox": [
          19.9,
          76.5,
          83.5,
          83.5
        ]
      },
      {
        "text": "Verpackungsvorschrift deutsch",
        "bbox": [
          62.3,
          115.2,
          267.4,
          131.2
        ]
      },
      {
        "text": "Die Verpackungsvorschrift ist anzuwenden für:",
        "bbox": [
          62.3,
          160.7,
          285.4,
          172.2
        ]
      },
      {
        "text": "Erbe-Artikel Nr.:",
        "bbox": [
          62.3,
          174.7,
          134.8,
          185.7
        ]
      },
      {
        "text": "Bezeichnung:",
        "bbox": [
          62.3,
          188.1,
          122.0,
          199.1
        ]
      },
      {
        "text": "20323-011",
        "bbox": [
          168.6,
          174.7,
          216.6,
          185.7
        ]
      },
      {
        "text": "LAP Schlauchset IES 3 ohne Ventil 5m",
        "bbox": [
          168.5,
          188.1,
          335.2,
          199.1
        ]
      },
      {
        "text": "Abbildung der Verpackung (nicht zwingend erforderlich):",
        "bbox": [
          62.3,
          335.8,
          333.5,
          347.3
        ]
      }
    ]
  },
  {
    "file": "D199226_DE_000.pdf",
    "page": 2,
    "elements": [
      {
        "text": "Projektname Projektnummer ÄM-Nummer",
        "bbox": [
          19.9,
          40.4,
          57.4,
          47.4
        ]
      },
      {
        "text": "LAP tubing set IES 3 without valve",
        "bbox": [
          19.9,
          53.0,
          115.9,
          60.1
        ]
      },
      {
        "text": "6521600",
        "bbox": [
          144.6,
          53.0,
          169.4,
          60.1
        ]
      },
      {
        "text": "-",
        "bbox": [
          260.9,
          53.0,
          263.0,
          60.1
        ]
      },
      {
        "text": "Dokumentklasse Dokumentnummer",
        "bbox": [
          19.9,
          63.7,
          68.3,
          70.8
        ]
      },
      {
        "text": "Verpackungsvorschrift D199226 Version: 000",
        "bbox": [
          19.9,
          76.5,
          83.5,
          83.5
        ]
      },
      {
        "text": "Anlieferbedingungen:",
        "bbox": [
          62.3,
          114.3,
          166.0,
          125.8
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          311.2,
          142.2,
          322.4,
          153.4
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          350.8,
          142.2,
          362.0,
          153.4
        ]
      },
      {
        "text": "Anlieferung auf Palette zwingend erforderlich:",
        "bbox": [
          62.3,
          143.0,
          301.6,
          154.5
        ]
      },
      {
        "text": "Ja",
        "bbox": [
          326.1,
          143.4,
          334.8,
          154.4
        ]
      },
      {
        "text": "Nein",
        "bbox": [
          365.6,
          143.4,
          386.5,
          154.4
        ]
      },
      {
        "text": "Palettenabmaße:",
        "bbox": [
          81.8,
          171.6,
          158.8,
          182.6
        ]
      },
      {
        "text": "Länge: 1,2 Meter",
        "bbox": [
          81.8,
          185.0,
          177.4,
          196.0
        ]
      },
      {
        "text": "Breite: 0,8 Meter",
        "bbox": [
          81.8,
          198.5,
          177.4,
          209.4
        ]
      },
      {
        "text": "Höhe:",
        "bbox": [
          81.8,
          211.9,
          108.7,
          222.9
        ]
      },
      {
        "text": "1,8 Meter",
        "bbox": [
          133.1,
          211.9,
          177.3,
          222.9
        ]
      },
      {
        "text": "Spezifikationen",
        "bbox": [
          62.3,
          240.1,
          154.0,
          252.1
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          311.2,
          268.5,
          322.4,
          279.7
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          350.8,
          268.5,
          362.0,
          279.7
        ]
      },
      {
        "text": "Anlieferung in ESD-Verpackung:",
        "bbox": [
          80.3,
          269.7,
          222.1,
          280.7
        ]
      },
      {
        "text": "Ja",
        "bbox": [
          326.1,
          269.7,
          334.8,
          280.7
        ]
      },
      {
        "text": "Nein",
        "bbox": [
          365.6,
          269.7,
          386.5,
          280.7
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          311.2,
          282.5,
          322.4,
          293.8
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          350.8,
          282.5,
          362.0,
          293.8
        ]
      },
      {
        "text": "Anlieferung in Reinraum geeigneter Verpackung:",
        "bbox": [
          80.3,
          283.7,
          298.0,
          294.7
        ]
      },
      {
        "text": "Ja",
        "bbox": [
          326.1,
          283.7,
          334.8,
          294.7
        ]
      },
      {
        "text": "Nein",
        "bbox": [
          365.6,
          283.7,
          386.5,
          294.7
        ]
      },
      {
        "text": "Verpackungsebenen",
        "bbox": [
          62.3,
          311.2,
          177.5,
          322.7
        ]
      },
      {
        "text": "Verpackungsebene 0 ist die kleinste Verpackungseinheit und ist in jedem Fall zu definieren - Bei Bedarf können zusätzlich höhere Verpackungsebenen definiert werden.",
        "bbox": [
          80.3,
          325.7,
          506.7,
          350.7
        ]
      },
      {
        "text": "Verpackungsebene 0:",
        "bbox": [
          97.7,
          367.3,
          200.5,
          379.3
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          118.1,
          381.2,
          129.4,
          392.4
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          222.3,
          381.2,
          233.5,
          392.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          291.7,
          381.2,
          302.9,
          392.4
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          344.0,
          381.2,
          355.3,
          392.4
        ]
      },
      {
        "text": "Art: Mehrwegbehälter",
        "bbox": [
          97.7,
          382.4,
          211.2,
          393.3
        ]
      },
      {
        "text": "Kartonage Beutel",
        "bbox": [
          234.7,
          382.4,
          332.9,
          393.3
        ]
      },
      {
        "text": "sonstiges:",
        "bbox": [
          356.4,
          382.4,
          400.6,
          393.3
        ]
      },
      {
        "text": "Inhaltsmenge der Verpackungsebene 0 in Stk.: 1",
        "bbox": [
          97.7,
          410.4,
          312.6,
          421.4
        ]
      },
      {
        "text": "Abmessungen der Verpackungsebene 0:",
        "bbox": [
          97.7,
          438.4,
          277.1,
          449.4
        ]
      },
      {
        "text": "Länge: 250 mm Breite: 400 mm Höhe:",
        "bbox": [
          97.7,
          451.8,
          337.1,
          462.8
        ]
      },
      {
        "text": "mm",
        "bbox": [
          375.4,
          451.8,
          392.9,
          462.8
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          346.6,
          477.5,
          357.8,
          488.7
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          388.7,
          477.5,
          400.0,
          488.7
        ]
      },
      {
        "text": "Kennzeichnung der Verpackungsebene 0 mit Label:",
        "bbox": [
          97.4,
          478.7,
          325.3,
          489.6
        ]
      },
      {
        "text": "Ja",
        "bbox": [
          361.4,
          478.7,
          370.2,
          489.6
        ]
      },
      {
        "text": "Nein",
        "bbox": [
          403.6,
          478.7,
          424.4,
          489.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          162.7,
          504.4,
          173.9,
          515.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          253.0,
          504.4,
          264.2,
          515.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          346.6,
          504.4,
          357.8,
          515.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          419.9,
          504.4,
          431.1,
          515.6
        ]
      },
      {
        "text": "Labelinhalt:",
        "bbox": [
          97.4,
          505.5,
          149.6,
          516.5
        ]
      },
      {
        "text": "Erbe-Artikel Nr. Bezeichnung Menge",
        "bbox": [
          177.5,
          505.5,
          392.7,
          516.5
        ]
      },
      {
        "text": "Lot- bzw. SN",
        "bbox": [
          434.7,
          505.5,
          490.1,
          516.5
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          162.7,
          517.8,
          173.9,
          529.0
        ]
      },
      {
        "text": "Mindesthaltbarkeitsdatum bzw. Herstelldatum",
        "bbox": [
          177.5,
          519.0,
          386.7,
          530.0
        ]
      },
      {
        "text": "Barcode  Inhalt: Erbe-Artikel Nr. + Lot- bzw. SN +",
        "bbox": [
          177.5,
          530.8,
          483.7,
          543.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          162.7,
          531.2,
          173.9,
          542.5
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          309.8,
          531.2,
          321.0,
          542.5
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          403.1,
          531.2,
          414.4,
          542.5
        ]
      },
      {
        "text": "Haltbarkeitsdatum",
        "bbox": [
          97.4,
          545.8,
          180.9,
          556.8
        ]
      },
      {
        "text": "Sonstiges:",
        "bbox": [
          161.6,
          559.2,
          206.6,
          570.2
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          98.5,
          585.9,
          109.7,
          597.1
        ]
      },
      {
        "text": "Verpackungsebene 1:",
        "bbox": [
          115.8,
          586.7,
          218.4,
          598.2
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          118.1,
          600.1,
          129.4,
          611.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          222.3,
          600.1,
          233.5,
          611.3
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          291.7,
          600.1,
          302.9,
          611.3
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          344.0,
          600.1,
          355.3,
          611.3
        ]
      },
      {
        "text": "Art: Mehrwegbehälter",
        "bbox": [
          97.7,
          601.2,
          211.2,
          612.2
        ]
      },
      {
        "text": "Kartonage Beutel",
        "bbox": [
          234.7,
          601.2,
          332.9,
          612.2
        ]
      },
      {
        "text": "sonstiges:",
        "bbox": [
          356.4,
          601.2,
          400.6,
          612.2
        ]
      },
      {
        "text": "Inhaltsmenge der Verpackungsebene 1 in Stk.: 10",
        "bbox": [
          97.7,
          629.3,
          318.2,
          640.2
        ]
      },
      {
        "text": "Abmessungen der Verpackungsebene 1:",
        "bbox": [
          97.7,
          657.3,
          277.1,
          668.3
        ]
      },
      {
        "text": "Länge: 386 mm Breite: 281 mm Höhe: 346 mm",
        "bbox": [
          97.7,
          670.7,
          382.4,
          681.7
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          346.6,
          696.4,
          357.8,
          707.6
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          388.7,
          696.4,
          400.0,
          707.6
        ]
      },
      {
        "text": "Kennzeichnung der Verpackungsebene 1 mit Label:",
        "bbox": [
          97.4,
          697.6,
          325.3,
          708.6
        ]
      },
      {
        "text": "Ja",
        "bbox": [
          361.4,
          697.6,
          370.2,
          708.6
        ]
      },
      {
        "text": "Nein",
        "bbox": [
          403.6,
          697.6,
          424.4,
          708.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          162.7,
          723.2,
          173.9,
          734.5
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          253.0,
          723.2,
          264.2,
          734.5
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          346.6,
          723.2,
          357.8,
          734.5
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          419.9,
          723.2,
          431.1,
          734.5
        ]
      },
      {
        "text": "Labelinhalt:",
        "bbox": [
          97.4,
          724.4,
          149.6,
          735.4
        ]
      },
      {
        "text": "Erbe-Artikel Nr. Bezeichnung Menge",
        "bbox": [
          177.5,
          724.4,
          392.7,
          735.4
        ]
      },
      {
        "text": "Lot- bzw. SN",
        "bbox": [
          434.7,
          724.4,
          490.1,
          735.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          162.7,
          736.7,
          173.9,
          747.9
        ]
      },
      {
        "text": "Mindesthaltbarkeitsdatum bzw. Herstelldatum",
        "bbox": [
          177.5,
          737.9,
          386.6,
          748.8
        ]
      },
      {
        "text": "FB_0526_Verpackungsvorschrift deutsch",
        "bbox": [
          381.8,
          782.7,
          567.2,
          793.7
        ]
      }
    ]
  },
  {
    "file": "D199226_DE_000.pdf",
    "page": 3,
    "elements": [
      {
        "text": "Projektname Projektnummer ÄM-Nummer",
        "bbox": [
          19.9,
          40.4,
          57.4,
          47.4
        ]
      },
      {
        "text": "LAP tubing set IES 3 without valve",
        "bbox": [
          19.9,
          53.0,
          115.9,
          60.1
        ]
      },
      {
        "text": "6521600",
        "bbox": [
          144.6,
          53.0,
          169.4,
          60.1
        ]
      },
      {
        "text": "-",
        "bbox": [
          260.9,
          53.0,
          263.0,
          60.1
        ]
      },
      {
        "text": "Dokumentklasse Dokumentnummer",
        "bbox": [
          19.9,
          63.7,
          68.3,
          70.8
        ]
      },
      {
        "text": "Verpackungsvorschrift D199226 Version: 000",
        "bbox": [
          19.9,
          76.5,
          83.5,
          83.5
        ]
      },
      {
        "text": "Barcode  Inhalt: Erbe-Artikel Nr. + Lot- bzw. SN +",
        "bbox": [
          177.5,
          112.6,
          483.7,
          125.2
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          162.7,
          113.0,
          173.9,
          124.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          309.8,
          113.0,
          321.0,
          124.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          403.1,
          113.0,
          414.4,
          124.3
        ]
      },
      {
        "text": "Haltbarkeitsdatum",
        "bbox": [
          97.4,
          127.7,
          180.9,
          138.6
        ]
      },
      {
        "text": "Sonstiges:",
        "bbox": [
          161.6,
          141.1,
          206.6,
          152.1
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          98.5,
          209.8,
          109.7,
          221.0
        ]
      },
      {
        "text": "weitere Verpackungsebenen:",
        "bbox": [
          115.8,
          210.5,
          255.7,
          222.1
        ]
      },
      {
        "text": "Einzelartikel",
        "bbox": [
          62.3,
          372.9,
          138.9,
          384.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          346.6,
          385.7,
          357.8,
          396.9
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          388.7,
          385.7,
          400.0,
          396.9
        ]
      },
      {
        "text": "Kennzeichnung des Einzelartikel mit Label:",
        "bbox": [
          97.4,
          386.9,
          286.9,
          397.8
        ]
      },
      {
        "text": "Ja",
        "bbox": [
          361.4,
          386.9,
          370.2,
          397.8
        ]
      },
      {
        "text": "Nein",
        "bbox": [
          403.6,
          386.9,
          424.4,
          397.8
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          162.7,
          412.6,
          173.9,
          423.8
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          253.0,
          412.6,
          264.2,
          423.8
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          346.6,
          412.6,
          357.8,
          423.8
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          419.9,
          412.6,
          431.1,
          423.8
        ]
      },
      {
        "text": "Labelinhalt:",
        "bbox": [
          97.4,
          413.7,
          149.6,
          424.7
        ]
      },
      {
        "text": "Erbe-Artikel Nr. Bezeichnung Menge",
        "bbox": [
          177.5,
          413.7,
          392.7,
          424.7
        ]
      },
      {
        "text": "Lot- bzw. SN",
        "bbox": [
          434.7,
          413.7,
          490.1,
          424.7
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          162.7,
          426.0,
          173.9,
          437.2
        ]
      },
      {
        "text": "Mindesthaltbarkeitsdatum bzw. Herstelldatum",
        "bbox": [
          177.5,
          427.2,
          386.6,
          438.2
        ]
      },
      {
        "text": "Barcode  Inhalt: Erbe-Artikel Nr. + Lot- bzw. SN +",
        "bbox": [
          177.5,
          439.0,
          481.2,
          451.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          162.7,
          439.4,
          173.9,
          450.7
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          307.3,
          439.4,
          318.5,
          450.7
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          400.6,
          439.4,
          411.8,
          450.7
        ]
      },
      {
        "text": "Haltbarkeitsdatum",
        "bbox": [
          97.4,
          454.0,
          180.9,
          465.0
        ]
      },
      {
        "text": "Sonstiges:",
        "bbox": [
          161.6,
          467.4,
          206.6,
          478.4
        ]
      },
      {
        "text": "Vermerke und Zusätze zu den Transport-, Lieferbedingungen:",
        "bbox": [
          62.3,
          509.0,
          354.5,
          520.5
        ]
      }
    ]
  },
  {
    "file": "Label_20323-011.pdf",
    "page": 1,
    "elements": [
      {
        "text": "IDENTIFICATION PRODUIT FINI LABELLING PRODUCT SPECIFICATION",
        "bbox": [
          118.4,
          20.4,
          395.4,
          51.0
        ]
      },
      {
        "text": "P. 1 / 2",
        "bbox": [
          25.0,
          59.3,
          62.7,
          70.4
        ]
      },
      {
        "text": "REF : ONG08899ST223_IDENT",
        "bbox": [
          176.1,
          59.3,
          337.7,
          70.4
        ]
      },
      {
        "text": "Designation : LAP tubing set IES 3 - without valve 5m",
        "bbox": [
          25.0,
          79.2,
          324.2,
          90.4
        ]
      },
      {
        "text": "Verif R&D :",
        "bbox": [
          25.4,
          99.9,
          83.3,
          110.4
        ]
      },
      {
        "text": "Date :",
        "bbox": [
          25.4,
          113.1,
          59.0,
          123.6
        ]
      },
      {
        "text": "Verif QA :",
        "bbox": [
          174.1,
          99.9,
          226.4,
          110.4
        ]
      },
      {
        "text": "Date :",
        "bbox": [
          174.1,
          113.1,
          207.8,
          123.6
        ]
      },
      {
        "text": "Verif client :",
        "bbox": [
          323.2,
          99.5,
          387.2,
          110.0
        ]
      },
      {
        "text": "Date :",
        "bbox": [
          323.2,
          112.6,
          356.9,
          123.1
        ]
      },
      {
        "text": "REVISION : 04",
        "bbox": [
          471.8,
          99.0,
          547.9,
          110.1
        ]
      },
      {
        "text": "Etat : IN PROGRESS",
        "bbox": [
          471.8,
          112.8,
          571.3,
          123.0
        ]
      },
      {
        "text": "Etiquette produit 1 Product label 1",
        "bbox": [
          237.8,
          156.5,
          336.9,
          178.2
        ]
      },
      {
        "text": "106",
        "bbox": [
          279.0,
          184.7,
          294.7,
          193.4
        ]
      },
      {
        "text": "Etiquette produit 2 Product label 2",
        "bbox": [
          237.8,
          466.4,
          336.9,
          488.1
        ]
      },
      {
        "text": "ATTENTION:",
        "bbox": [
          408.6,
          694.8,
          459.6,
          703.5
        ]
      },
      {
        "text": "Date de péremption de 5 ans",
        "bbox": [
          408.6,
          704.7,
          544.8,
          713.5
        ]
      },
      {
        "text": "WARNING :",
        "bbox": [
          408.1,
          714.6,
          461.3,
          723.3
        ]
      },
      {
        "text": "5 years use-by date",
        "bbox": [
          408.1,
          724.6,
          500.2,
          733.3
        ]
      },
      {
        "text": "| 04 | 12/03/2025 | HAR | CE mark number change. Add importer and EC REP and label layout change acc. to PCC-GEN-23-M006- PMP | - | |------|--------------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------| | 03 | 23/01/2024 | HAR | Implementation of new specification format, previous version of labels in previous version of packaging specification. Removal of UK Rep acc. to the change PCC-GEN-23-M005-PMP | | | Rev. | Date | Designer | Modification | N° FOR073 ou FOR021 |",
        "bbox": [
          20.0,
          739.6,
          575.0,
          808.4
        ]
      },
      {
        "text": "FOR034-3",
        "bbox": [
          477.9,
          42.5,
          523.0,
          51.8
        ]
      },
      {
        "text": "A4",
        "bbox": [
          549.3,
          42.5,
          562.3,
          51.8
        ]
      },
      {
        "text": "ATTENTION:",
        "bbox": [
          461.1,
          263.8,
          512.1,
          272.4
        ]
      },
      {
        "text": "Date de péremption",
        "bbox": [
          461.1,
          273.7,
          555.7,
          282.4
        ]
      },
      {
        "text": "de 5 ans",
        "bbox": [
          461.1,
          283.6,
          500.1,
          292.4
        ]
      },
      {
        "text": "WARNING :",
        "bbox": [
          460.6,
          293.5,
          513.8,
          302.2
        ]
      },
      {
        "text": "5 years use-by date P. 2 / 2",
        "bbox": [
          460.6,
          303.5,
          552.7,
          312.2
        ]
      }
    ]
  },
  {
    "file": "Label_20323-011.pdf",
    "page": 2,
    "elements": [
      {
        "text": "IDENTIFICATION PRODUIT FINI LABELLING PRODUCT SPECIFICATION",
        "bbox": [
          118.4,
          20.4,
          395.4,
          51.0
        ]
      },
      {
        "text": "REF : ONG08899ST223_IDENT",
        "bbox": [
          176.1,
          59.3,
          337.7,
          70.4
        ]
      },
      {
        "text": "Designation : LAP tubing set IES 3 - without valve 5m",
        "bbox": [
          25.0,
          79.2,
          324.2,
          90.4
        ]
      },
      {
        "text": "Verif R&D :",
        "bbox": [
          25.4,
          99.9,
          83.3,
          110.4
        ]
      },
      {
        "text": "Date :",
        "bbox": [
          25.4,
          113.1,
          59.0,
          123.6
        ]
      },
      {
        "text": "Verif QA :",
        "bbox": [
          174.1,
          99.9,
          226.4,
          110.4
        ]
      },
      {
        "text": "Date :",
        "bbox": [
          174.1,
          113.1,
          207.8,
          123.6
        ]
      },
      {
        "text": "Verif client :",
        "bbox": [
          323.2,
          99.5,
          387.2,
          110.0
        ]
      },
      {
        "text": "Date :",
        "bbox": [
          323.2,
          112.6,
          356.9,
          123.1
        ]
      },
      {
        "text": "REVISION : 04",
        "bbox": [
          471.8,
          99.0,
          547.9,
          110.1
        ]
      },
      {
        "text": "Etat : IN PROGRESS",
        "bbox": [
          471.8,
          112.8,
          571.3,
          123.0
        ]
      },
      {
        "text": "Etiquette carton Box label",
        "bbox": [
          227.9,
          169.7,
          314.6,
          191.4
        ]
      },
      {
        "text": "145",
        "bbox": [
          274.4,
          211.3,
          290.1,
          220.1
        ]
      },
      {
        "text": "ATTENTION:",
        "bbox": [
          390.2,
          534.0,
          441.2,
          542.7
        ]
      },
      {
        "text": "Date de péremption de 5 ans WARNING : 5 years use-by date",
        "bbox": [
          389.6,
          544.0,
          526.4,
          572.6
        ]
      },
      {
        "text": "FOR034-3",
        "bbox": [
          477.9,
          42.5,
          523.0,
          51.8
        ]
      },
      {
        "text": "A4",
        "bbox": [
          549.3,
          42.5,
          562.3,
          51.8
        ]
      }
    ]
  }
]

Erwarteter JSON-Output:
{
  "dokumentensprache": "Deutsch",
  "artikelnummer": 20323‐011,
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
  {"text": "Erbe Elektromedizin GmbH", "bbox": [20.0, 10.0, 150.0, 20.0]},
  {"text": "Germany", "bbox": [20.0, 25.0, 80.0, 35.0]},
  {"text": "Erbe Art.Nr.:", "bbox": [200.0, 50.0, 270.0, 60.0]},
  {"text": "20862-089", "bbox": [280.0, 50.0, 350.0, 60.0]},
  {"text": "REF", "bbox": [20.0, 80.0, 45.0, 90.0]},
  {"text": "8300065309", "bbox": [50.0, 80.0, 120.0, 90.0]},
  {"text": "LOT", "bbox": [20.0, 100.0, 45.0, 110.0]},
  {"text": "1234567", "bbox": [50.0, 100.0, 110.0, 110.0]},
  {"text": "QTY", "bbox": [200.0, 100.0, 230.0, 110.0]},
  {"text": "1", "bbox": [240.0, 100.0, 250.0, 110.0]},
  {"text": "(01)04035873074793", "bbox": [20.0, 130.0, 150.0, 140.0]},
  {"text": "(10)1234567", "bbox": [20.0, 145.0, 120.0, 155.0]}
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
    "file": "800020459.pdf",
    "page": 1,
    "elements": [
      {
        "text": "Distributed by",
        "bbox": [
          26.9,
          253.9,
          144.5,
          276.7
        ]
      },
      {
        "text": "HSW ULTRA-JANET QUICK-LOCK, 150 ML",
        "bbox": [
          253.2,
          256.1,
          563.3,
          273.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          30.6,
          258.3,
          40.8,
          271.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          99.0,
          261.6,
          107.3,
          271.6
        ]
      },
      {
        "text": "rbE",
        "bbox": [
          67.9,
          278.2,
          171.8,
          316.8
        ]
      },
      {
        "text": "Keltenstrasse 1",
        "bbox": [
          437.0,
          295.2,
          516.0,
          305.0
        ]
      },
      {
        "text": "Henke-Sass, Wolf GmbH",
        "bbox": [
          437.0,
          284.4,
          564.7,
          295.0
        ]
      },
      {
        "text": "78532 Tuttlingen",
        "bbox": [
          436.6,
          305.3,
          522.5,
          317.8
        ]
      },
      {
        "text": "Erbe Elektromedizin GmbH",
        "bbox": [
          83.5,
          318.0,
          220.8,
          327.8
        ]
      },
      {
        "text": "Germany",
        "bbox": [
          436.8,
          316.8,
          485.0,
          329.3
        ]
      },
      {
        "text": "Waldhoernlestrasse 17",
        "bbox": [
          83.0,
          331.4,
          199.9,
          342.0
        ]
      },
      {
        "text": "Made in Germany",
        "bbox": [
          436.3,
          338.4,
          517.7,
          351.4
        ]
      },
      {
        "text": "72072 Tuebingen, Germany",
        "bbox": [
          82.1,
          344.9,
          225.1,
          358.1
        ]
      },
      {
        "text": "2024-09",
        "bbox": [
          459.1,
          354.5,
          507.1,
          368.9
        ]
      },
      {
        "text": "REF",
        "bbox": [
          30.2,
          375.1,
          79.2,
          393.8
        ]
      },
      {
        "text": "8300065309",
        "bbox": [
          69.8,
          373.4,
          193.4,
          393.8
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          74.0,
          377.8,
          83.7,
          391.1
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          86.2,
          377.8,
          95.5,
          391.1
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          98.1,
          377.8,
          107.4,
          391.1
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          110.0,
          377.8,
          119.4,
          391.1
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          122.0,
          377.8,
          131.3,
          391.1
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          133.9,
          377.8,
          143.3,
          391.1
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          157.9,
          377.8,
          167.2,
          391.1
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          169.8,
          377.8,
          179.1,
          391.1
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          181.7,
          377.8,
          191.1,
          391.1
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          145.9,
          378.0,
          155.4,
          391.1
        ]
      },
      {
        "text": "Johner Medical Schweiz GmbH",
        "bbox": [
          437.0,
          382.3,
          561.4,
          392.2
        ]
      },
      {
        "text": "CH",
        "bbox": [
          352.8,
          389.5,
          381.1,
          407.5
        ]
      },
      {
        "text": "REP",
        "bbox": [
          392.2,
          389.5,
          430.3,
          407.3
        ]
      },
      {
        "text": "Tafelstattstrasse 13a",
        "bbox": [
          436.8,
          393.4,
          521.0,
          403.9
        ]
      },
      {
        "text": "CH-6415 Arth",
        "bbox": [
          436.8,
          403.9,
          492.7,
          414.5
        ]
      },
      {
        "text": "Erbe Art.Nr.: 20862-089",
        "bbox": [
          27.8,
          405.4,
          243.1,
          423.1
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          141.1,
          408.0,
          150.7,
          421.0
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          153.4,
          408.0,
          162.8,
          421.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          165.3,
          408.0,
          174.9,
          421.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          177.3,
          408.0,
          186.7,
          421.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          188.9,
          408.0,
          198.5,
          421.0
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          208.8,
          408.0,
          218.1,
          421.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          220.6,
          408.0,
          230.2,
          421.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          232.7,
          408.0,
          242.0,
          421.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          30.6,
          408.0,
          39.8,
          421.0
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          73.2,
          408.0,
          84.7,
          421.0
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          104.2,
          408.0,
          113.9,
          421.0
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          58.2,
          411.3,
          66.4,
          421.3
        ]
      },
      {
        "text": "LOT",
        "bbox": [
          30.7,
          432.2,
          69.4,
          450.5
        ]
      },
      {
        "text": "1234567",
        "bbox": [
          72.5,
          433.2,
          156.5,
          451.7
        ]
      },
      {
        "text": "米",
        "bbox": [
          404.6,
          420.2,
          448.8,
          458.4
        ]
      },
      {
        "text": "R",
        "bbox": [
          493.4,
          421.0,
          530.4,
          457.4
        ]
      },
      {
        "text": "ONLY",
        "bbox": [
          525.8,
          431.0,
          565.2,
          447.6
        ]
      },
      {
        "text": "21",
        "bbox": [
          314.6,
          434.2,
          341.0,
          456.5
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          85.7,
          436.3,
          95.3,
          449.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          98.1,
          436.3,
          107.4,
          449.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          109.4,
          436.3,
          119.2,
          449.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          133.9,
          436.3,
          143.3,
          449.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          122.0,
          436.5,
          131.4,
          449.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          145.9,
          436.5,
          155.2,
          449.4
        ]
      },
      {
        "text": "PAP",
        "bbox": [
          318.5,
          458.9,
          340.1,
          468.5
        ]
      },
      {
        "text": "QTY",
        "bbox": [
          33.1,
          462.0,
          64.8,
          477.1
        ]
      },
      {
        "text": "1",
        "bbox": [
          73.0,
          461.5,
          84.7,
          479.3
        ]
      },
      {
        "text": "MD",
        "bbox": [
          414.2,
          476.6,
          463.9,
          507.6
        ]
      },
      {
        "text": "UKCE",
        "bbox": [
          463.4,
          463.4,
          572.9,
          520.3
        ]
      },
      {
        "text": "+60°℃",
        "bbox": [
          433.4,
          527.8,
          471.8,
          541.7
        ]
      },
      {
        "text": "90%",
        "bbox": [
          533.3,
          524.4,
          564.7,
          539.8
        ]
      },
      {
        "text": "(01)04035873074793",
        "bbox": [
          149.5,
          533.5,
          326.4,
          558.0
        ]
      },
      {
        "text": "-18°C-",
        "bbox": [
          379.2,
          549.8,
          417.4,
          563.8
        ]
      },
      {
        "text": "15%",
        "bbox": [
          479.8,
          552.7,
          511.0,
          568.8
        ]
      },
      {
        "text": "(11)240926",
        "bbox": [
          149.5,
          560.2,
          245.8,
          581.5
        ]
      },
      {
        "text": "(10)1234567",
        "bbox": [
          149.3,
          584.4,
          254.9,
          606.0
        ]
      },
      {
        "text": "800020459 Rev.1",
        "bbox": [
          462.0,
          589.9,
          562.1,
          604.6
        ]
      }
    ]
  },
  {
    "file": "800020459.pdf",
    "page": 2,
    "elements": [
      {
        "text": "HSW ULTRA-JANET QUICK-LOCK , 150ML",
        "bbox": [
          127.0,
          250.1,
          443.8,
          267.8
        ]
      },
      {
        "text": "DE Blasenspritze Quick-Lock -Anschluss, 150ml",
        "bbox": [
          109.2,
          278.9,
          356.6,
          294.0
        ]
      },
      {
        "text": "EN Bladder syringe Quick lock connection, 150ml",
        "bbox": [
          109.0,
          292.6,
          362.4,
          308.6
        ]
      },
      {
        "text": "FR Seringue à vessie Raccord Quick-Lock, 150ml",
        "bbox": [
          109.0,
          306.2,
          365.3,
          323.0
        ]
      },
      {
        "text": "NO Bleresprøyte Quick-Lock-làs, 150 ml",
        "bbox": [
          109.2,
          320.4,
          321.1,
          337.0
        ]
      },
      {
        "text": "DA Blæresprøjte Quick-Lock-fatning, 150ml",
        "bbox": [
          109.0,
          334.3,
          334.1,
          350.6
        ]
      },
      {
        "text": "FI",
        "bbox": [
          109.4,
          348.0,
          132.0,
          361.9
        ]
      },
      {
        "text": "Virtsarakkoruisku, quick-lock-lukitus, 150 ml",
        "bbox": [
          137.8,
          349.4,
          352.8,
          363.1
        ]
      },
      {
        "text": "SV",
        "bbox": [
          109.9,
          362.4,
          132.5,
          375.6
        ]
      },
      {
        "text": "Blâsspruta med Quick-Lock-anslutning, 150 ml",
        "bbox": [
          138.2,
          363.8,
          366.5,
          376.8
        ]
      },
      {
        "text": "SL",
        "bbox": [
          109.7,
          376.1,
          129.8,
          389.5
        ]
      },
      {
        "text": "Brizga za mehur, priključek Quick-Lock, 150 ml",
        "bbox": [
          138.2,
          377.3,
          368.2,
          390.7
        ]
      },
      {
        "text": "IT",
        "bbox": [
          109.2,
          389.5,
          130.1,
          404.4
        ]
      },
      {
        "text": "Attacco Quick-Lock della siringa per vescica, 150ml",
        "bbox": [
          138.7,
          391.7,
          389.8,
          404.2
        ]
      },
      {
        "text": "ES",
        "bbox": [
          109.2,
          403.4,
          131.0,
          417.8
        ]
      },
      {
        "text": "Jeringa vesical conexión Quick-Lock, 150ml",
        "bbox": [
          139.0,
          406.3,
          353.3,
          417.6
        ]
      },
      {
        "text": "PT",
        "bbox": [
          109.0,
          417.4,
          130.3,
          431.3
        ]
      },
      {
        "text": "Seringa para irrigação vesical com conector Quick Lock, 150ml",
        "bbox": [
          139.2,
          419.5,
          445.2,
          431.5
        ]
      },
      {
        "text": "NL",
        "bbox": [
          109.4,
          431.5,
          130.3,
          445.0
        ]
      },
      {
        "text": "Blaasspuit quick-lock-aansluiting, 150 ml",
        "bbox": [
          138.2,
          432.7,
          337.9,
          446.4
        ]
      },
      {
        "text": "PL",
        "bbox": [
          109.0,
          444.7,
          129.8,
          459.4
        ]
      },
      {
        "text": "Strzykawka cewnikowa złącze quick-lock, 150ml",
        "bbox": [
          138.5,
          446.6,
          374.4,
          460.1
        ]
      },
      {
        "text": "EL",
        "bbox": [
          109.9,
          459.4,
          134.4,
          472.3
        ]
      },
      {
        "text": "Σúριγγα oupοδóχου κστη με σvδεση Quick-Lοck, 150ml",
        "bbox": [
          137.5,
          460.1,
          425.8,
          474.2
        ]
      },
      {
        "text": "CS Lavážní stříkačka s připojením Quick-Lock, 150 ml",
        "bbox": [
          109.0,
          472.3,
          385.7,
          488.9
        ]
      },
      {
        "text": "HU Hólyagfecskendő Quick-Lock csatlakozóval, 150ml",
        "bbox": [
          109.0,
          486.5,
          387.6,
          502.8
        ]
      },
      {
        "text": "- , 150",
        "bbox": [
          108.7,
          499.9,
          443.0,
          517.4
        ]
      },
      {
        "text": "HR Quick-lock priključak štrcaljke za mjehur, 150 ml",
        "bbox": [
          108.7,
          514.1,
          373.9,
          530.2
        ]
      },
      {
        "text": "ET",
        "bbox": [
          109.0,
          527.8,
          144.0,
          542.6
        ]
      },
      {
        "text": "Quick-Lock-liitmikuga põiesüstal, 150 ml",
        "bbox": [
          137.8,
          529.7,
          336.0,
          542.6
        ]
      },
      {
        "text": "LV ŠJirce ar Quick-Lock savienojumu, 150 ml",
        "bbox": [
          107.5,
          540.2,
          343.0,
          559.2
        ]
      },
      {
        "text": "LT Šlapimo pūslės švirkšto Quick-Lock jungtis, 150 ml",
        "bbox": [
          108.5,
          555.1,
          386.9,
          572.4
        ]
      },
      {
        "text": "RO Seringå pentru vezica urinară conectare tip Quick-Lock, 150 ml",
        "bbox": [
          108.7,
          569.0,
          446.4,
          586.3
        ]
      },
      {
        "text": "SK Injekčná striekačka na močový mechúr, s uzáverom Quick-Lock, 150ml",
        "bbox": [
          109.4,
          583.4,
          485.0,
          599.5
        ]
      },
      {
        "text": "800020460 Rev.1",
        "bbox": [
          472.6,
          601.0,
          571.9,
          614.2
        ]
      }
    ]
  },
  {
    "file": "800020800.pdf",
    "page": 1,
    "elements": [
      {
        "text": "[X]",
        "bbox": [
          776.8,
          216.1,
          798.3,
          237.7
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          780.4,
          217.2,
          797.9,
          238.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          806.3,
          226.2,
          825.3,
          240.5
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          810.6,
          228.0,
          829.6,
          250.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          809.6,
          234.8,
          827.5,
          249.1
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          622.8,
          248.8,
          635.3,
          265.0
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          780.2,
          249.4,
          799.6,
          271.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          782.3,
          251.1,
          798.5,
          270.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          460.8,
          681.2,
          472.0,
          689.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          464.9,
          681.7,
          473.6,
          691.1
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          447.1,
          688.2,
          464.9,
          701.5
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          454.2,
          689.6,
          469.2,
          705.2
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          948.2,
          761.1,
          961.0,
          773.9
        ]
      }
    ]
  }
]
