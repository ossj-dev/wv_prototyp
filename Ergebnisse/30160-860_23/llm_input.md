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
          81.2,
          57.0,
          142.5,
          67.9
        ]
      },
      {
        "text": " Etikettenwerkstoff.PolyesterfoliemitAcrylatkleber",
        "bbox": [
          74.6,
          380.3,
          342.3,
          395.1
        ]
      },
      {
        "text": " BeiPlatzmangelkanndasLabelgeteiltwerden",
        "bbox": [
          74.6,
          410.2,
          318.0,
          425.0
        ]
      },
      {
        "text": " LabelgrößekannvomZuliefererbestimmtwerden",
        "bbox": [
          74.6,
          440.2,
          336.8,
          455.0
        ]
      },
      {
        "text": " Mindestschriftgröße2mm",
        "bbox": [
          74.6,
          470.1,
          219.5,
          484.9
        ]
      },
      {
        "text": " DasSymbolREFkannauchnuralsTextdargestelltwerden",
        "bbox": [
          74.6,
          500.1,
          375.7,
          514.9
        ]
      },
      {
        "text": " DieLOT-NummerundderStatusistentsprechenddemArbeitsauftrageinzutragen",
        "bbox": [
          74.6,
          530.0,
          493.2,
          544.8
        ]
      },
      {
        "text": " DemZuliefererwirdfreigestelltdenDatamatrixcodemiteineralphanumerischenTrennung zwischen REF-Nr. und LOT (z.B. 12345-678OP123456) oder ohne Trennung (z.B. 12345-678123456) auszuführen",
        "bbox": [
          74.6,
          560.0,
          574.0,
          604.0
        ]
      },
      {
        "text": " MindestgrößeDatamatrixcode6x6mm",
        "bbox": [
          74.6,
          619.1,
          289.2,
          633.9
        ]
      },
      {
        "text": "| Alle mit * gekennzeichneten Zeichnungsobjekte haben . | Alle mit * gekennzeichneten Zeichnungsobjekte haben . | Alle mit * gekennzeichneten Zeichnungsobjekte haben . | sich gegenüber der . | sich gegenüber der . | Vorgängerversion . 2:1 . | Vorgängerversion . 2:1 . | geändert! | |---------------------------------------------------------|---------------------------------------------------------|---------------------------------------------------------|------------------------|------------------------|----------------------------|----------------------------|----------------| | Werkstoff, Bezeichnung, Lieferant | Werkstoff, Bezeichnung, Lieferant | Werkstoff, Bezeichnung, Lieferant | Werkstoff-Nr. | Werkstoff-Nr. | Volumencm³ Maßstab | Volumencm³ Maßstab | geändert! | | Status | ERBE-Nr. | ÄM-Nr. | | Datum | Name Titel: | | | | Gültig | 30135-804 | 20023 | Bearb. | 07.06.2016 | UWED Labellayout | Chargenpflicht | Chargenpflicht | | | | | Gepr. | 07.06.2016 | LAURAS 2D-Code | | | | Dokumentklasse | Dokumentklasse | | | | Dokumentnummer: | Version: | Größe: | | Produktkennzeichnung | Produktkennzeichnung | | | | | | | | Oberflächenbeschaffenheit nach ISO 1302 | Oberflächenbeschaffenheit nach ISO 1302 | | | | D108713 | 001 | | | Maße ohne Toleranzangabe ISO 2768 - mH | Maße ohne Toleranzangabe ISO 2768 - mH | | Elektromedizin GmbH | Elektromedizin GmbH | | | | | | | | Urspr.: | Urspr.: | Ers.für: | Blatt: | 1 / 1 |",
        "bbox": [
          55.2,
          662.9,
          580.8,
          801.0
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
          4.3,
          112.0,
          10.1,
          121.2
        ]
      },
      {
        "text": "1",
        "bbox": [
          1180.5,
          112.0,
          1186.2,
          121.2
        ]
      },
      {
        "text": "2",
        "bbox": [
          4.3,
          315.3,
          10.1,
          324.4
        ]
      },
      {
        "text": "2",
        "bbox": [
          1180.5,
          315.3,
          1186.2,
          324.4
        ]
      },
      {
        "text": "3",
        "bbox": [
          4.3,
          518.6,
          10.1,
          527.7
        ]
      },
      {
        "text": "3",
        "bbox": [
          1180.5,
          518.6,
          1186.2,
          527.7
        ]
      },
      {
        "text": "4",
        "bbox": [
          4.3,
          721.9,
          10.1,
          731.0
        ]
      },
      {
        "text": "4",
        "bbox": [
          1180.5,
          721.9,
          1186.2,
          731.0
        ]
      },
      {
        "text": "A",
        "bbox": [
          156.2,
          3.2,
          163.1,
          12.3
        ]
      },
      {
        "text": "A",
        "bbox": [
          156.2,
          830.7,
          163.1,
          839.8
        ]
      },
      {
        "text": "Realistic View",
        "bbox": [
          173.1,
          40.0,
          238.4,
          49.3
        ]
      },
      {
        "text": "B",
        "bbox": [
          446.6,
          3.2,
          453.5,
          12.3
        ]
      },
      {
        "text": "B",
        "bbox": [
          446.6,
          830.7,
          453.5,
          839.8
        ]
      },
      {
        "text": "C",
        "bbox": [
          736.8,
          3.2,
          744.2,
          12.3
        ]
      },
      {
        "text": "Status",
        "bbox": [
          696.1,
          746.6,
          717.4,
          753.3
        ]
      },
      {
        "text": "Document type",
        "bbox": [
          696.1,
          774.9,
          746.5,
          781.5
        ]
      },
      {
        "text": "Drawing",
        "bbox": [
          696.1,
          786.5,
          729.1,
          794.4
        ]
      },
      {
        "text": "No part of this document may be reproduced or transmitted in any form or by",
        "bbox": [
          696.1,
          801.4,
          848.6,
          805.4
        ]
      },
      {
        "text": "any means, electronic or mechanical, including photocopying, recording or",
        "bbox": [
          696.1,
          806.6,
          843.9,
          810.6
        ]
      },
      {
        "text": "otherwise, without prior written permission. Any infringement shall give rise",
        "bbox": [
          696.1,
          811.8,
          844.6,
          815.7
        ]
      },
      {
        "text": "to an obligation to pay damages. All rights reserved in the event of patent,",
        "bbox": [
          696.1,
          816.9,
          842.9,
          820.9
        ]
      },
      {
        "text": "utility model or design registration.",
        "bbox": [
          696.1,
          822.1,
          764.4,
          826.1
        ]
      },
      {
        "text": "C",
        "bbox": [
          736.8,
          830.7,
          744.2,
          839.8
        ]
      },
      {
        "text": "Created Date Name",
        "bbox": [
          852.0,
          760.8,
          878.7,
          767.5
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887.5,
          760.8,
          925.0,
          767.5
        ]
      },
      {
        "text": "T. Ripplinger",
        "bbox": [
          930.0,
          760.8,
          972.5,
          767.4
        ]
      },
      {
        "text": "Checked",
        "bbox": [
          852.0,
          774.9,
          881.6,
          781.5
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887.5,
          775.0,
          925.0,
          781.6
        ]
      },
      {
        "text": "D.Sauter",
        "bbox": [
          930.0,
          774.9,
          959.6,
          781.5
        ]
      },
      {
        "text": "Elektromedizin GmbH",
        "bbox": [
          870.6,
          816.9,
          958.1,
          824.9
        ]
      },
      {
        "text": "Project",
        "bbox": [
          979.6,
          746.6,
          1002.9,
          753.3
        ]
      },
      {
        "text": "PB HW",
        "bbox": [
          979.6,
          760.2,
          1009.1,
          768.2
        ]
      },
      {
        "text": "Title",
        "bbox": [
          979.6,
          775.0,
          993.8,
          781.6
        ]
      },
      {
        "text": "Assembly Drawing",
        "bbox": [
          979.6,
          788.6,
          1054.1,
          796.5
        ]
      },
      {
        "text": "Schematic Revision",
        "bbox": [
          979.3,
          803.3,
          1045.1,
          810.0
        ]
      },
      {
        "text": "004",
        "bbox": [
          1063.1,
          803.3,
          1075.6,
          810.0
        ]
      },
      {
        "text": "Layout Revision EENr Assy EENr PCB",
        "bbox": [
          979.3,
          817.5,
          1032.6,
          824.1
        ]
      },
      {
        "text": "30160-860 40160-860",
        "bbox": [
          1094.8,
          760.8,
          1173.0,
          767.5
        ]
      },
      {
        "text": "Size",
        "bbox": [
          1135.5,
          775.0,
          1150.1,
          781.6
        ]
      },
      {
        "text": "A3",
        "bbox": [
          1149.6,
          788.6,
          1160.6,
          796.5
        ]
      },
      {
        "text": "Sheet",
        "bbox": [
          1135.5,
          803.3,
          1155.1,
          810.0
        ]
      },
      {
        "text": "04.04.2023",
        "bbox": [
          1063.2,
          817.5,
          1100.7,
          824.1
        ]
      },
      {
        "text": "1 of 7",
        "bbox": [
          1146.5,
          817.5,
          1165.2,
          824.1
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027.2,
          830.7,
          1034.7,
          839.8
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027.2,
          3.2,
          1034.7,
          12.3
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
          4.3,
          112.0,
          10.1,
          121.2
        ]
      },
      {
        "text": "1",
        "bbox": [
          1180.5,
          112.0,
          1186.2,
          121.2
        ]
      },
      {
        "text": "2",
        "bbox": [
          4.3,
          315.3,
          10.1,
          324.4
        ]
      },
      {
        "text": "2",
        "bbox": [
          1180.5,
          315.3,
          1186.2,
          324.4
        ]
      },
      {
        "text": "3",
        "bbox": [
          4.3,
          518.6,
          10.1,
          527.7
        ]
      },
      {
        "text": "3",
        "bbox": [
          1180.5,
          518.6,
          1186.2,
          527.7
        ]
      },
      {
        "text": "4",
        "bbox": [
          4.3,
          721.9,
          10.1,
          731.0
        ]
      },
      {
        "text": "4",
        "bbox": [
          1180.5,
          721.9,
          1186.2,
          731.0
        ]
      },
      {
        "text": "A",
        "bbox": [
          156.2,
          3.2,
          163.1,
          12.3
        ]
      },
      {
        "text": "A",
        "bbox": [
          156.2,
          830.7,
          163.1,
          839.8
        ]
      },
      {
        "text": "View from Top side (Scale 1:1)",
        "bbox": [
          183.7,
          17.4,
          327.1,
          26.7
        ]
      },
      {
        "text": "B",
        "bbox": [
          446.6,
          3.2,
          453.5,
          12.3
        ]
      },
      {
        "text": "B",
        "bbox": [
          446.6,
          830.7,
          453.5,
          839.8
        ]
      },
      {
        "text": "C",
        "bbox": [
          736.8,
          3.2,
          744.2,
          12.3
        ]
      },
      {
        "text": "Status",
        "bbox": [
          696.1,
          746.6,
          717.4,
          753.3
        ]
      },
      {
        "text": "Document type",
        "bbox": [
          696.1,
          774.9,
          746.5,
          781.5
        ]
      },
      {
        "text": "Drawing",
        "bbox": [
          696.1,
          786.5,
          729.1,
          794.4
        ]
      },
      {
        "text": "No part of this document may be reproduced or transmitted in any form or by",
        "bbox": [
          696.1,
          801.4,
          848.6,
          805.4
        ]
      },
      {
        "text": "any means, electronic or mechanical, including photocopying, recording or",
        "bbox": [
          696.1,
          806.6,
          843.9,
          810.6
        ]
      },
      {
        "text": "otherwise, without prior written permission. Any infringement shall give rise",
        "bbox": [
          696.1,
          811.8,
          844.6,
          815.7
        ]
      },
      {
        "text": "to an obligation to pay damages. All rights reserved in the event of patent,",
        "bbox": [
          696.1,
          816.9,
          842.9,
          820.9
        ]
      },
      {
        "text": "utility model or design registration.",
        "bbox": [
          696.1,
          822.1,
          764.4,
          826.1
        ]
      },
      {
        "text": "C",
        "bbox": [
          736.8,
          830.7,
          744.2,
          839.8
        ]
      },
      {
        "text": "Created Date Name",
        "bbox": [
          852.0,
          760.8,
          878.7,
          767.5
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887.5,
          760.8,
          925.0,
          767.5
        ]
      },
      {
        "text": "T. Ripplinger",
        "bbox": [
          930.0,
          760.8,
          972.5,
          767.4
        ]
      },
      {
        "text": "Checked",
        "bbox": [
          852.0,
          774.9,
          881.6,
          781.5
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887.5,
          775.0,
          925.0,
          781.6
        ]
      },
      {
        "text": "D.Sauter",
        "bbox": [
          930.0,
          774.9,
          959.6,
          781.5
        ]
      },
      {
        "text": "Elektromedizin GmbH",
        "bbox": [
          870.6,
          816.9,
          958.1,
          824.9
        ]
      },
      {
        "text": "Project",
        "bbox": [
          979.6,
          746.6,
          1002.9,
          753.3
        ]
      },
      {
        "text": "PB HW",
        "bbox": [
          979.6,
          760.2,
          1009.1,
          768.2
        ]
      },
      {
        "text": "Title",
        "bbox": [
          979.6,
          775.0,
          993.8,
          781.6
        ]
      },
      {
        "text": "Assembly Drawing",
        "bbox": [
          979.6,
          788.6,
          1054.1,
          796.5
        ]
      },
      {
        "text": "Schematic Revision",
        "bbox": [
          979.3,
          803.3,
          1045.1,
          810.0
        ]
      },
      {
        "text": "004",
        "bbox": [
          1063.1,
          803.3,
          1075.6,
          810.0
        ]
      },
      {
        "text": "Layout Revision EENr Assy EENr PCB",
        "bbox": [
          979.3,
          817.5,
          1032.6,
          824.1
        ]
      },
      {
        "text": "30160-860 40160-860",
        "bbox": [
          1094.8,
          760.8,
          1173.0,
          767.5
        ]
      },
      {
        "text": "Size",
        "bbox": [
          1135.5,
          775.0,
          1150.1,
          781.6
        ]
      },
      {
        "text": "A3",
        "bbox": [
          1149.6,
          788.6,
          1160.6,
          796.5
        ]
      },
      {
        "text": "Sheet",
        "bbox": [
          1135.5,
          803.3,
          1155.1,
          810.0
        ]
      },
      {
        "text": "04.04.2023",
        "bbox": [
          1063.2,
          817.5,
          1100.7,
          824.1
        ]
      },
      {
        "text": "2 of 7",
        "bbox": [
          1146.5,
          817.5,
          1165.2,
          824.1
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027.2,
          830.7,
          1034.7,
          839.8
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027.2,
          3.2,
          1034.7,
          12.3
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
          4.3,
          112.0,
          10.1,
          121.2
        ]
      },
      {
        "text": "1",
        "bbox": [
          1180.5,
          112.0,
          1186.2,
          121.2
        ]
      },
      {
        "text": "2",
        "bbox": [
          4.3,
          315.3,
          10.1,
          324.4
        ]
      },
      {
        "text": "2",
        "bbox": [
          1180.5,
          315.3,
          1186.2,
          324.4
        ]
      },
      {
        "text": "3",
        "bbox": [
          4.3,
          518.6,
          10.1,
          527.7
        ]
      },
      {
        "text": "3",
        "bbox": [
          1180.5,
          518.6,
          1186.2,
          527.7
        ]
      },
      {
        "text": "4",
        "bbox": [
          4.3,
          721.9,
          10.1,
          731.0
        ]
      },
      {
        "text": "4",
        "bbox": [
          1180.5,
          721.9,
          1186.2,
          731.0
        ]
      },
      {
        "text": "A",
        "bbox": [
          156.2,
          3.2,
          163.1,
          12.3
        ]
      },
      {
        "text": "A",
        "bbox": [
          156.2,
          830.7,
          163.1,
          839.8
        ]
      },
      {
        "text": "Realistic View Bottom",
        "bbox": [
          244.0,
          54.2,
          345.5,
          63.5
        ]
      },
      {
        "text": "B",
        "bbox": [
          446.6,
          3.2,
          453.5,
          12.3
        ]
      },
      {
        "text": "B",
        "bbox": [
          446.6,
          830.7,
          453.5,
          839.8
        ]
      },
      {
        "text": "C",
        "bbox": [
          736.8,
          3.2,
          744.2,
          12.3
        ]
      },
      {
        "text": "Vorzugsrichtung Wellenlötung auf der LS",
        "bbox": [
          533.1,
          39.5,
          798.3,
          51.4
        ]
      },
      {
        "text": "Status",
        "bbox": [
          696.1,
          746.6,
          717.4,
          753.3
        ]
      },
      {
        "text": "Document type",
        "bbox": [
          696.1,
          774.9,
          746.5,
          781.5
        ]
      },
      {
        "text": "Drawing",
        "bbox": [
          696.1,
          786.5,
          729.1,
          794.4
        ]
      },
      {
        "text": "No part of this document may be reproduced or transmitted in any form or by",
        "bbox": [
          696.1,
          801.4,
          848.6,
          805.4
        ]
      },
      {
        "text": "any means, electronic or mechanical, including photocopying, recording or",
        "bbox": [
          696.1,
          806.6,
          843.9,
          810.6
        ]
      },
      {
        "text": "otherwise, without prior written permission. Any infringement shall give rise",
        "bbox": [
          696.1,
          811.8,
          844.6,
          815.7
        ]
      },
      {
        "text": "to an obligation to pay damages. All rights reserved in the event of patent,",
        "bbox": [
          696.1,
          816.9,
          842.9,
          820.9
        ]
      },
      {
        "text": "utility model or design registration.",
        "bbox": [
          696.1,
          822.1,
          764.4,
          826.1
        ]
      },
      {
        "text": "C",
        "bbox": [
          736.8,
          830.7,
          744.2,
          839.8
        ]
      },
      {
        "text": "Created Date Name",
        "bbox": [
          852.0,
          760.8,
          878.7,
          767.5
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887.5,
          760.8,
          925.0,
          767.5
        ]
      },
      {
        "text": "T. Ripplinger",
        "bbox": [
          930.0,
          760.8,
          972.5,
          767.4
        ]
      },
      {
        "text": "Checked",
        "bbox": [
          852.0,
          774.9,
          881.6,
          781.5
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887.5,
          775.0,
          925.0,
          781.6
        ]
      },
      {
        "text": "D.Sauter",
        "bbox": [
          930.0,
          774.9,
          959.6,
          781.5
        ]
      },
      {
        "text": "Elektromedizin GmbH",
        "bbox": [
          870.6,
          816.9,
          958.1,
          824.9
        ]
      },
      {
        "text": "Project",
        "bbox": [
          979.6,
          746.6,
          1002.9,
          753.3
        ]
      },
      {
        "text": "PB HW",
        "bbox": [
          979.6,
          760.2,
          1009.1,
          768.2
        ]
      },
      {
        "text": "Title",
        "bbox": [
          979.6,
          775.0,
          993.8,
          781.6
        ]
      },
      {
        "text": "Assembly Drawing",
        "bbox": [
          979.6,
          788.6,
          1054.1,
          796.5
        ]
      },
      {
        "text": "Schematic Revision",
        "bbox": [
          979.3,
          803.3,
          1045.1,
          810.0
        ]
      },
      {
        "text": "004",
        "bbox": [
          1063.1,
          803.3,
          1075.6,
          810.0
        ]
      },
      {
        "text": "Layout Revision EENr Assy EENr PCB",
        "bbox": [
          979.3,
          817.5,
          1032.6,
          824.1
        ]
      },
      {
        "text": "30160-860 40160-860",
        "bbox": [
          1094.8,
          760.8,
          1173.0,
          767.5
        ]
      },
      {
        "text": "Size",
        "bbox": [
          1135.5,
          775.0,
          1150.1,
          781.6
        ]
      },
      {
        "text": "A3",
        "bbox": [
          1149.6,
          788.6,
          1160.6,
          796.5
        ]
      },
      {
        "text": "Sheet",
        "bbox": [
          1135.5,
          803.3,
          1155.1,
          810.0
        ]
      },
      {
        "text": "04.04.2023",
        "bbox": [
          1063.2,
          817.5,
          1100.7,
          824.1
        ]
      },
      {
        "text": "3 of 7",
        "bbox": [
          1146.5,
          817.5,
          1165.2,
          824.1
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027.2,
          830.7,
          1034.7,
          839.8
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027.2,
          3.2,
          1034.7,
          12.3
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
          4.3,
          112.0,
          10.1,
          121.2
        ]
      },
      {
        "text": "1",
        "bbox": [
          1180.5,
          112.0,
          1186.2,
          121.2
        ]
      },
      {
        "text": "2",
        "bbox": [
          4.3,
          315.3,
          10.1,
          324.4
        ]
      },
      {
        "text": "2",
        "bbox": [
          1180.5,
          315.3,
          1186.2,
          324.4
        ]
      },
      {
        "text": "3",
        "bbox": [
          4.3,
          518.6,
          10.1,
          527.7
        ]
      },
      {
        "text": "3",
        "bbox": [
          1180.5,
          518.6,
          1186.2,
          527.7
        ]
      },
      {
        "text": "4",
        "bbox": [
          4.3,
          721.9,
          10.1,
          731.0
        ]
      },
      {
        "text": "4",
        "bbox": [
          1180.5,
          721.9,
          1186.2,
          731.0
        ]
      },
      {
        "text": "A",
        "bbox": [
          156.2,
          3.2,
          163.1,
          12.3
        ]
      },
      {
        "text": "A",
        "bbox": [
          156.2,
          830.7,
          163.1,
          839.8
        ]
      },
      {
        "text": "View from Bottom side (Scale 2:3)",
        "bbox": [
          271.4,
          77.9,
          430.0,
          87.2
        ]
      },
      {
        "text": "B",
        "bbox": [
          446.6,
          3.2,
          453.5,
          12.3
        ]
      },
      {
        "text": "B",
        "bbox": [
          446.6,
          830.7,
          453.5,
          839.8
        ]
      },
      {
        "text": "C",
        "bbox": [
          736.8,
          3.2,
          744.2,
          12.3
        ]
      },
      {
        "text": "Status",
        "bbox": [
          696.1,
          746.6,
          717.4,
          753.3
        ]
      },
      {
        "text": "Document type",
        "bbox": [
          696.1,
          774.9,
          746.5,
          781.5
        ]
      },
      {
        "text": "Drawing",
        "bbox": [
          696.1,
          786.5,
          729.1,
          794.4
        ]
      },
      {
        "text": "No part of this document may be reproduced or transmitted in any form or by",
        "bbox": [
          696.1,
          801.4,
          848.6,
          805.4
        ]
      },
      {
        "text": "any means, electronic or mechanical, including photocopying, recording or",
        "bbox": [
          696.1,
          806.6,
          843.9,
          810.6
        ]
      },
      {
        "text": "otherwise, without prior written permission. Any infringement shall give rise",
        "bbox": [
          696.1,
          811.8,
          844.6,
          815.7
        ]
      },
      {
        "text": "to an obligation to pay damages. All rights reserved in the event of patent,",
        "bbox": [
          696.1,
          816.9,
          842.9,
          820.9
        ]
      },
      {
        "text": "utility model or design registration.",
        "bbox": [
          696.1,
          822.1,
          764.4,
          826.1
        ]
      },
      {
        "text": "C",
        "bbox": [
          736.8,
          830.7,
          744.2,
          839.8
        ]
      },
      {
        "text": "Created Date Name",
        "bbox": [
          852.0,
          760.8,
          878.7,
          767.5
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887.5,
          760.8,
          925.0,
          767.5
        ]
      },
      {
        "text": "T. Ripplinger",
        "bbox": [
          930.0,
          760.8,
          972.5,
          767.4
        ]
      },
      {
        "text": "Checked",
        "bbox": [
          852.0,
          774.9,
          881.6,
          781.5
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887.5,
          775.0,
          925.0,
          781.6
        ]
      },
      {
        "text": "D.Sauter",
        "bbox": [
          930.0,
          774.9,
          959.6,
          781.5
        ]
      },
      {
        "text": "Elektromedizin GmbH",
        "bbox": [
          870.6,
          816.9,
          958.1,
          824.9
        ]
      },
      {
        "text": "Project",
        "bbox": [
          979.6,
          746.6,
          1002.9,
          753.3
        ]
      },
      {
        "text": "PB HW",
        "bbox": [
          979.6,
          760.2,
          1009.1,
          768.2
        ]
      },
      {
        "text": "Title",
        "bbox": [
          979.6,
          775.0,
          993.8,
          781.6
        ]
      },
      {
        "text": "Assembly Drawing",
        "bbox": [
          979.6,
          788.6,
          1054.1,
          796.5
        ]
      },
      {
        "text": "Schematic Revision",
        "bbox": [
          979.3,
          803.3,
          1045.1,
          810.0
        ]
      },
      {
        "text": "004",
        "bbox": [
          1063.1,
          803.3,
          1075.6,
          810.0
        ]
      },
      {
        "text": "Layout Revision EENr Assy EENr PCB",
        "bbox": [
          979.3,
          817.5,
          1032.6,
          824.1
        ]
      },
      {
        "text": "30160-860 40160-860",
        "bbox": [
          1094.8,
          760.8,
          1173.0,
          767.5
        ]
      },
      {
        "text": "Size",
        "bbox": [
          1135.5,
          775.0,
          1150.1,
          781.6
        ]
      },
      {
        "text": "A3",
        "bbox": [
          1149.6,
          788.6,
          1160.6,
          796.5
        ]
      },
      {
        "text": "Sheet",
        "bbox": [
          1135.5,
          803.3,
          1155.1,
          810.0
        ]
      },
      {
        "text": "04.04.2023",
        "bbox": [
          1063.2,
          817.5,
          1100.7,
          824.1
        ]
      },
      {
        "text": "4 of 7",
        "bbox": [
          1146.5,
          817.5,
          1165.2,
          824.1
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027.2,
          830.7,
          1034.7,
          839.8
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027.2,
          3.2,
          1034.7,
          12.3
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
          313.7,
          104.4,
          325.1,
          115.8
        ]
      },
      {
        "text": "1",
        "bbox": [
          4.3,
          112.0,
          10.1,
          121.2
        ]
      },
      {
        "text": "1",
        "bbox": [
          1180.5,
          112.0,
          1186.2,
          121.2
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          644.2,
          184.9,
          652.7,
          193.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          701.8,
          242.5,
          710.3,
          251.0
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          114.2,
          284.2,
          129.2,
          299.2
        ]
      },
      {
        "text": "2",
        "bbox": [
          4.3,
          315.3,
          10.1,
          324.4
        ]
      },
      {
        "text": "2",
        "bbox": [
          1180.5,
          315.3,
          1186.2,
          324.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          563.9,
          491.5,
          578.9,
          506.5
        ]
      },
      {
        "text": "3",
        "bbox": [
          4.3,
          518.6,
          10.1,
          527.7
        ]
      },
      {
        "text": "3",
        "bbox": [
          1180.5,
          518.6,
          1186.2,
          527.7
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          656.7,
          666.4,
          677.0,
          691.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          635.2,
          666.4,
          660.1,
          691.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          638.8,
          666.4,
          663.6,
          691.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          642.3,
          666.4,
          667.2,
          691.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          645.8,
          666.4,
          670.7,
          691.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          649.4,
          666.4,
          674.2,
          691.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          652.9,
          666.4,
          677.8,
          691.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          660.0,
          666.4,
          684.8,
          691.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          663.5,
          666.4,
          688.3,
          691.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          667.0,
          666.4,
          691.9,
          691.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          670.5,
          666.4,
          695.4,
          691.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          674.1,
          666.4,
          698.9,
          691.3
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          388.4,
          700.1,
          399.8,
          711.5
        ]
      },
      {
        "text": "4",
        "bbox": [
          4.3,
          721.9,
          10.1,
          731.0
        ]
      },
      {
        "text": "4",
        "bbox": [
          1180.5,
          721.9,
          1186.2,
          731.0
        ]
      },
      {
        "text": "L301",
        "bbox": [
          146.2,
          378.4,
          154.0,
          397.9
        ]
      },
      {
        "text": "K300",
        "bbox": [
          137.2,
          475.3,
          157.7,
          483.1
        ]
      },
      {
        "text": "C318",
        "bbox": [
          132.7,
          507.8,
          153.8,
          515.6
        ]
      },
      {
        "text": "L300",
        "bbox": [
          135.8,
          552.4,
          155.4,
          560.1
        ]
      },
      {
        "text": "C317",
        "bbox": [
          133.2,
          598.0,
          154.3,
          605.7
        ]
      },
      {
        "text": "J301",
        "bbox": [
          129.9,
          644.5,
          149.0,
          652.2
        ]
      },
      {
        "text": "SW300",
        "bbox": [
          141.1,
          714.7,
          148.9,
          743.5
        ]
      },
      {
        "text": "SW300",
        "bbox": [
          141.1,
          714.7,
          148.9,
          743.5
        ]
      },
      {
        "text": "A",
        "bbox": [
          156.2,
          3.2,
          163.1,
          12.3
        ]
      },
      {
        "text": "View from Top side (Scale 1:1)",
        "bbox": [
          104.7,
          86.0,
          248.1,
          95.3
        ]
      },
      {
        "text": "Designator11",
        "bbox": [
          144.3,
          242.3,
          147.7,
          264.6
        ]
      },
      {
        "text": "C301",
        "bbox": [
          203.7,
          277.2,
          224.8,
          285.0
        ]
      },
      {
        "text": "C302",
        "bbox": [
          203.9,
          330.8,
          224.9,
          338.6
        ]
      },
      {
        "text": "J300",
        "bbox": [
          219.1,
          514.4,
          226.8,
          533.5
        ]
      },
      {
        "text": "J1000",
        "bbox": [
          223.0,
          699.6,
          230.8,
          723.6
        ]
      },
      {
        "text": "A",
        "bbox": [
          156.2,
          830.7,
          163.1,
          839.8
        ]
      },
      {
        "text": "RV300",
        "bbox": [
          182.2,
          643.7,
          190.0,
          670.6
        ]
      },
      {
        "text": "R318",
        "bbox": [
          193.9,
          544.5,
          201.7,
          565.5
        ]
      },
      {
        "text": "J1103",
        "bbox": [
          272.9,
          257.6,
          280.7,
          281.6
        ]
      },
      {
        "text": "C404",
        "bbox": [
          287.3,
          405.8,
          309.5,
          417.8
        ]
      },
      {
        "text": "HS403",
        "bbox": [
          315.0,
          440.0,
          341.9,
          447.8
        ]
      },
      {
        "text": "D401",
        "bbox": [
          333.1,
          432.9,
          340.9,
          453.9
        ]
      },
      {
        "text": "J1500",
        "bbox": [
          355.3,
          256.7,
          363.1,
          280.7
        ]
      },
      {
        "text": "HS400",
        "bbox": [
          361.1,
          440.2,
          388.0,
          447.9
        ]
      },
      {
        "text": "D402",
        "bbox": [
          379.1,
          433.0,
          386.9,
          454.1
        ]
      },
      {
        "text": "HS402 HS401",
        "bbox": [
          315.0,
          487.4,
          388.0,
          495.3
        ]
      },
      {
        "text": "D405",
        "bbox": [
          333.1,
          480.2,
          340.9,
          501.3
        ]
      },
      {
        "text": "D403",
        "bbox": [
          379.1,
          480.4,
          386.9,
          501.4
        ]
      },
      {
        "text": "T400",
        "bbox": [
          348.9,
          585.8,
          356.7,
          605.9
        ]
      },
      {
        "text": "L402",
        "bbox": [
          312.6,
          688.7,
          332.2,
          696.5
        ]
      },
      {
        "text": "R401",
        "bbox": [
          397.8,
          446.3,
          405.6,
          467.3
        ]
      },
      {
        "text": "R400",
        "bbox": [
          401.1,
          584.3,
          408.8,
          605.4
        ]
      },
      {
        "text": "L1201",
        "bbox": [
          410.5,
          123.9,
          435.0,
          131.6
        ]
      },
      {
        "text": "JP1203",
        "bbox": [
          412.0,
          120.9,
          415.3,
          133.6
        ]
      },
      {
        "text": "JP1202",
        "bbox": [
          426.8,
          120.9,
          430.1,
          133.6
        ]
      },
      {
        "text": "JP1201",
        "bbox": [
          415.8,
          120.9,
          419.1,
          133.6
        ]
      },
      {
        "text": "JP1200",
        "bbox": [
          430.6,
          120.9,
          433.9,
          133.6
        ]
      },
      {
        "text": "C1204",
        "bbox": [
          420.9,
          203.2,
          428.7,
          229.1
        ]
      },
      {
        "text": "B",
        "bbox": [
          446.6,
          3.2,
          453.5,
          12.3
        ]
      },
      {
        "text": "C401",
        "bbox": [
          450.7,
          341.9,
          471.8,
          349.6
        ]
      },
      {
        "text": "L403",
        "bbox": [
          446.4,
          404.8,
          465.9,
          412.6
        ]
      },
      {
        "text": "L404",
        "bbox": [
          430.1,
          487.1,
          437.9,
          506.6
        ]
      },
      {
        "text": "L400",
        "bbox": [
          493.3,
          487.1,
          501.1,
          506.6
        ]
      },
      {
        "text": "C206",
        "bbox": [
          448.8,
          616.9,
          463.9,
          639.3
        ]
      },
      {
        "text": "C206",
        "bbox": [
          448.8,
          616.9,
          463.9,
          639.3
        ]
      },
      {
        "text": "B",
        "bbox": [
          446.6,
          830.7,
          453.5,
          839.8
        ]
      },
      {
        "text": "Q200",
        "bbox": [
          471.2,
          660.2,
          486.8,
          683.0
        ]
      },
      {
        "text": "R1301",
        "bbox": [
          520.2,
          376.3,
          530.6,
          402.9
        ]
      },
      {
        "text": "C200",
        "bbox": [
          517.3,
          574.6,
          539.7,
          589.7
        ]
      },
      {
        "text": "C200",
        "bbox": [
          517.3,
          574.6,
          539.7,
          589.7
        ]
      },
      {
        "text": "T1200",
        "bbox": [
          542.1,
          195.0,
          549.9,
          219.9
        ]
      },
      {
        "text": "T200",
        "bbox": [
          544.7,
          638.7,
          566.2,
          653.7
        ]
      },
      {
        "text": "T200",
        "bbox": [
          544.7,
          638.7,
          566.2,
          653.7
        ]
      },
      {
        "text": "K1204",
        "bbox": [
          566.5,
          332.6,
          577.4,
          358.8
        ]
      },
      {
        "text": "K1203",
        "bbox": [
          603.7,
          337.1,
          614.5,
          363.3
        ]
      },
      {
        "text": "K1202",
        "bbox": [
          640.5,
          341.6,
          651.3,
          367.8
        ]
      },
      {
        "text": "C1201",
        "bbox": [
          665.8,
          120.3,
          692.6,
          138.3
        ]
      },
      {
        "text": "L1200",
        "bbox": [
          673.9,
          205.6,
          681.7,
          230.0
        ]
      },
      {
        "text": "K1205",
        "bbox": [
          676.5,
          355.2,
          687.3,
          381.4
        ]
      },
      {
        "text": "C216",
        "bbox": [
          647.1,
          553.3,
          662.5,
          575.7
        ]
      },
      {
        "text": "C215 C214",
        "bbox": [
          624.8,
          589.8,
          684.9,
          622.9
        ]
      },
      {
        "text": "J1104",
        "bbox": [
          663.4,
          666.9,
          671.2,
          690.8
        ]
      },
      {
        "text": "L203",
        "bbox": [
          700.1,
          548.4,
          714.9,
          569.5
        ]
      },
      {
        "text": "J1102",
        "bbox": [
          690.4,
          676.4,
          714.4,
          684.2
        ]
      },
      {
        "text": "C",
        "bbox": [
          736.8,
          3.2,
          744.2,
          12.3
        ]
      },
      {
        "text": "R1200",
        "bbox": [
          738.0,
          120.7,
          764.4,
          140.4
        ]
      },
      {
        "text": "R1201",
        "bbox": [
          734.6,
          171.4,
          761.0,
          191.1
        ]
      },
      {
        "text": "C1203",
        "bbox": [
          736.5,
          243.7,
          744.3,
          269.6
        ]
      },
      {
        "text": "C1200",
        "bbox": [
          768.6,
          243.7,
          776.4,
          269.6
        ]
      },
      {
        "text": "C1202",
        "bbox": [
          734.9,
          304.7,
          760.8,
          312.5
        ]
      },
      {
        "text": "K1201",
        "bbox": [
          759.6,
          357.2,
          770.4,
          383.4
        ]
      },
      {
        "text": "C213",
        "bbox": [
          739.5,
          538.6,
          761.9,
          554.0
        ]
      },
      {
        "text": "J1101",
        "bbox": [
          758.8,
          659.2,
          766.6,
          683.2
        ]
      },
      {
        "text": "Status",
        "bbox": [
          696.1,
          746.6,
          717.4,
          753.3
        ]
      },
      {
        "text": "Document type",
        "bbox": [
          696.1,
          774.9,
          746.5,
          781.5
        ]
      },
      {
        "text": "Drawing",
        "bbox": [
          696.1,
          786.5,
          729.1,
          794.4
        ]
      },
      {
        "text": "No part of this document may be reproduced or transmitted in any form or by",
        "bbox": [
          696.1,
          801.4,
          848.6,
          805.4
        ]
      },
      {
        "text": "any means, electronic or mechanical, including photocopying, recording or",
        "bbox": [
          696.1,
          806.6,
          843.9,
          810.6
        ]
      },
      {
        "text": "otherwise, without prior written permission. Any infringement shall give rise",
        "bbox": [
          696.1,
          811.8,
          844.6,
          815.7
        ]
      },
      {
        "text": "to an obligation to pay damages. All rights reserved in the event of patent,",
        "bbox": [
          696.1,
          816.9,
          842.9,
          820.9
        ]
      },
      {
        "text": "utility model or design registration.",
        "bbox": [
          696.1,
          822.1,
          764.4,
          826.1
        ]
      },
      {
        "text": "C",
        "bbox": [
          736.8,
          830.7,
          744.2,
          839.8
        ]
      },
      {
        "text": "K1200",
        "bbox": [
          722.4,
          352.7,
          733.3,
          378.9
        ]
      },
      {
        "text": "J1600",
        "bbox": [
          802.7,
          133.5,
          810.4,
          157.5
        ]
      },
      {
        "text": "J1601",
        "bbox": [
          802.7,
          139.4,
          810.4,
          163.4
        ]
      },
      {
        "text": "J1401",
        "bbox": [
          803.0,
          226.8,
          810.8,
          250.8
        ]
      },
      {
        "text": "J1400",
        "bbox": [
          802.5,
          474.9,
          810.3,
          498.8
        ]
      },
      {
        "text": "J1100",
        "bbox": [
          807.6,
          621.6,
          815.4,
          645.5
        ]
      },
      {
        "text": "Created",
        "bbox": [
          852.0,
          760.8,
          878.7,
          767.5
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027.2,
          3.2,
          1034.7,
          12.3
        ]
      },
      {
        "text": "Footprint J1100 für",
        "bbox": [
          918.6,
          565.6,
          1107.4,
          585.4
        ]
      },
      {
        "text": "Einpressbauteil in der",
        "bbox": [
          918.6,
          591.4,
          1134.9,
          611.3
        ]
      },
      {
        "text": "Montagelinie!",
        "bbox": [
          918.6,
          617.3,
          1052.4,
          637.2
        ]
      },
      {
        "text": "Pins beim Wellenlöten",
        "bbox": [
          918.6,
          643.2,
          1141.1,
          663.1
        ]
      },
      {
        "text": "abdecken!",
        "bbox": [
          918.6,
          669.0,
          1022.5,
          688.9
        ]
      },
      {
        "text": "Date Name Project",
        "bbox": [
          887.5,
          746.6,
          903.3,
          753.3
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887.5,
          760.8,
          925.0,
          767.5
        ]
      },
      {
        "text": "T. Ripplinger",
        "bbox": [
          930.0,
          760.8,
          972.5,
          767.4
        ]
      },
      {
        "text": "Checked",
        "bbox": [
          852.0,
          774.9,
          881.6,
          781.5
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887.5,
          775.0,
          925.0,
          781.6
        ]
      },
      {
        "text": "D.Sauter",
        "bbox": [
          930.0,
          774.9,
          959.6,
          781.5
        ]
      },
      {
        "text": "Elektromedizin GmbH",
        "bbox": [
          870.6,
          816.9,
          958.1,
          824.9
        ]
      },
      {
        "text": "PB HW",
        "bbox": [
          979.6,
          760.2,
          1009.1,
          768.2
        ]
      },
      {
        "text": "Title",
        "bbox": [
          979.6,
          775.0,
          993.8,
          781.6
        ]
      },
      {
        "text": "Assembly Drawing",
        "bbox": [
          979.6,
          788.6,
          1054.1,
          796.5
        ]
      },
      {
        "text": "Schematic Revision",
        "bbox": [
          979.3,
          803.3,
          1045.1,
          810.0
        ]
      },
      {
        "text": "004",
        "bbox": [
          1063.1,
          803.3,
          1075.6,
          810.0
        ]
      },
      {
        "text": "Layout Revision EENr Assy EENr PCB",
        "bbox": [
          979.3,
          817.5,
          1032.6,
          824.1
        ]
      },
      {
        "text": "30160-860 40160-860",
        "bbox": [
          1094.8,
          760.8,
          1173.0,
          767.5
        ]
      },
      {
        "text": "Size",
        "bbox": [
          1135.5,
          775.0,
          1150.1,
          781.6
        ]
      },
      {
        "text": "A3",
        "bbox": [
          1149.6,
          788.6,
          1160.6,
          796.5
        ]
      },
      {
        "text": "Sheet",
        "bbox": [
          1135.5,
          803.3,
          1155.1,
          810.0
        ]
      },
      {
        "text": "04.04.2023",
        "bbox": [
          1063.2,
          817.5,
          1100.7,
          824.1
        ]
      },
      {
        "text": "5 of 7",
        "bbox": [
          1146.5,
          817.5,
          1165.2,
          824.1
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027.2,
          830.7,
          1034.7,
          839.8
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
          607.1,
          44.9,
          618.5,
          56.2
        ]
      },
      {
        "text": "1",
        "bbox": [
          4.3,
          112.0,
          10.1,
          121.2
        ]
      },
      {
        "text": "1",
        "bbox": [
          1180.5,
          112.0,
          1186.2,
          121.2
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          279.5,
          125.4,
          288.0,
          133.9
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          446.4,
          149.4,
          457.7,
          164.1
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          478.3,
          149.5,
          489.6,
          164.2
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          508.9,
          149.5,
          520.2,
          164.2
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          462.9,
          149.5,
          474.1,
          164.2
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          493.4,
          149.5,
          504.6,
          164.2
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          614.5,
          165.8,
          623.0,
          174.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          221.9,
          183.0,
          230.4,
          191.5
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          606.5,
          199.2,
          620.8,
          216.2
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          803.0,
          224.6,
          818.0,
          239.7
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          448.2,
          298.8,
          456.8,
          307.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          482.3,
          299.0,
          490.8,
          307.5
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          598.7,
          306.9,
          612.9,
          325.0
        ]
      },
      {
        "text": "2",
        "bbox": [
          4.3,
          315.3,
          10.1,
          324.4
        ]
      },
      {
        "text": "2",
        "bbox": [
          1180.5,
          315.3,
          1186.2,
          324.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          428.7,
          378.4,
          450.5,
          400.2
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          147.5,
          380.0,
          156.3,
          388.0
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          483.8,
          384.8,
          499.9,
          400.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          297.7,
          403.6,
          309.7,
          416.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          353.3,
          432.0,
          368.3,
          447.0
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          735.2,
          494.1,
          749.5,
          505.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          298.3,
          504.5,
          316.0,
          524.8
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          322.8,
          504.7,
          331.3,
          515.7
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          735.2,
          510.4,
          749.5,
          521.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          316.6,
          516.4,
          337.7,
          536.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          276.3,
          517.9,
          296.7,
          538.0
        ]
      },
      {
        "text": "3",
        "bbox": [
          4.3,
          518.6,
          10.1,
          527.7
        ]
      },
      {
        "text": "3",
        "bbox": [
          1180.5,
          518.6,
          1186.2,
          527.7
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          311.9,
          548.8,
          327.4,
          565.5
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          450.4,
          574.0,
          458.9,
          585.0
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          460.3,
          576.7,
          471.0,
          588.7
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          343.9,
          579.1,
          352.2,
          588.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          435.0,
          586.0,
          450.3,
          602.2
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          549.1,
          589.9,
          563.3,
          604.0
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          429.6,
          602.0,
          438.1,
          613.0
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          435.7,
          604.6,
          444.2,
          615.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          483.1,
          613.0,
          491.3,
          623.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          464.7,
          620.0,
          485.1,
          637.7
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          421.1,
          620.6,
          433.7,
          635.8
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          442.3,
          631.7,
          465.8,
          650.9
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          414.2,
          637.4,
          426.8,
          652.6
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          532.4,
          640.6,
          543.8,
          652.0
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          436.8,
          644.7,
          460.3,
          663.9
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          473.7,
          645.1,
          482.9,
          653.5
        ]
      },
      {
        "text": "4",
        "bbox": [
          4.3,
          721.9,
          10.1,
          731.0
        ]
      },
      {
        "text": "4",
        "bbox": [
          1180.5,
          721.9,
          1186.2,
          731.0
        ]
      },
      {
        "text": "C1100",
        "bbox": [
          116.9,
          519.1,
          128.0,
          522.4
        ]
      },
      {
        "text": "C1101",
        "bbox": [
          128.0,
          512.7,
          131.3,
          523.8
        ]
      },
      {
        "text": "R1100",
        "bbox": [
          117.3,
          525.8,
          120.7,
          536.9
        ]
      },
      {
        "text": "U1100",
        "bbox": [
          120.8,
          524.2,
          131.8,
          527.5
        ]
      },
      {
        "text": "C1104",
        "bbox": [
          128.0,
          528.0,
          131.3,
          539.1
        ]
      },
      {
        "text": "C1103",
        "bbox": [
          132.8,
          528.0,
          136.2,
          539.1
        ]
      },
      {
        "text": "R1101",
        "bbox": [
          121.4,
          527.5,
          124.7,
          538.6
        ]
      },
      {
        "text": "R1105",
        "bbox": [
          132.3,
          509.4,
          135.6,
          520.5
        ]
      },
      {
        "text": "C1102",
        "bbox": [
          132.3,
          518.2,
          135.6,
          529.2
        ]
      },
      {
        "text": "R1108R1104",
        "bbox": [
          136.5,
          509.5,
          139.8,
          529.2
        ]
      },
      {
        "text": "A",
        "bbox": [
          156.2,
          3.2,
          163.1,
          12.3
        ]
      },
      {
        "text": "View from Bottom side (Scale 1:1)",
        "bbox": [
          104.7,
          26.5,
          263.3,
          35.7
        ]
      },
      {
        "text": "R1107",
        "bbox": [
          140.7,
          352.2,
          151.8,
          355.5
        ]
      },
      {
        "text": "R1106",
        "bbox": [
          141.7,
          357.0,
          152.7,
          360.3
        ]
      },
      {
        "text": "R1103",
        "bbox": [
          141.7,
          361.2,
          152.8,
          364.6
        ]
      },
      {
        "text": "R1102",
        "bbox": [
          141.7,
          366.1,
          152.7,
          369.4
        ]
      },
      {
        "text": "R1210",
        "bbox": [
          243.7,
          359.1,
          254.8,
          362.4
        ]
      },
      {
        "text": "R908",
        "bbox": [
          247.7,
          396.1,
          251.0,
          405.1
        ]
      },
      {
        "text": "U1201",
        "bbox": [
          276.1,
          350.3,
          302.0,
          358.1
        ]
      },
      {
        "text": "R1211",
        "bbox": [
          258.8,
          367.0,
          269.8,
          370.4
        ]
      },
      {
        "text": "R1212",
        "bbox": [
          267.3,
          374.7,
          278.3,
          378.0
        ]
      },
      {
        "text": "C900",
        "bbox": [
          262.1,
          399.1,
          271.1,
          402.4
        ]
      },
      {
        "text": "R314",
        "bbox": [
          790.0,
          395.0,
          799.0,
          398.3
        ]
      },
      {
        "text": "R308",
        "bbox": [
          798.7,
          395.0,
          807.6,
          398.3
        ]
      },
      {
        "text": "C316",
        "bbox": [
          789.9,
          399.2,
          798.8,
          402.5
        ]
      },
      {
        "text": "R900",
        "bbox": [
          253.2,
          400.9,
          262.2,
          404.2
        ]
      },
      {
        "text": "R906",
        "bbox": [
          245.5,
          407.7,
          254.5,
          411.0
        ]
      },
      {
        "text": "R910",
        "bbox": [
          243.8,
          412.0,
          252.7,
          415.3
        ]
      },
      {
        "text": "C907",
        "bbox": [
          253.3,
          412.3,
          262.3,
          415.6
        ]
      },
      {
        "text": "C904",
        "bbox": [
          245.8,
          417.5,
          249.1,
          426.5
        ]
      },
      {
        "text": "C918",
        "bbox": [
          245.5,
          434.3,
          248.8,
          443.3
        ]
      },
      {
        "text": "U900",
        "bbox": [
          257.9,
          403.8,
          261.2,
          412.8
        ]
      },
      {
        "text": "R902",
        "bbox": [
          251.4,
          417.6,
          254.7,
          426.6
        ]
      },
      {
        "text": "C906",
        "bbox": [
          256.7,
          419.4,
          260.3,
          429.1
        ]
      },
      {
        "text": "U902",
        "bbox": [
          249.7,
          436.3,
          258.6,
          439.6
        ]
      },
      {
        "text": "R913",
        "bbox": [
          249.9,
          444.1,
          258.9,
          447.4
        ]
      },
      {
        "text": "R1214",
        "bbox": [
          293.9,
          372.5,
          297.2,
          383.5
        ]
      },
      {
        "text": "R1215",
        "bbox": [
          298.5,
          372.6,
          301.8,
          383.7
        ]
      },
      {
        "text": "R1213",
        "bbox": [
          289.5,
          372.6,
          292.8,
          383.6
        ]
      },
      {
        "text": "R912",
        "bbox": [
          273.0,
          396.0,
          276.3,
          405.0
        ]
      },
      {
        "text": "L900",
        "bbox": [
          265.4,
          403.9,
          268.7,
          412.2
        ]
      },
      {
        "text": "C908",
        "bbox": [
          264.2,
          414.2,
          273.2,
          417.6
        ]
      },
      {
        "text": "D900",
        "bbox": [
          275.0,
          405.8,
          278.3,
          414.8
        ]
      },
      {
        "text": "C909",
        "bbox": [
          263.6,
          420.6,
          273.2,
          424.2
        ]
      },
      {
        "text": "R904",
        "bbox": [
          263.8,
          427.9,
          272.5,
          431.1
        ]
      },
      {
        "text": "C917",
        "bbox": [
          260.4,
          434.8,
          263.7,
          443.8
        ]
      },
      {
        "text": "C913",
        "bbox": [
          280.5,
          395.9,
          283.8,
          404.8
        ]
      },
      {
        "text": "D901",
        "bbox": [
          280.7,
          405.8,
          284.0,
          414.8
        ]
      },
      {
        "text": "C914",
        "bbox": [
          291.2,
          399.2,
          294.5,
          408.2
        ]
      },
      {
        "text": "C905",
        "bbox": [
          280.8,
          420.1,
          289.8,
          423.4
        ]
      },
      {
        "text": "R903",
        "bbox": [
          280.9,
          424.6,
          289.9,
          427.9
        ]
      },
      {
        "text": "C902",
        "bbox": [
          279.9,
          430.0,
          289.5,
          433.5
        ]
      },
      {
        "text": "R905",
        "bbox": [
          273.2,
          435.5,
          282.2,
          438.8
        ]
      },
      {
        "text": "C910",
        "bbox": [
          266.8,
          443.4,
          276.4,
          446.9
        ]
      },
      {
        "text": "R914",
        "bbox": [
          297.9,
          399.0,
          306.8,
          402.3
        ]
      },
      {
        "text": "D902",
        "bbox": [
          286.2,
          397.4,
          289.5,
          406.3
        ]
      },
      {
        "text": "C915",
        "bbox": [
          292.7,
          408.1,
          296.0,
          417.1
        ]
      },
      {
        "text": "U903",
        "bbox": [
          301.8,
          403.9,
          306.5,
          416.8
        ]
      },
      {
        "text": "R911",
        "bbox": [
          292.3,
          419.2,
          295.6,
          428.2
        ]
      },
      {
        "text": "R909",
        "bbox": [
          301.9,
          422.0,
          310.9,
          425.3
        ]
      },
      {
        "text": "R907",
        "bbox": [
          296.4,
          420.2,
          299.8,
          429.2
        ]
      },
      {
        "text": "U901",
        "bbox": [
          295.1,
          432.4,
          304.1,
          435.7
        ]
      },
      {
        "text": "C903",
        "bbox": [
          292.2,
          428.1,
          295.5,
          437.0
        ]
      },
      {
        "text": "C911",
        "bbox": [
          290.2,
          437.2,
          293.5,
          446.2
        ]
      },
      {
        "text": "C912",
        "bbox": [
          283.9,
          437.0,
          287.4,
          446.6
        ]
      },
      {
        "text": "C212",
        "bbox": [
          269.1,
          517.7,
          278.6,
          524.2
        ]
      },
      {
        "text": "L202",
        "bbox": [
          277.7,
          522.2,
          294.9,
          534.4
        ]
      },
      {
        "text": "R901",
        "bbox": [
          304.0,
          427.3,
          307.3,
          436.3
        ]
      },
      {
        "text": "L901",
        "bbox": [
          295.6,
          440.1,
          303.9,
          443.4
        ]
      },
      {
        "text": "C901",
        "bbox": [
          305.6,
          436.4,
          308.9,
          445.3
        ]
      },
      {
        "text": "R223",
        "bbox": [
          308.0,
          493.8,
          314.6,
          503.3
        ]
      },
      {
        "text": "R222",
        "bbox": [
          313.2,
          496.0,
          319.8,
          505.5
        ]
      },
      {
        "text": "U203",
        "bbox": [
          301.4,
          506.2,
          313.6,
          524.0
        ]
      },
      {
        "text": "R211",
        "bbox": [
          304.2,
          527.5,
          313.7,
          534.0
        ]
      },
      {
        "text": "R207",
        "bbox": [
          328.9,
          509.9,
          335.4,
          519.5
        ]
      },
      {
        "text": "C220",
        "bbox": [
          317.3,
          505.2,
          323.9,
          514.7
        ]
      },
      {
        "text": "C210",
        "bbox": [
          323.8,
          505.2,
          330.8,
          515.4
        ]
      },
      {
        "text": "C217",
        "bbox": [
          310.6,
          519.6,
          317.1,
          529.1
        ]
      },
      {
        "text": "D206",
        "bbox": [
          303.4,
          532.6,
          312.9,
          539.1
        ]
      },
      {
        "text": "R212",
        "bbox": [
          312.3,
          530.8,
          318.9,
          540.3
        ]
      },
      {
        "text": "C211",
        "bbox": [
          297.1,
          530.1,
          303.7,
          539.6
        ]
      },
      {
        "text": "Q201",
        "bbox": [
          317.6,
          520.6,
          335.8,
          533.0
        ]
      },
      {
        "text": "D201",
        "bbox": [
          314.7,
          549.6,
          325.2,
          564.9
        ]
      },
      {
        "text": "Q300",
        "bbox": [
          789.9,
          406.0,
          799.1,
          409.3
        ]
      },
      {
        "text": "R306",
        "bbox": [
          799.5,
          405.2,
          808.4,
          408.6
        ]
      },
      {
        "text": "R305",
        "bbox": [
          799.4,
          409.2,
          808.3,
          412.5
        ]
      },
      {
        "text": "C307",
        "bbox": [
          793.8,
          414.6,
          803.4,
          418.1
        ]
      },
      {
        "text": "C309",
        "bbox": [
          793.8,
          421.2,
          803.4,
          424.8
        ]
      },
      {
        "text": "D302",
        "bbox": [
          806.5,
          414.2,
          809.8,
          423.1
        ]
      },
      {
        "text": "C308",
        "bbox": [
          793.8,
          427.8,
          803.4,
          431.4
        ]
      },
      {
        "text": "C312",
        "bbox": [
          806.2,
          423.3,
          809.5,
          432.3
        ]
      },
      {
        "text": "C322 C321",
        "bbox": [
          769.5,
          443.2,
          806.8,
          449.0
        ]
      },
      {
        "text": "L302",
        "bbox": [
          787.0,
          454.3,
          790.4,
          462.8
        ]
      },
      {
        "text": "R317 R316",
        "bbox": [
          773.1,
          526.9,
          800.8,
          530.2
        ]
      },
      {
        "text": "C319",
        "bbox": [
          770.1,
          541.8,
          785.9,
          547.6
        ]
      },
      {
        "text": "C320",
        "bbox": [
          790.5,
          541.8,
          806.3,
          547.6
        ]
      },
      {
        "text": "C1207",
        "bbox": [
          153.6,
          373.6,
          164.6,
          376.9
        ]
      },
      {
        "text": "Q1200",
        "bbox": [
          146.3,
          382.6,
          157.5,
          385.9
        ]
      },
      {
        "text": "R1203",
        "bbox": [
          143.1,
          378.1,
          146.5,
          389.1
        ]
      },
      {
        "text": "R1202",
        "bbox": [
          157.7,
          377.2,
          161.1,
          388.3
        ]
      },
      {
        "text": "C1205",
        "bbox": [
          146.1,
          391.6,
          157.1,
          394.9
        ]
      },
      {
        "text": "R1208",
        "bbox": [
          146.2,
          397.7,
          157.2,
          401.0
        ]
      },
      {
        "text": "C501",
        "bbox": [
          144.9,
          402.6,
          148.2,
          411.5
        ]
      },
      {
        "text": "R506",
        "bbox": [
          150.9,
          402.7,
          154.2,
          411.7
        ]
      },
      {
        "text": "C1002",
        "bbox": [
          159.1,
          388.2,
          162.4,
          399.2
        ]
      },
      {
        "text": "R504",
        "bbox": [
          155.4,
          402.6,
          158.7,
          411.5
        ]
      },
      {
        "text": "R319",
        "bbox": [
          146.0,
          452.3,
          149.3,
          461.3
        ]
      },
      {
        "text": "A",
        "bbox": [
          156.2,
          830.7,
          163.1,
          839.8
        ]
      },
      {
        "text": "L1100",
        "bbox": [
          167.2,
          571.4,
          177.7,
          574.7
        ]
      },
      {
        "text": "C1105",
        "bbox": [
          166.1,
          581.9,
          177.1,
          585.2
        ]
      },
      {
        "text": "C1107",
        "bbox": [
          219.1,
          602.3,
          230.1,
          605.6
        ]
      },
      {
        "text": "C1210",
        "bbox": [
          307.2,
          338.3,
          318.3,
          341.6
        ]
      },
      {
        "text": "C1211",
        "bbox": [
          307.2,
          343.9,
          318.3,
          347.2
        ]
      },
      {
        "text": "C202",
        "bbox": [
          343.6,
          569.0,
          350.1,
          578.5
        ]
      },
      {
        "text": "R1308",
        "bbox": [
          358.8,
          367.7,
          362.1,
          378.7
        ]
      },
      {
        "text": "Q1303",
        "bbox": [
          366.3,
          367.4,
          369.6,
          378.6
        ]
      },
      {
        "text": "R1304",
        "bbox": [
          374.2,
          352.8,
          377.6,
          363.8
        ]
      },
      {
        "text": "C1302",
        "bbox": [
          378.6,
          352.8,
          381.9,
          363.8
        ]
      },
      {
        "text": "Q1301",
        "bbox": [
          371.9,
          366.3,
          383.1,
          369.6
        ]
      },
      {
        "text": "R1306",
        "bbox": [
          372.7,
          374.1,
          383.8,
          377.4
        ]
      },
      {
        "text": "L200",
        "bbox": [
          359.4,
          496.0,
          368.5,
          502.3
        ]
      },
      {
        "text": "R202",
        "bbox": [
          348.2,
          570.7,
          357.8,
          577.3
        ]
      },
      {
        "text": "U201",
        "bbox": [
          344.4,
          579.0,
          351.0,
          588.5
        ]
      },
      {
        "text": "C203",
        "bbox": [
          354.1,
          579.0,
          363.7,
          585.5
        ]
      },
      {
        "text": "R205",
        "bbox": [
          346.5,
          574.6,
          356.0,
          581.2
        ]
      },
      {
        "text": "C201",
        "bbox": [
          351.1,
          582.5,
          357.6,
          592.1
        ]
      },
      {
        "text": "R203",
        "bbox": [
          355.0,
          584.2,
          361.6,
          593.8
        ]
      },
      {
        "text": "R200",
        "bbox": [
          366.1,
          581.7,
          375.7,
          588.2
        ]
      },
      {
        "text": "U200",
        "bbox": [
          370.8,
          591.5,
          393.2,
          606.9
        ]
      },
      {
        "text": "R204",
        "bbox": [
          396.1,
          601.7,
          402.6,
          611.3
        ]
      },
      {
        "text": "C204",
        "bbox": [
          399.9,
          603.4,
          406.5,
          612.9
        ]
      },
      {
        "text": "R201",
        "bbox": [
          361.9,
          587.0,
          368.5,
          596.6
        ]
      },
      {
        "text": "R1300",
        "bbox": [
          387.7,
          361.3,
          391.0,
          372.3
        ]
      },
      {
        "text": "Q1300",
        "bbox": [
          409.6,
          299.2,
          417.3,
          325.6
        ]
      },
      {
        "text": "C1301",
        "bbox": [
          407.3,
          328.9,
          418.3,
          332.2
        ]
      },
      {
        "text": "U1301",
        "bbox": [
          410.7,
          334.5,
          416.6,
          354.0
        ]
      },
      {
        "text": "R1303",
        "bbox": [
          397.7,
          328.1,
          407.9,
          338.2
        ]
      },
      {
        "text": "C1300",
        "bbox": [
          392.6,
          357.4,
          403.6,
          360.7
        ]
      },
      {
        "text": "U1300",
        "bbox": [
          391.0,
          365.6,
          402.1,
          368.9
        ]
      },
      {
        "text": "R1305",
        "bbox": [
          402.3,
          361.8,
          405.6,
          372.9
        ]
      },
      {
        "text": "R1302",
        "bbox": [
          410.7,
          357.4,
          421.7,
          360.7
        ]
      },
      {
        "text": "R1307",
        "bbox": [
          407.7,
          361.8,
          411.0,
          372.9
        ]
      },
      {
        "text": "Q1302",
        "bbox": [
          414.4,
          361.4,
          417.7,
          372.7
        ]
      },
      {
        "text": "R610",
        "bbox": [
          438.2,
          290.3,
          441.5,
          299.2
        ]
      },
      {
        "text": "C601",
        "bbox": [
          438.0,
          302.1,
          441.3,
          311.0
        ]
      },
      {
        "text": "C603",
        "bbox": [
          448.2,
          287.8,
          457.1,
          291.1
        ]
      },
      {
        "text": "C604",
        "bbox": [
          448.6,
          293.1,
          457.6,
          296.4
        ]
      },
      {
        "text": "U601",
        "bbox": [
          451.1,
          298.5,
          454.4,
          307.5
        ]
      },
      {
        "text": "R603",
        "bbox": [
          442.3,
          290.4,
          445.6,
          299.3
        ]
      },
      {
        "text": "R606",
        "bbox": [
          443.1,
          300.5,
          446.4,
          309.5
        ]
      },
      {
        "text": "C608",
        "bbox": [
          446.5,
          311.7,
          449.8,
          320.7
        ]
      },
      {
        "text": "C1510",
        "bbox": [
          454.6,
          127.7,
          465.6,
          131.0
        ]
      },
      {
        "text": "C1513",
        "bbox": [
          454.6,
          137.9,
          465.6,
          141.2
        ]
      },
      {
        "text": "C1512",
        "bbox": [
          486.4,
          127.7,
          497.5,
          131.0
        ]
      },
      {
        "text": "C1511",
        "bbox": [
          517.9,
          127.7,
          529.0,
          131.0
        ]
      },
      {
        "text": "C1509",
        "bbox": [
          486.4,
          137.9,
          497.5,
          141.2
        ]
      },
      {
        "text": "C1508",
        "bbox": [
          517.9,
          140.1,
          529.0,
          143.4
        ]
      },
      {
        "text": "D1506",
        "bbox": [
          426.9,
          152.3,
          434.6,
          178.2
        ]
      },
      {
        "text": "D1500",
        "bbox": [
          531.9,
          153.7,
          539.7,
          179.6
        ]
      },
      {
        "text": "D1505",
        "bbox": [
          450.2,
          149.7,
          454.5,
          163.8
        ]
      },
      {
        "text": "D1503",
        "bbox": [
          482.1,
          149.8,
          486.4,
          164.0
        ]
      },
      {
        "text": "D1501",
        "bbox": [
          512.7,
          149.8,
          517.0,
          164.0
        ]
      },
      {
        "text": "D1504",
        "bbox": [
          466.7,
          149.8,
          470.9,
          164.0
        ]
      },
      {
        "text": "D1502",
        "bbox": [
          497.1,
          149.8,
          501.4,
          164.0
        ]
      },
      {
        "text": "C1504",
        "bbox": [
          471.6,
          175.4,
          482.6,
          178.7
        ]
      },
      {
        "text": "C1507",
        "bbox": [
          471.6,
          185.8,
          482.6,
          189.1
        ]
      },
      {
        "text": "C1506",
        "bbox": [
          502.8,
          175.6,
          513.8,
          178.9
        ]
      },
      {
        "text": "C1503",
        "bbox": [
          502.8,
          185.9,
          513.8,
          189.2
        ]
      },
      {
        "text": "R600",
        "bbox": [
          451.0,
          271.1,
          459.7,
          274.3
        ]
      },
      {
        "text": "R621 R619",
        "bbox": [
          458.7,
          282.1,
          464.0,
          301.0
        ]
      },
      {
        "text": "R617",
        "bbox": [
          458.7,
          301.5,
          462.0,
          310.5
        ]
      },
      {
        "text": "C612",
        "bbox": [
          451.9,
          311.3,
          455.2,
          320.2
        ]
      },
      {
        "text": "C614",
        "bbox": [
          457.3,
          311.3,
          460.6,
          320.2
        ]
      },
      {
        "text": "L401",
        "bbox": [
          431.4,
          381.7,
          447.2,
          397.5
        ]
      },
      {
        "text": "R206",
        "bbox": [
          444.0,
          569.6,
          452.8,
          582.4
        ]
      },
      {
        "text": "R607",
        "bbox": [
          497.8,
          273.8,
          506.4,
          277.0
        ]
      },
      {
        "text": "R602",
        "bbox": [
          474.7,
          271.1,
          483.3,
          274.3
        ]
      },
      {
        "text": "R618",
        "bbox": [
          466.1,
          282.1,
          469.4,
          291.1
        ]
      },
      {
        "text": "C600",
        "bbox": [
          475.8,
          288.1,
          484.7,
          291.4
        ]
      },
      {
        "text": "R604",
        "bbox": [
          476.1,
          293.1,
          485.1,
          296.4
        ]
      },
      {
        "text": "C607",
        "bbox": [
          468.6,
          296.5,
          477.5,
          299.8
        ]
      },
      {
        "text": "R611",
        "bbox": [
          497.8,
          283.2,
          506.4,
          286.4
        ]
      },
      {
        "text": "R614",
        "bbox": [
          464.1,
          290.2,
          467.4,
          299.1
        ]
      },
      {
        "text": "C606",
        "bbox": [
          464.1,
          301.6,
          467.4,
          310.6
        ]
      },
      {
        "text": "C610",
        "bbox": [
          464.1,
          311.7,
          467.4,
          320.7
        ]
      },
      {
        "text": "C611",
        "bbox": [
          468.6,
          301.8,
          477.5,
          305.2
        ]
      },
      {
        "text": "R609",
        "bbox": [
          487.7,
          288.2,
          496.7,
          291.6
        ]
      },
      {
        "text": "R601",
        "bbox": [
          487.7,
          293.6,
          496.7,
          296.9
        ]
      },
      {
        "text": "U600",
        "bbox": [
          482.0,
          301.8,
          491.0,
          305.2
        ]
      },
      {
        "text": "C613",
        "bbox": [
          469.2,
          306.1,
          478.2,
          309.4
        ]
      },
      {
        "text": "R616",
        "bbox": [
          477.0,
          311.0,
          486.0,
          314.3
        ]
      },
      {
        "text": "C602",
        "bbox": [
          493.3,
          298.4,
          496.6,
          307.4
        ]
      },
      {
        "text": "R620",
        "bbox": [
          488.6,
          310.4,
          497.5,
          313.7
        ]
      },
      {
        "text": "U602",
        "bbox": [
          468.6,
          314.9,
          477.6,
          318.2
        ]
      },
      {
        "text": "C605",
        "bbox": [
          477.4,
          315.1,
          486.3,
          318.4
        ]
      },
      {
        "text": "C609",
        "bbox": [
          475.1,
          320.8,
          478.5,
          329.7
        ]
      },
      {
        "text": "C400",
        "bbox": [
          466.0,
          384.5,
          475.6,
          388.1
        ]
      },
      {
        "text": "C207",
        "bbox": [
          451.3,
          574.5,
          458.3,
          584.7
        ]
      },
      {
        "text": "D200",
        "bbox": [
          437.9,
          587.1,
          448.1,
          601.9
        ]
      },
      {
        "text": "C209",
        "bbox": [
          430.5,
          602.5,
          437.6,
          612.7
        ]
      },
      {
        "text": "R218",
        "bbox": [
          432.3,
          625.6,
          438.6,
          634.8
        ]
      },
      {
        "text": "C208",
        "bbox": [
          436.7,
          605.1,
          443.7,
          615.3
        ]
      },
      {
        "text": "D205",
        "bbox": [
          422.7,
          621.2,
          432.8,
          636.0
        ]
      },
      {
        "text": "D203",
        "bbox": [
          415.7,
          638.0,
          425.9,
          652.8
        ]
      },
      {
        "text": "C205",
        "bbox": [
          462.0,
          577.6,
          468.9,
          587.9
        ]
      },
      {
        "text": "R209",
        "bbox": [
          467.0,
          606.4,
          476.5,
          613.0
        ]
      },
      {
        "text": "C218",
        "bbox": [
          461.7,
          615.4,
          468.2,
          624.9
        ]
      },
      {
        "text": "D208",
        "bbox": [
          436.1,
          631.1,
          442.7,
          640.6
        ]
      },
      {
        "text": "R217",
        "bbox": [
          424.1,
          645.1,
          430.4,
          654.3
        ]
      },
      {
        "text": "R208",
        "bbox": [
          465.4,
          610.1,
          474.9,
          616.7
        ]
      },
      {
        "text": "C219",
        "bbox": [
          458.2,
          623.6,
          464.8,
          633.1
        ]
      },
      {
        "text": "D207",
        "bbox": [
          431.6,
          642.1,
          438.1,
          651.6
        ]
      },
      {
        "text": "C222",
        "bbox": [
          442.6,
          634.3,
          464.6,
          649.3
        ]
      },
      {
        "text": "C221",
        "bbox": [
          437.1,
          647.2,
          459.0,
          662.3
        ]
      },
      {
        "text": "B",
        "bbox": [
          446.6,
          830.7,
          453.5,
          839.8
        ]
      },
      {
        "text": "D202",
        "bbox": [
          473.5,
          611.1,
          480.1,
          620.6
        ]
      },
      {
        "text": "C402",
        "bbox": [
          514.6,
          532.2,
          524.2,
          535.8
        ]
      },
      {
        "text": "R214",
        "bbox": [
          505.7,
          591.7,
          512.0,
          601.0
        ]
      },
      {
        "text": "C226",
        "bbox": [
          479.5,
          610.2,
          486.0,
          619.8
        ]
      },
      {
        "text": "U202",
        "bbox": [
          465.6,
          623.1,
          483.4,
          635.3
        ]
      },
      {
        "text": "R224",
        "bbox": [
          484.1,
          613.7,
          490.7,
          623.4
        ]
      },
      {
        "text": "C224",
        "bbox": [
          486.2,
          623.7,
          492.8,
          633.2
        ]
      },
      {
        "text": "C225",
        "bbox": [
          490.4,
          625.4,
          496.9,
          634.9
        ]
      },
      {
        "text": "R221",
        "bbox": [
          487.1,
          635.2,
          496.6,
          641.7
        ]
      },
      {
        "text": "C223",
        "bbox": [
          482.1,
          633.0,
          488.6,
          642.5
        ]
      },
      {
        "text": "D204",
        "bbox": [
          473.4,
          645.7,
          483.0,
          652.2
        ]
      },
      {
        "text": "R210",
        "bbox": [
          465.7,
          650.1,
          475.3,
          656.6
        ]
      },
      {
        "text": "R225",
        "bbox": [
          485.2,
          639.7,
          494.8,
          646.2
        ]
      },
      {
        "text": "R213",
        "bbox": [
          513.9,
          595.2,
          520.2,
          604.4
        ]
      },
      {
        "text": "R220 R216",
        "bbox": [
          499.0,
          607.1,
          510.5,
          628.4
        ]
      },
      {
        "text": "R219 R215",
        "bbox": [
          505.3,
          610.3,
          518.3,
          635.2
        ]
      },
      {
        "text": "NT600",
        "bbox": [
          499.3,
          289.4,
          510.6,
          292.7
        ]
      },
      {
        "text": "R605",
        "bbox": [
          497.9,
          293.6,
          506.9,
          296.9
        ]
      },
      {
        "text": "R608",
        "bbox": [
          497.9,
          299.0,
          506.9,
          302.3
        ]
      },
      {
        "text": "R612",
        "bbox": [
          497.9,
          304.3,
          506.9,
          307.6
        ]
      },
      {
        "text": "R615",
        "bbox": [
          497.9,
          308.9,
          506.9,
          312.2
        ]
      },
      {
        "text": "R402",
        "bbox": [
          510.1,
          295.5,
          516.7,
          313.2
        ]
      },
      {
        "text": "R613",
        "bbox": [
          488.8,
          315.1,
          497.7,
          318.4
        ]
      },
      {
        "text": "L405",
        "bbox": [
          483.8,
          389.8,
          499.8,
          396.2
        ]
      },
      {
        "text": "B",
        "bbox": [
          446.6,
          3.2,
          453.5,
          12.3
        ]
      },
      {
        "text": "C403",
        "bbox": [
          531.4,
          442.1,
          535.0,
          451.6
        ]
      },
      {
        "text": "C1500",
        "bbox": [
          538.6,
          229.0,
          549.6,
          232.3
        ]
      },
      {
        "text": "C1502",
        "bbox": [
          538.6,
          237.9,
          549.6,
          241.2
        ]
      },
      {
        "text": "C1505",
        "bbox": [
          538.6,
          246.8,
          549.6,
          250.2
        ]
      },
      {
        "text": "C1501",
        "bbox": [
          538.6,
          255.9,
          549.6,
          259.2
        ]
      },
      {
        "text": "C1206",
        "bbox": [
          549.4,
          317.6,
          552.7,
          328.7
        ]
      },
      {
        "text": "C916",
        "bbox": [
          538.8,
          346.3,
          542.1,
          355.3
        ]
      },
      {
        "text": "L201",
        "bbox": [
          548.6,
          594.5,
          563.3,
          600.4
        ]
      },
      {
        "text": "C700",
        "bbox": [
          592.7,
          156.6,
          602.3,
          160.2
        ]
      },
      {
        "text": "R704 R702",
        "bbox": [
          600.2,
          160.9,
          603.5,
          180.1
        ]
      },
      {
        "text": "C703",
        "bbox": [
          592.7,
          181.0,
          602.3,
          184.5
        ]
      },
      {
        "text": "C705",
        "bbox": [
          593.6,
          190.2,
          597.0,
          199.2
        ]
      },
      {
        "text": "R707",
        "bbox": [
          599.2,
          187.7,
          602.5,
          196.7
        ]
      },
      {
        "text": "R706",
        "bbox": [
          603.9,
          187.7,
          607.2,
          196.7
        ]
      },
      {
        "text": "U702",
        "bbox": [
          592.3,
          203.5,
          601.3,
          206.8
        ]
      },
      {
        "text": "C702 C701",
        "bbox": [
          605.5,
          160.9,
          608.9,
          180.1
        ]
      },
      {
        "text": "C710",
        "bbox": [
          610.4,
          165.4,
          613.7,
          174.4
        ]
      },
      {
        "text": "U700",
        "bbox": [
          617.3,
          165.6,
          620.6,
          174.5
        ]
      },
      {
        "text": "C704",
        "bbox": [
          614.7,
          177.8,
          623.7,
          181.1
        ]
      },
      {
        "text": "C709",
        "bbox": [
          605.1,
          184.4,
          614.0,
          187.8
        ]
      },
      {
        "text": "R705",
        "bbox": [
          608.2,
          187.7,
          611.5,
          196.7
        ]
      },
      {
        "text": "R700",
        "bbox": [
          622.1,
          187.7,
          625.4,
          196.7
        ]
      },
      {
        "text": "C708",
        "bbox": [
          602.4,
          198.9,
          605.7,
          207.8
        ]
      },
      {
        "text": "C802",
        "bbox": [
          594.3,
          212.0,
          603.2,
          215.3
        ]
      },
      {
        "text": "R801",
        "bbox": [
          595.1,
          216.1,
          604.0,
          219.4
        ]
      },
      {
        "text": "R703",
        "bbox": [
          612.9,
          187.7,
          616.2,
          196.7
        ]
      },
      {
        "text": "R701",
        "bbox": [
          617.6,
          187.7,
          620.9,
          196.7
        ]
      },
      {
        "text": "U701",
        "bbox": [
          611.0,
          199.6,
          617.2,
          216.3
        ]
      },
      {
        "text": "R1206",
        "bbox": [
          594.5,
          260.8,
          597.8,
          271.8
        ]
      },
      {
        "text": "C1209",
        "bbox": [
          602.3,
          257.6,
          613.4,
          260.9
        ]
      },
      {
        "text": "U1200",
        "bbox": [
          605.4,
          260.8,
          608.7,
          271.8
        ]
      },
      {
        "text": "C1208",
        "bbox": [
          592.7,
          272.1,
          603.7,
          275.4
        ]
      },
      {
        "text": "R1205",
        "bbox": [
          602.5,
          272.1,
          613.5,
          275.4
        ]
      },
      {
        "text": "R1209",
        "bbox": [
          592.8,
          277.5,
          603.9,
          280.8
        ]
      },
      {
        "text": "R802",
        "bbox": [
          598.2,
          284.5,
          601.5,
          293.4
        ]
      },
      {
        "text": "R800",
        "bbox": [
          592.8,
          295.4,
          596.1,
          304.3
        ]
      },
      {
        "text": "C800",
        "bbox": [
          597.0,
          295.4,
          600.4,
          304.4
        ]
      },
      {
        "text": "R1207",
        "bbox": [
          604.1,
          275.8,
          607.4,
          286.9
        ]
      },
      {
        "text": "R1204",
        "bbox": [
          609.5,
          275.8,
          612.8,
          286.9
        ]
      },
      {
        "text": "C801",
        "bbox": [
          604.4,
          292.2,
          608.0,
          301.9
        ]
      },
      {
        "text": "R804",
        "bbox": [
          610.6,
          292.2,
          613.9,
          301.2
        ]
      },
      {
        "text": "U800",
        "bbox": [
          603.0,
          307.4,
          609.6,
          325.1
        ]
      },
      {
        "text": "R803",
        "bbox": [
          599.8,
          328.8,
          608.8,
          332.1
        ]
      },
      {
        "text": "C707 C706",
        "bbox": [
          622.1,
          197.5,
          625.4,
          216.3
        ]
      },
      {
        "text": "C1106",
        "bbox": [
          627.8,
          197.3,
          638.9,
          200.6
        ]
      },
      {
        "text": "D1100",
        "bbox": [
          628.1,
          203.1,
          639.2,
          206.4
        ]
      },
      {
        "text": "Q1100",
        "bbox": [
          625.1,
          211.0,
          636.4,
          214.3
        ]
      },
      {
        "text": "R1110",
        "bbox": [
          631.9,
          220.2,
          635.2,
          231.3
        ]
      },
      {
        "text": "R1109",
        "bbox": [
          631.9,
          229.7,
          635.2,
          240.8
        ]
      },
      {
        "text": "C502",
        "bbox": [
          619.0,
          257.0,
          622.5,
          266.6
        ]
      },
      {
        "text": "R505",
        "bbox": [
          625.7,
          255.7,
          629.0,
          264.7
        ]
      },
      {
        "text": "C500",
        "bbox": [
          620.3,
          268.5,
          623.6,
          277.4
        ]
      },
      {
        "text": "C305",
        "bbox": [
          618.7,
          280.4,
          627.6,
          283.7
        ]
      },
      {
        "text": "R304",
        "bbox": [
          618.5,
          285.8,
          627.5,
          289.1
        ]
      },
      {
        "text": "C300",
        "bbox": [
          618.7,
          291.2,
          627.6,
          294.5
        ]
      },
      {
        "text": "R315",
        "bbox": [
          618.5,
          296.6,
          627.5,
          299.9
        ]
      },
      {
        "text": "R313",
        "bbox": [
          618.5,
          304.5,
          627.5,
          307.8
        ]
      },
      {
        "text": "C315",
        "bbox": [
          618.7,
          309.8,
          627.6,
          313.1
        ]
      },
      {
        "text": "C311",
        "bbox": [
          618.7,
          315.4,
          627.6,
          318.8
        ]
      },
      {
        "text": "R1112",
        "bbox": [
          637.3,
          219.5,
          640.6,
          230.6
        ]
      },
      {
        "text": "R1111",
        "bbox": [
          637.3,
          229.7,
          640.6,
          240.8
        ]
      },
      {
        "text": "U501",
        "bbox": [
          632.4,
          268.0,
          653.4,
          275.8
        ]
      },
      {
        "text": "U301",
        "bbox": [
          633.5,
          283.3,
          654.6,
          291.0
        ]
      },
      {
        "text": "U305",
        "bbox": [
          633.5,
          295.8,
          654.6,
          303.6
        ]
      },
      {
        "text": "U304",
        "bbox": [
          633.5,
          308.8,
          654.6,
          316.5
        ]
      },
      {
        "text": "R502",
        "bbox": [
          665.2,
          265.8,
          674.1,
          269.2
        ]
      },
      {
        "text": "C503",
        "bbox": [
          666.5,
          270.5,
          669.8,
          279.4
        ]
      },
      {
        "text": "R501",
        "bbox": [
          670.7,
          270.6,
          674.0,
          279.6
        ]
      },
      {
        "text": "R300",
        "bbox": [
          660.0,
          284.3,
          669.0,
          287.6
        ]
      },
      {
        "text": "C304",
        "bbox": [
          663.9,
          295.2,
          667.2,
          304.2
        ]
      },
      {
        "text": "C303",
        "bbox": [
          680.3,
          294.3,
          683.6,
          303.3
        ]
      },
      {
        "text": "U300",
        "bbox": [
          668.7,
          297.4,
          677.4,
          300.6
        ]
      },
      {
        "text": "R307",
        "bbox": [
          660.8,
          306.6,
          664.1,
          315.6
        ]
      },
      {
        "text": "U303",
        "bbox": [
          665.2,
          306.8,
          674.2,
          310.1
        ]
      },
      {
        "text": "C314",
        "bbox": [
          674.8,
          306.4,
          683.8,
          309.8
        ]
      },
      {
        "text": "C306",
        "bbox": [
          664.8,
          312.6,
          673.7,
          315.9
        ]
      },
      {
        "text": "D303",
        "bbox": [
          655.6,
          318.0,
          658.9,
          326.9
        ]
      },
      {
        "text": "C313",
        "bbox": [
          660.0,
          318.3,
          663.3,
          327.2
        ]
      },
      {
        "text": "R311",
        "bbox": [
          663.9,
          317.7,
          667.2,
          326.7
        ]
      },
      {
        "text": "U302",
        "bbox": [
          669.3,
          316.3,
          672.6,
          325.2
        ]
      },
      {
        "text": "R310",
        "bbox": [
          658.7,
          327.5,
          667.7,
          330.8
        ]
      },
      {
        "text": "R309",
        "bbox": [
          658.8,
          331.4,
          667.8,
          334.8
        ]
      },
      {
        "text": "C310",
        "bbox": [
          655.5,
          327.0,
          658.9,
          335.9
        ]
      },
      {
        "text": "D404",
        "bbox": [
          651.1,
          509.5,
          672.1,
          517.3
        ]
      },
      {
        "text": "D400",
        "bbox": [
          644.4,
          537.0,
          665.4,
          544.8
        ]
      },
      {
        "text": "R312",
        "bbox": [
          674.4,
          310.5,
          683.3,
          313.8
        ]
      },
      {
        "text": "D304",
        "bbox": [
          674.2,
          314.0,
          682.9,
          322.6
        ]
      },
      {
        "text": "R303",
        "bbox": [
          683.0,
          432.1,
          686.2,
          440.7
        ]
      },
      {
        "text": "R302",
        "bbox": [
          683.0,
          449.1,
          686.2,
          457.7
        ]
      },
      {
        "text": "R301",
        "bbox": [
          683.2,
          465.2,
          686.4,
          473.8
        ]
      },
      {
        "text": "L1000",
        "bbox": [
          684.6,
          656.8,
          687.9,
          667.3
        ]
      },
      {
        "text": "C1001 C1000",
        "bbox": [
          684.6,
          647.2,
          687.9,
          677.2
        ]
      },
      {
        "text": "R500",
        "bbox": [
          675.9,
          258.8,
          684.9,
          262.1
        ]
      },
      {
        "text": "U500",
        "bbox": [
          675.1,
          267.1,
          684.0,
          270.4
        ]
      },
      {
        "text": "C504",
        "bbox": [
          674.5,
          275.3,
          683.5,
          278.6
        ]
      },
      {
        "text": "R503",
        "bbox": [
          674.4,
          279.6,
          683.3,
          282.9
        ]
      },
      {
        "text": "R508",
        "bbox": [
          685.5,
          257.6,
          688.8,
          266.5
        ]
      },
      {
        "text": "R507",
        "bbox": [
          685.5,
          266.5,
          688.8,
          275.5
        ]
      },
      {
        "text": "C",
        "bbox": [
          736.8,
          3.2,
          744.2,
          12.3
        ]
      },
      {
        "text": "D300",
        "bbox": [
          735.2,
          497.6,
          749.1,
          502.7
        ]
      },
      {
        "text": "D301",
        "bbox": [
          735.2,
          513.9,
          749.1,
          519.0
        ]
      },
      {
        "text": "Status",
        "bbox": [
          696.1,
          746.6,
          717.4,
          753.3
        ]
      },
      {
        "text": "Document type",
        "bbox": [
          696.1,
          774.9,
          746.5,
          781.5
        ]
      },
      {
        "text": "Drawing",
        "bbox": [
          696.1,
          786.5,
          729.1,
          794.4
        ]
      },
      {
        "text": "No part of this document may be reproduced or transmitted in any form or by",
        "bbox": [
          696.1,
          801.4,
          848.6,
          805.4
        ]
      },
      {
        "text": "any means, electronic or mechanical, including photocopying, recording or",
        "bbox": [
          696.1,
          806.6,
          843.9,
          810.6
        ]
      },
      {
        "text": "otherwise, without prior written permission. Any infringement shall give rise",
        "bbox": [
          696.1,
          811.8,
          844.6,
          815.7
        ]
      },
      {
        "text": "to an obligation to pay damages. All rights reserved in the event of patent,",
        "bbox": [
          696.1,
          816.9,
          842.9,
          820.9
        ]
      },
      {
        "text": "utility model or design registration.",
        "bbox": [
          696.1,
          822.1,
          764.4,
          826.1
        ]
      },
      {
        "text": "C",
        "bbox": [
          736.8,
          830.7,
          744.2,
          839.8
        ]
      },
      {
        "text": "Created Date Name",
        "bbox": [
          852.0,
          760.8,
          878.7,
          767.5
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887.5,
          760.8,
          925.0,
          767.5
        ]
      },
      {
        "text": "T. Ripplinger",
        "bbox": [
          930.0,
          760.8,
          972.5,
          767.4
        ]
      },
      {
        "text": "Checked",
        "bbox": [
          852.0,
          774.9,
          881.6,
          781.5
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887.5,
          775.0,
          925.0,
          781.6
        ]
      },
      {
        "text": "D.Sauter",
        "bbox": [
          930.0,
          774.9,
          959.6,
          781.5
        ]
      },
      {
        "text": "Elektromedizin GmbH",
        "bbox": [
          870.6,
          816.9,
          958.1,
          824.9
        ]
      },
      {
        "text": "Project",
        "bbox": [
          979.6,
          746.6,
          1002.9,
          753.3
        ]
      },
      {
        "text": "PB HW",
        "bbox": [
          979.6,
          760.2,
          1009.1,
          768.2
        ]
      },
      {
        "text": "Title",
        "bbox": [
          979.6,
          775.0,
          993.8,
          781.6
        ]
      },
      {
        "text": "Assembly Drawing",
        "bbox": [
          979.6,
          788.6,
          1054.1,
          796.5
        ]
      },
      {
        "text": "Schematic Revision",
        "bbox": [
          979.3,
          803.3,
          1045.1,
          810.0
        ]
      },
      {
        "text": "004",
        "bbox": [
          1063.1,
          803.3,
          1075.6,
          810.0
        ]
      },
      {
        "text": "Layout Revision EENr Assy EENr PCB",
        "bbox": [
          979.3,
          817.5,
          1032.6,
          824.1
        ]
      },
      {
        "text": "30160-860 40160-860",
        "bbox": [
          1094.8,
          760.8,
          1173.0,
          767.5
        ]
      },
      {
        "text": "Size",
        "bbox": [
          1135.5,
          775.0,
          1150.1,
          781.6
        ]
      },
      {
        "text": "A3",
        "bbox": [
          1149.6,
          788.6,
          1160.6,
          796.5
        ]
      },
      {
        "text": "Sheet",
        "bbox": [
          1135.5,
          803.3,
          1155.1,
          810.0
        ]
      },
      {
        "text": "04.04.2023",
        "bbox": [
          1063.2,
          817.5,
          1100.7,
          824.1
        ]
      },
      {
        "text": "6 of 7",
        "bbox": [
          1146.5,
          817.5,
          1165.2,
          824.1
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027.2,
          830.7,
          1034.7,
          839.8
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027.2,
          3.2,
          1034.7,
          12.3
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
          826.2,
          68.2,
          834.8,
          76.7
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          421.2,
          74.0,
          432.5,
          85.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          448.8,
          75.6,
          457.3,
          84.1
        ]
      },
      {
        "text": "1",
        "bbox": [
          4.3,
          112.0,
          10.1,
          121.2
        ]
      },
      {
        "text": "1",
        "bbox": [
          1180.5,
          112.0,
          1186.2,
          121.2
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          751.7,
          154.5,
          760.2,
          163.0
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          809.3,
          212.1,
          817.8,
          220.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          221.6,
          253.8,
          236.6,
          268.8
        ]
      },
      {
        "text": "2",
        "bbox": [
          4.3,
          315.3,
          10.1,
          324.4
        ]
      },
      {
        "text": "2",
        "bbox": [
          1180.5,
          315.3,
          1186.2,
          324.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          830.6,
          449.5,
          839.3,
          458.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          821.4,
          460.6,
          830.5,
          469.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          671.3,
          461.1,
          686.4,
          476.1
        ]
      },
      {
        "text": "3",
        "bbox": [
          4.3,
          518.6,
          10.1,
          527.7
        ]
      },
      {
        "text": "3",
        "bbox": [
          1180.5,
          518.6,
          1186.2,
          527.7
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          764.1,
          636.0,
          784.4,
          660.9
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          741.1,
          636.0,
          766.0,
          660.9
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          744.6,
          636.0,
          769.5,
          660.9
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          748.2,
          636.0,
          773.0,
          660.9
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          751.7,
          636.0,
          776.6,
          660.9
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          755.2,
          636.0,
          780.1,
          660.9
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          758.8,
          636.0,
          783.6,
          660.9
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          769.4,
          636.0,
          794.2,
          660.9
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          772.9,
          636.0,
          797.7,
          660.9
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          776.4,
          636.0,
          801.3,
          660.9
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          779.9,
          636.0,
          804.8,
          660.9
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          783.5,
          636.0,
          808.3,
          660.9
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          495.9,
          669.7,
          507.2,
          681.1
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          236.2,
          713.4,
          244.7,
          721.9
        ]
      },
      {
        "text": "4",
        "bbox": [
          4.3,
          721.9,
          10.1,
          731.0
        ]
      },
      {
        "text": "4",
        "bbox": [
          1180.5,
          721.9,
          1186.2,
          731.0
        ]
      },
      {
        "text": "A",
        "bbox": [
          156.2,
          3.2,
          163.1,
          12.3
        ]
      },
      {
        "text": "A",
        "bbox": [
          156.2,
          830.7,
          163.1,
          839.8
        ]
      },
      {
        "text": "Labeling Top side (Scale 1:1)",
        "bbox": [
          212.1,
          55.6,
          348.6,
          64.9
        ]
      },
      {
        "text": "Designator11",
        "bbox": [
          251.8,
          211.8,
          255.1,
          234.2
        ]
      },
      {
        "text": "C301",
        "bbox": [
          311.2,
          246.8,
          332.2,
          254.6
        ]
      },
      {
        "text": "C302",
        "bbox": [
          311.3,
          300.4,
          332.3,
          308.2
        ]
      },
      {
        "text": "J300",
        "bbox": [
          326.5,
          484.0,
          334.3,
          503.1
        ]
      },
      {
        "text": "J1000",
        "bbox": [
          330.5,
          669.2,
          338.2,
          693.2
        ]
      },
      {
        "text": "L301",
        "bbox": [
          253.7,
          348.0,
          261.4,
          367.5
        ]
      },
      {
        "text": "K300",
        "bbox": [
          244.6,
          444.9,
          265.2,
          452.7
        ]
      },
      {
        "text": "C318",
        "bbox": [
          240.2,
          477.4,
          261.2,
          485.2
        ]
      },
      {
        "text": "L300",
        "bbox": [
          243.2,
          522.0,
          262.8,
          529.8
        ]
      },
      {
        "text": "C317",
        "bbox": [
          240.7,
          567.6,
          261.7,
          575.3
        ]
      },
      {
        "text": "J301",
        "bbox": [
          237.3,
          614.0,
          256.4,
          621.8
        ]
      },
      {
        "text": "SW300",
        "bbox": [
          248.5,
          684.3,
          256.3,
          713.1
        ]
      },
      {
        "text": "SW300",
        "bbox": [
          248.5,
          684.3,
          256.3,
          713.1
        ]
      },
      {
        "text": "FID100",
        "bbox": [
          234.3,
          716.2,
          246.6,
          719.5
        ]
      },
      {
        "text": "RV300",
        "bbox": [
          289.7,
          613.3,
          297.4,
          640.2
        ]
      },
      {
        "text": "R318",
        "bbox": [
          301.4,
          514.1,
          309.1,
          535.1
        ]
      },
      {
        "text": "J1103",
        "bbox": [
          380.3,
          227.2,
          388.1,
          251.2
        ]
      },
      {
        "text": "C404",
        "bbox": [
          394.7,
          375.4,
          416.9,
          387.4
        ]
      },
      {
        "text": "B",
        "bbox": [
          446.6,
          3.2,
          453.5,
          12.3
        ]
      },
      {
        "text": "FID101",
        "bbox": [
          451.6,
          73.7,
          454.9,
          86.0
        ]
      },
      {
        "text": "HS403",
        "bbox": [
          422.4,
          409.6,
          449.3,
          417.4
        ]
      },
      {
        "text": "D401",
        "bbox": [
          440.5,
          402.5,
          448.3,
          423.5
        ]
      },
      {
        "text": "J1500",
        "bbox": [
          462.7,
          226.3,
          470.5,
          250.3
        ]
      },
      {
        "text": "HS400",
        "bbox": [
          468.5,
          409.8,
          495.4,
          417.5
        ]
      },
      {
        "text": "D402",
        "bbox": [
          486.6,
          402.6,
          494.4,
          423.7
        ]
      },
      {
        "text": "HS402 HS401",
        "bbox": [
          422.4,
          456.9,
          495.4,
          464.9
        ]
      },
      {
        "text": "D405",
        "bbox": [
          440.5,
          449.8,
          448.3,
          470.9
        ]
      },
      {
        "text": "D403",
        "bbox": [
          486.6,
          450.0,
          494.4,
          471.0
        ]
      },
      {
        "text": "T400",
        "bbox": [
          456.3,
          555.4,
          464.1,
          575.5
        ]
      },
      {
        "text": "L402",
        "bbox": [
          420.0,
          658.3,
          439.6,
          666.0
        ]
      },
      {
        "text": "B",
        "bbox": [
          446.6,
          830.7,
          453.5,
          839.8
        ]
      },
      {
        "text": "R401",
        "bbox": [
          505.2,
          415.9,
          513.0,
          436.9
        ]
      },
      {
        "text": "R400",
        "bbox": [
          508.5,
          553.9,
          516.3,
          575.0
        ]
      },
      {
        "text": "L1201",
        "bbox": [
          517.9,
          93.5,
          542.4,
          101.2
        ]
      },
      {
        "text": "JP1203",
        "bbox": [
          519.4,
          90.5,
          522.8,
          103.2
        ]
      },
      {
        "text": "JP1202",
        "bbox": [
          534.2,
          90.5,
          537.5,
          103.2
        ]
      },
      {
        "text": "JP1201",
        "bbox": [
          523.3,
          90.5,
          526.6,
          103.2
        ]
      },
      {
        "text": "JP1200",
        "bbox": [
          538.0,
          90.5,
          541.3,
          103.2
        ]
      },
      {
        "text": "C1204",
        "bbox": [
          528.3,
          172.8,
          536.1,
          198.7
        ]
      },
      {
        "text": "C401",
        "bbox": [
          558.2,
          311.4,
          579.2,
          319.2
        ]
      },
      {
        "text": "L403",
        "bbox": [
          553.8,
          374.4,
          573.4,
          382.2
        ]
      },
      {
        "text": "L404",
        "bbox": [
          537.5,
          456.7,
          545.3,
          476.2
        ]
      },
      {
        "text": "L400",
        "bbox": [
          600.8,
          456.7,
          608.5,
          476.2
        ]
      },
      {
        "text": "C206",
        "bbox": [
          556.2,
          586.5,
          571.3,
          608.9
        ]
      },
      {
        "text": "C206",
        "bbox": [
          556.2,
          586.5,
          571.3,
          608.9
        ]
      },
      {
        "text": "Q200",
        "bbox": [
          578.7,
          629.8,
          594.2,
          652.6
        ]
      },
      {
        "text": "R1301",
        "bbox": [
          627.6,
          345.9,
          638.1,
          372.5
        ]
      },
      {
        "text": "C200",
        "bbox": [
          624.7,
          544.2,
          647.1,
          559.3
        ]
      },
      {
        "text": "C200",
        "bbox": [
          624.7,
          544.2,
          647.1,
          559.3
        ]
      },
      {
        "text": "T1200",
        "bbox": [
          649.5,
          164.6,
          657.3,
          189.6
        ]
      },
      {
        "text": "T200",
        "bbox": [
          652.1,
          608.3,
          673.6,
          623.3
        ]
      },
      {
        "text": "T200",
        "bbox": [
          652.1,
          608.3,
          673.6,
          623.3
        ]
      },
      {
        "text": "K1204",
        "bbox": [
          674.0,
          302.2,
          684.8,
          328.4
        ]
      },
      {
        "text": "K1203",
        "bbox": [
          711.1,
          306.7,
          721.9,
          332.9
        ]
      },
      {
        "text": "C",
        "bbox": [
          736.8,
          3.2,
          744.2,
          12.3
        ]
      },
      {
        "text": "K1202",
        "bbox": [
          747.9,
          311.2,
          758.8,
          337.4
        ]
      },
      {
        "text": "C1201",
        "bbox": [
          773.2,
          89.9,
          800.0,
          107.9
        ]
      },
      {
        "text": "L1200",
        "bbox": [
          781.3,
          175.2,
          789.1,
          199.6
        ]
      },
      {
        "text": "K1205",
        "bbox": [
          783.9,
          324.9,
          794.8,
          351.1
        ]
      },
      {
        "text": "C216",
        "bbox": [
          754.5,
          522.9,
          769.9,
          545.3
        ]
      },
      {
        "text": "C215 C214",
        "bbox": [
          732.2,
          559.4,
          792.3,
          592.5
        ]
      },
      {
        "text": "J1104",
        "bbox": [
          770.9,
          636.4,
          778.6,
          660.4
        ]
      },
      {
        "text": "Status",
        "bbox": [
          696.1,
          746.6,
          717.4,
          753.3
        ]
      },
      {
        "text": "Document type",
        "bbox": [
          696.1,
          774.9,
          746.5,
          781.5
        ]
      },
      {
        "text": "Drawing",
        "bbox": [
          696.1,
          786.5,
          729.1,
          794.4
        ]
      },
      {
        "text": "No part of this document may be reproduced or transmitted in any form or by",
        "bbox": [
          696.1,
          801.4,
          848.6,
          805.4
        ]
      },
      {
        "text": "any means, electronic or mechanical, including photocopying, recording or",
        "bbox": [
          696.1,
          806.6,
          843.9,
          810.6
        ]
      },
      {
        "text": "otherwise, without prior written permission. Any infringement shall give rise",
        "bbox": [
          696.1,
          811.8,
          844.6,
          815.7
        ]
      },
      {
        "text": "to an obligation to pay damages. All rights reserved in the event of patent,",
        "bbox": [
          696.1,
          816.9,
          842.9,
          820.9
        ]
      },
      {
        "text": "utility model or design registration.",
        "bbox": [
          696.1,
          822.1,
          764.4,
          826.1
        ]
      },
      {
        "text": "C",
        "bbox": [
          736.8,
          830.7,
          744.2,
          839.8
        ]
      },
      {
        "text": "L203",
        "bbox": [
          807.5,
          518.0,
          822.3,
          539.1
        ]
      },
      {
        "text": "J1102",
        "bbox": [
          797.8,
          646.0,
          821.8,
          653.8
        ]
      },
      {
        "text": "FID102",
        "bbox": [
          829.0,
          66.3,
          832.4,
          78.6
        ]
      },
      {
        "text": "K1200",
        "bbox": [
          829.9,
          322.3,
          840.7,
          348.5
        ]
      },
      {
        "text": "R1200",
        "bbox": [
          845.5,
          90.3,
          871.8,
          110.0
        ]
      },
      {
        "text": "R1201",
        "bbox": [
          842.1,
          141.0,
          868.4,
          160.7
        ]
      },
      {
        "text": "C1203",
        "bbox": [
          844.0,
          213.3,
          851.8,
          239.2
        ]
      },
      {
        "text": "C1200",
        "bbox": [
          876.0,
          213.3,
          883.8,
          239.2
        ]
      },
      {
        "text": "C1202",
        "bbox": [
          842.3,
          274.3,
          868.3,
          282.1
        ]
      },
      {
        "text": "K1201",
        "bbox": [
          867.0,
          326.8,
          877.8,
          353.0
        ]
      },
      {
        "text": "C213",
        "bbox": [
          846.9,
          508.2,
          869.3,
          523.5
        ]
      },
      {
        "text": "J1101",
        "bbox": [
          866.2,
          628.8,
          874.0,
          652.8
        ]
      },
      {
        "text": "Created J1600",
        "bbox": [
          852.0,
          760.8,
          878.7,
          767.5
        ]
      },
      {
        "text": "J1601",
        "bbox": [
          910.1,
          109.0,
          917.9,
          133.0
        ]
      },
      {
        "text": "J1401",
        "bbox": [
          910.4,
          196.4,
          918.2,
          220.4
        ]
      },
      {
        "text": "J1400",
        "bbox": [
          910.0,
          444.4,
          917.8,
          468.4
        ]
      },
      {
        "text": "J1100",
        "bbox": [
          915.1,
          591.2,
          922.9,
          615.1
        ]
      },
      {
        "text": "Date Name",
        "bbox": [
          887.5,
          746.6,
          903.3,
          753.3
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887.5,
          760.8,
          925.0,
          767.5
        ]
      },
      {
        "text": "T. Ripplinger",
        "bbox": [
          930.0,
          760.8,
          972.5,
          767.4
        ]
      },
      {
        "text": "Checked",
        "bbox": [
          852.0,
          774.9,
          881.6,
          781.5
        ]
      },
      {
        "text": "05.08.2026",
        "bbox": [
          887.5,
          775.0,
          925.0,
          781.6
        ]
      },
      {
        "text": "D.Sauter",
        "bbox": [
          930.0,
          774.9,
          959.6,
          781.5
        ]
      },
      {
        "text": "Elektromedizin GmbH",
        "bbox": [
          870.6,
          816.9,
          958.1,
          824.9
        ]
      },
      {
        "text": "Project",
        "bbox": [
          979.6,
          746.6,
          1002.9,
          753.3
        ]
      },
      {
        "text": "PB HW",
        "bbox": [
          979.6,
          760.2,
          1009.1,
          768.2
        ]
      },
      {
        "text": "Title",
        "bbox": [
          979.6,
          775.0,
          993.8,
          781.6
        ]
      },
      {
        "text": "Assembly Drawing",
        "bbox": [
          979.6,
          788.6,
          1054.1,
          796.5
        ]
      },
      {
        "text": "Schematic Revision",
        "bbox": [
          979.3,
          803.3,
          1045.1,
          810.0
        ]
      },
      {
        "text": "004",
        "bbox": [
          1063.1,
          803.3,
          1075.6,
          810.0
        ]
      },
      {
        "text": "Layout Revision EENr Assy EENr PCB",
        "bbox": [
          979.3,
          817.5,
          1032.6,
          824.1
        ]
      },
      {
        "text": "30160-860 40160-860",
        "bbox": [
          1094.8,
          760.8,
          1173.0,
          767.5
        ]
      },
      {
        "text": "Size",
        "bbox": [
          1135.5,
          775.0,
          1150.1,
          781.6
        ]
      },
      {
        "text": "A3",
        "bbox": [
          1149.6,
          788.6,
          1160.6,
          796.5
        ]
      },
      {
        "text": "Sheet",
        "bbox": [
          1135.5,
          803.3,
          1155.1,
          810.0
        ]
      },
      {
        "text": "04.04.2023",
        "bbox": [
          1063.2,
          817.5,
          1100.7,
          824.1
        ]
      },
      {
        "text": "7 of 7",
        "bbox": [
          1146.5,
          817.5,
          1165.2,
          824.1
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027.2,
          830.7,
          1034.7,
          839.8
        ]
      },
      {
        "text": "D",
        "bbox": [
          1027.2,
          3.2,
          1034.7,
          12.3
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
          19.8,
          53.9,
          39.3,
          59.6
        ]
      },
      {
        "text": "6520001",
        "bbox": [
          144.5,
          53.9,
          169.3,
          59.6
        ]
      },
      {
        "text": "25241",
        "bbox": [
          260.8,
          53.9,
          278.4,
          59.6
        ]
      },
      {
        "text": "Document class Document number",
        "bbox": [
          19.8,
          64.6,
          65.2,
          70.2
        ]
      },
      {
        "text": "Packaging Specification D275036 Version: 000",
        "bbox": [
          19.8,
          77.2,
          86.0,
          82.8
        ]
      },
      {
        "text": "Packaging specification/Verpackungsvorschrift",
        "bbox": [
          62.4,
          110.0,
          371.8,
          123.0
        ]
      },
      {
        "text": "This packaging specification applies to/Diese Verpackungsvorschrift ist anzuwenden für:",
        "bbox": [
          62.4,
          154.8,
          481.9,
          164.2
        ]
      },
      {
        "text": "Erbe article no./Erbe Artikel Nr.:",
        "bbox": [
          62.4,
          182.7,
          205.3,
          191.7
        ]
      },
      {
        "text": "Designation/Bezeichnung:",
        "bbox": [
          62.4,
          196.2,
          178.9,
          205.1
        ]
      },
      {
        "text": "30160-860",
        "bbox": [
          239.4,
          182.8,
          287.4,
          191.7
        ]
      },
      {
        "text": "PB HW VIO 3n PowerBoard",
        "bbox": [
          239.4,
          196.2,
          360.7,
          205.1
        ]
      },
      {
        "text": "Image of packaging (not mandatory)/Abbildung der Verpackung (nicht zwingend erforderlich):",
        "bbox": [
          62.4,
          303.8,
          511.6,
          313.1
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
          19.8,
          41.2,
          58.4,
          46.8
        ]
      },
      {
        "text": "Aurora Project number Change number",
        "bbox": [
          19.8,
          53.9,
          39.3,
          59.6
        ]
      },
      {
        "text": "6520001",
        "bbox": [
          144.5,
          53.9,
          169.3,
          59.6
        ]
      },
      {
        "text": "25241",
        "bbox": [
          260.8,
          53.9,
          278.4,
          59.6
        ]
      },
      {
        "text": "Document class Document number",
        "bbox": [
          19.8,
          64.6,
          65.2,
          70.2
        ]
      },
      {
        "text": "Packaging Specification D275036 Version: 000",
        "bbox": [
          19.8,
          77.2,
          86.0,
          82.8
        ]
      },
      {
        "text": "Delivery conditions/Anlieferbedingungen:",
        "bbox": [
          62.4,
          108.5,
          262.9,
          117.8
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          452.9,
          135.1,
          464.0,
          146.3
        ]
      },
      {
        "text": "Delivery on pallet mandatory/Anlieferung auf Palette zwingend erforderlich:",
        "bbox": [
          62.4,
          137.2,
          445.2,
          146.5
        ]
      },
      {
        "text": "Yes/Ja",
        "bbox": [
          467.7,
          137.5,
          496.4,
          146.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          452.9,
          149.2,
          464.0,
          160.3
        ]
      },
      {
        "text": "No/Nein",
        "bbox": [
          467.7,
          151.5,
          505.6,
          160.5
        ]
      },
      {
        "text": "Pallet dimensions/Palettenabmaße:",
        "bbox": [
          82.0,
          165.0,
          242.1,
          173.9
        ]
      },
      {
        "text": "Length/Länge: 1,2 Meter(s)",
        "bbox": [
          82.0,
          178.4,
          223.9,
          187.4
        ]
      },
      {
        "text": "Width/Breite:",
        "bbox": [
          82.0,
          191.8,
          143.2,
          200.8
        ]
      },
      {
        "text": "0,8 Meter(s)",
        "bbox": [
          168.6,
          191.9,
          223.9,
          200.8
        ]
      },
      {
        "text": "Height/Höhe:",
        "bbox": [
          82.0,
          205.3,
          142.2,
          214.2
        ]
      },
      {
        "text": "1,4 Meter(s)",
        "bbox": [
          168.7,
          205.3,
          223.9,
          214.2
        ]
      },
      {
        "text": "Specifications/Spezifikationen",
        "bbox": [
          62.4,
          233.8,
          224.4,
          243.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          417.5,
          260.8,
          428.6,
          271.9
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          474.4,
          260.8,
          485.5,
          271.9
        ]
      },
      {
        "text": "To be supplied in ESD packaging/Anlieferung in ESD-Verpackung:",
        "bbox": [
          80.4,
          263.1,
          369.1,
          272.1
        ]
      },
      {
        "text": "Yes/Ja No/Nein",
        "bbox": [
          432.3,
          263.1,
          527.1,
          272.1
        ]
      },
      {
        "text": "To be supplied in cleanroom compatible packaging/Anlieferung in Reinraum-geeigneter Verpackung:",
        "bbox": [
          80.0,
          277.1,
          373.1,
          300.1
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          417.5,
          288.7,
          428.6,
          299.9
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          474.4,
          288.7,
          485.5,
          299.9
        ]
      },
      {
        "text": "Packaging levels/Verpackungsebenen",
        "bbox": [
          62.4,
          318.8,
          259.7,
          328.1
        ]
      },
      {
        "text": "Packaging level 0 is the smallest packing unit and must always be defined. If required, higher packaging levels can be defined.",
        "bbox": [
          80.3,
          347.1,
          493.2,
          370.1
        ]
      },
      {
        "text": "Verpackungsebene 0 ist die kleinste Verpackungseinheit und ist in jedem Fall zu definieren - Bei Bedarf können zusätzlich höhere Verpackungsebenen definiert werden.",
        "bbox": [
          80.4,
          375.2,
          502.5,
          398.1
        ]
      },
      {
        "text": "Packaging level 0/Verpackungsebene 0:",
        "bbox": [
          97.8,
          417.0,
          286.7,
          426.7
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          169.7,
          429.5,
          180.8,
          440.6
        ]
      },
      {
        "text": "Type/Art:",
        "bbox": [
          97.8,
          431.9,
          140.5,
          440.8
        ]
      },
      {
        "text": "Reusable packaging/Mehrwegbehälter",
        "bbox": [
          184.5,
          431.9,
          356.9,
          440.8
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          169.7,
          443.5,
          180.8,
          454.7
        ]
      },
      {
        "text": "Cardboard/Kartonage",
        "bbox": [
          184.5,
          445.9,
          282.7,
          454.9
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          169.7,
          457.4,
          180.8,
          468.6
        ]
      },
      {
        "text": "Bag/Beutel",
        "bbox": [
          184.5,
          459.8,
          233.6,
          468.8
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          169.7,
          471.5,
          180.8,
          482.6
        ]
      },
      {
        "text": "Other/Sonstiges:",
        "bbox": [
          184.5,
          473.9,
          259.8,
          482.8
        ]
      },
      {
        "text": "Content quantity of packaging level 0 in pcs./Inhaltsmenge der Verpackungsebene 0 in Stk: 4",
        "bbox": [
          97.8,
          501.8,
          510.0,
          510.8
        ]
      },
      {
        "text": "Dimensions of packaging level 0/Abmessungen der Verpackungsebene 0:",
        "bbox": [
          97.8,
          529.9,
          422.0,
          538.9
        ]
      },
      {
        "text": "Length/Länge: 400 mm Width/Breite: 300 mm Height/Höhe: 320 mm",
        "bbox": [
          97.8,
          543.2,
          488.7,
          552.2
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          452.9,
          567.7,
          464.0,
          578.9
        ]
      },
      {
        "text": "Label on packaging level 0/Kennzeichnung der Verpackungsebene 0 mit Label:",
        "bbox": [
          97.6,
          570.1,
          444.2,
          579.0
        ]
      },
      {
        "text": "Yes/Ja",
        "bbox": [
          467.7,
          570.1,
          496.4,
          579.0
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          452.9,
          581.2,
          464.0,
          592.3
        ]
      },
      {
        "text": "No/Nein",
        "bbox": [
          467.7,
          583.5,
          505.6,
          592.5
        ]
      },
      {
        "text": "Yes/Ja No/Nein",
        "bbox": [
          432.3,
          291.1,
          527.1,
          300.1
        ]
      },
      {
        "text": "Content of the label/Labelinhalt:",
        "bbox": [
          97.6,
          610.4,
          243.3,
          619.4
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          162.7,
          621.5,
          173.9,
          632.6
        ]
      },
      {
        "text": "Erbe article no./Erbe-Artikel Nr.",
        "bbox": [
          177.6,
          623.9,
          318.4,
          632.8
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          162.7,
          634.9,
          173.9,
          646.1
        ]
      },
      {
        "text": "Designation/Bezeichnung",
        "bbox": [
          177.6,
          637.3,
          291.3,
          646.2
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          162.7,
          648.4,
          173.9,
          659.5
        ]
      },
      {
        "text": "Quantity/Menge",
        "bbox": [
          177.6,
          650.7,
          252.3,
          659.7
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          162.7,
          661.7,
          173.9,
          672.8
        ]
      },
      {
        "text": "Lot no. or SN/Lot- bzw. SN",
        "bbox": [
          177.6,
          664.0,
          294.6,
          673.0
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          162.7,
          675.1,
          173.9,
          686.3
        ]
      },
      {
        "text": "Expiry date or Manufacturing date/Mindesthaltbarkeitsdatum bzw.",
        "bbox": [
          177.6,
          677.5,
          477.9,
          686.5
        ]
      },
      {
        "text": "Herstelldatum",
        "bbox": [
          176.6,
          690.9,
          240.3,
          699.9
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          162.7,
          702.0,
          173.9,
          713.2
        ]
      },
      {
        "text": "Barcode",
        "bbox": [
          177.6,
          704.4,
          214.4,
          713.3
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          276.1,
          718.3,
          287.3,
          729.5
        ]
      },
      {
        "text": " Content/Inhalt:",
        "bbox": [
          179.2,
          720.0,
          261.6,
          729.6
        ]
      },
      {
        "text": "Erbe article no./Erbe Artikel Nr. +",
        "bbox": [
          291.0,
          718.8,
          440.3,
          730.2
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          276.1,
          735.5,
          287.3,
          746.6
        ]
      },
      {
        "text": "Other/Sonstiges:",
        "bbox": [
          161.6,
          752.0,
          236.9,
          761.0
        ]
      },
      {
        "text": "Lot no. or SN/Lot- bzw. SN +",
        "bbox": [
          291.0,
          736.0,
          419.9,
          747.3
        ]
      },
      {
        "text": "FB_0526_Packaging specification/Verpackungsvorschrift",
        "bbox": [
          310.0,
          784.0,
          567.4,
          792.9
        ]
      },
      {
        "text": "Page:",
        "bbox": [
          514.8,
          798.6,
          530.3,
          804.3
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
          19.8,
          41.2,
          58.4,
          46.8
        ]
      },
      {
        "text": "Aurora Project number Change number",
        "bbox": [
          19.8,
          53.9,
          39.3,
          59.6
        ]
      },
      {
        "text": "6520001",
        "bbox": [
          144.5,
          53.9,
          169.3,
          59.6
        ]
      },
      {
        "text": "25241",
        "bbox": [
          260.8,
          53.9,
          278.4,
          59.6
        ]
      },
      {
        "text": "Document class Document number",
        "bbox": [
          19.8,
          64.6,
          65.2,
          70.2
        ]
      },
      {
        "text": "Packaging Specification D275036 Version: 000",
        "bbox": [
          19.8,
          77.2,
          86.0,
          82.8
        ]
      },
      {
        "text": "Packaging level 1/Verpackungsebene 1:",
        "bbox": [
          97.8,
          122.6,
          286.7,
          132.3
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          169.7,
          135.1,
          180.8,
          146.3
        ]
      },
      {
        "text": "Type/Art:",
        "bbox": [
          97.8,
          137.5,
          140.5,
          146.4
        ]
      },
      {
        "text": "Reusable packaging/Mehrwegbehälter",
        "bbox": [
          184.5,
          137.5,
          356.9,
          146.4
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          169.7,
          149.2,
          180.8,
          160.3
        ]
      },
      {
        "text": "Cardboard/Kartonage",
        "bbox": [
          184.5,
          151.5,
          282.7,
          160.5
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          169.7,
          163.1,
          180.8,
          174.2
        ]
      },
      {
        "text": "Bag/Beutel",
        "bbox": [
          184.5,
          165.4,
          233.6,
          174.4
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          169.7,
          177.1,
          180.8,
          188.3
        ]
      },
      {
        "text": "Other/Sonstiges:",
        "bbox": [
          184.5,
          179.5,
          259.8,
          188.4
        ]
      },
      {
        "text": "Content quantity of packaging level 1 in pcs./Inhaltsmenge der Verpackungsebene 1 in Stk:",
        "bbox": [
          97.8,
          207.4,
          501.9,
          216.4
        ]
      },
      {
        "text": "Dimensions of packaging level 1/Abmessungen der Verpackungsebene 1:",
        "bbox": [
          97.8,
          235.5,
          422.0,
          244.5
        ]
      },
      {
        "text": "Length/Länge:",
        "bbox": [
          97.8,
          249.0,
          162.4,
          257.9
        ]
      },
      {
        "text": "mm Width/Breite:",
        "bbox": [
          198.4,
          249.0,
          300.7,
          257.9
        ]
      },
      {
        "text": "mm Height/Höhe:",
        "bbox": [
          340.1,
          249.0,
          441.2,
          257.9
        ]
      },
      {
        "text": "mm",
        "bbox": [
          481.7,
          249.0,
          499.2,
          257.9
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          452.9,
          273.5,
          464.0,
          284.6
        ]
      },
      {
        "text": "Label on packaging level 1/Kennzeichnung der Verpackungsebene 1 mit Label:",
        "bbox": [
          97.6,
          275.9,
          444.2,
          284.8
        ]
      },
      {
        "text": "Yes/Ja",
        "bbox": [
          467.7,
          275.9,
          496.4,
          284.8
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          452.9,
          286.8,
          464.0,
          298.0
        ]
      },
      {
        "text": "No/Nein",
        "bbox": [
          467.7,
          289.2,
          505.6,
          298.1
        ]
      },
      {
        "text": "Content of the label/Labelinhalt:",
        "bbox": [
          97.6,
          316.1,
          243.3,
          325.0
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          162.7,
          327.1,
          173.9,
          338.3
        ]
      },
      {
        "text": "Erbe article no./Erbe-Artikel Nr.",
        "bbox": [
          177.6,
          329.5,
          318.4,
          338.4
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          162.7,
          340.6,
          173.9,
          351.7
        ]
      },
      {
        "text": "Designation/Bezeichnung",
        "bbox": [
          177.6,
          342.9,
          291.3,
          351.9
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          162.7,
          354.0,
          173.9,
          365.2
        ]
      },
      {
        "text": "Quantity/Menge",
        "bbox": [
          177.6,
          356.4,
          252.3,
          365.3
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          162.7,
          367.4,
          173.9,
          378.6
        ]
      },
      {
        "text": "Lot no. or SN/Lot- bzw. SN",
        "bbox": [
          177.6,
          369.8,
          294.6,
          378.8
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          162.7,
          380.9,
          173.9,
          392.0
        ]
      },
      {
        "text": "Expiry date or Manufacturing date/Mindesthaltbarkeitsdatum bzw. Herstelldatum",
        "bbox": [
          176.6,
          383.2,
          477.9,
          405.6
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          162.7,
          407.6,
          173.9,
          418.8
        ]
      },
      {
        "text": "Barcode",
        "bbox": [
          177.6,
          410.0,
          214.4,
          419.0
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          276.1,
          424.0,
          287.3,
          435.1
        ]
      },
      {
        "text": " Content/Inhalt:",
        "bbox": [
          179.0,
          425.6,
          261.6,
          435.3
        ]
      },
      {
        "text": "Erbe article no./Erbe Artikel Nr. +",
        "bbox": [
          291.0,
          424.5,
          440.3,
          435.8
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          276.1,
          441.1,
          287.3,
          452.3
        ]
      },
      {
        "text": "Other/Sonstiges:",
        "bbox": [
          161.6,
          457.6,
          236.9,
          466.6
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          98.6,
          483.2,
          109.8,
          494.4
        ]
      },
      {
        "text": "Additional packaging levels/weitere Verpackungsebenen:",
        "bbox": [
          116.0,
          485.3,
          389.8,
          494.6
        ]
      },
      {
        "text": "Article/Einzelartikel",
        "bbox": [
          62.4,
          634.2,
          175.2,
          643.6
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          417.5,
          645.7,
          428.6,
          656.9
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          479.4,
          645.7,
          490.6,
          656.9
        ]
      },
      {
        "text": "Label on article/Kennzeichnung des Einzelartikel mit Label:",
        "bbox": [
          97.6,
          648.1,
          358.1,
          657.0
        ]
      },
      {
        "text": "Yes/Ja",
        "bbox": [
          432.3,
          648.1,
          461.0,
          657.0
        ]
      },
      {
        "text": "No/Nein",
        "bbox": [
          494.3,
          648.1,
          532.0,
          657.0
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          233.6,
          672.5,
          244.8,
          683.6
        ]
      },
      {
        "text": "Label content/Labelinhalt:",
        "bbox": [
          97.4,
          674.9,
          215.1,
          683.8
        ]
      },
      {
        "text": "Erbe article no./Erbe-Artikel Nr.",
        "bbox": [
          248.5,
          674.9,
          389.3,
          683.8
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          233.6,
          685.9,
          244.8,
          697.1
        ]
      },
      {
        "text": "Designation/Bezeichnung",
        "bbox": [
          248.5,
          688.3,
          362.2,
          697.2
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          233.6,
          699.4,
          244.8,
          710.5
        ]
      },
      {
        "text": "Quantity/Menge",
        "bbox": [
          248.5,
          701.7,
          323.2,
          710.7
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          233.6,
          712.8,
          244.8,
          724.0
        ]
      },
      {
        "text": "Lot no. or SN/Lot- bzw. SN",
        "bbox": [
          248.5,
          715.2,
          365.6,
          724.1
        ]
      },
      {
        "text": "[ ]",
        "bbox": [
          233.6,
          726.2,
          244.8,
          737.4
        ]
      },
      {
        "text": "Expiry date or manufacturing date/Mindesthaltbarkeitsdatum bzw. Herstelldatum",
        "bbox": [
          247.5,
          728.6,
          525.0,
          751.0
        ]
      },
      {
        "text": "Lot no. or SN/Lot- bzw. SN +",
        "bbox": [
          291.0,
          441.6,
          419.9,
          453.0
        ]
      },
      {
        "text": "FB_0526_Packaging specification/Verpackungsvorschrift",
        "bbox": [
          310.0,
          784.0,
          567.4,
          792.9
        ]
      },
      {
        "text": "Page:",
        "bbox": [
          514.8,
          798.6,
          530.3,
          804.3
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
          19.8,
          53.9,
          39.3,
          59.6
        ]
      },
      {
        "text": "6520001",
        "bbox": [
          144.5,
          53.9,
          169.3,
          59.6
        ]
      },
      {
        "text": "25241",
        "bbox": [
          260.8,
          53.9,
          278.4,
          59.6
        ]
      },
      {
        "text": "Document class Document number",
        "bbox": [
          19.8,
          64.6,
          65.2,
          70.2
        ]
      },
      {
        "text": "Packaging Specification D275036 Version: 000",
        "bbox": [
          19.8,
          77.2,
          86.0,
          82.8
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          233.6,
          106.0,
          244.8,
          117.1
        ]
      },
      {
        "text": "Barcode",
        "bbox": [
          248.5,
          108.3,
          285.3,
          117.3
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          346.7,
          122.3,
          357.8,
          133.4
        ]
      },
      {
        "text": " Content/Inhalt:",
        "bbox": [
          250.0,
          123.9,
          332.5,
          133.6
        ]
      },
      {
        "text": "Erbe article no./Erbe Artikel Nr. +",
        "bbox": [
          361.5,
          122.8,
          510.9,
          134.1
        ]
      },
      {
        "text": "[X]",
        "bbox": [
          346.7,
          139.3,
          357.8,
          150.5
        ]
      },
      {
        "text": "Other/Sonstiges:",
        "bbox": [
          232.6,
          155.8,
          307.9,
          164.8
        ]
      },
      {
        "text": "Comments and additional information on transport and delivery conditions/Vermerke und Zusätze zu den Transport-, Lieferbedingungen:",
        "bbox": [
          62.4,
          197.6,
          494.4,
          220.9
        ]
      },
      {
        "text": "Pendelverpackung KLT ESD EG43/32 Schaumstoffeinlage inkl. Tray Deckel",
        "bbox": [
          62.4,
          238.9,
          225.9,
          261.3
        ]
      },
      {
        "text": "Lot no. or SN/Lot- bzw. SN +",
        "bbox": [
          361.5,
          139.8,
          490.5,
          151.2
        ]
      }
    ]
  }
]
