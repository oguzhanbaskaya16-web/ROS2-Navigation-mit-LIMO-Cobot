# Autonomes Greif-Szenario mit LIMO Cobot

## Zielsetzung

Der LIMO Cobot soll vollständig autonom einen Baustein erkennen, anfahren und greifen —
ohne manuellen Eingriff.

---

## Ablauf

```
1. Navigation  →  2. Suche  →  3. Auswahl  →  4. Ausrichten  →  5. Annähern  →  6. Greifen
```

**1. Navigation zum Zielpunkt**
Der Roboter fährt autonom zu einem vordefinierten Punkt in der Karte (Nav2 + AMCL).

**2. Suche nach den Bausteinen**
Am Zielpunkt dreht sich der Roboter langsam, bis die Kamera die trainierten Bausteine erkennt (YOLOv8).

**3. Auswahl des Ziel-Bausteins**
Sind mehrere Bausteine sichtbar, wählt der Roboter anhand eines definierten Kriteriums
(z. B. Nähe, Konfidenz der Erkennung) einen der beiden Bausteine als Ziel aus.

**4. Baustein ausrichten**
Der Roboter dreht sich feinjustiert, bis der Baustein mittig im Kamerabild liegt.

**5. Autonomes Annähern**
Der Roboter fährt auf den Baustein zu, bis ein definierter Greifabstand erreicht ist.
Die Ausrichtung wird dabei kontinuierlich gehalten.

**6. Automatisches Greifen**
Der Roboterarm (MyCobot) berechnet anhand der Kamerakoordinaten (XYZ) den Greifpunkt
und führt die Greifsequenz automatisch aus.

---

## Eingesetzte Technologien

| Komponente | Technologie |
|---|---|
| Autonome Navigation | ROS2 Nav2 + AMCL |
| Objekterkennung | YOLOv8 (trainiertes Modell) |
| Tiefenwahrnehmung | RealSense Tiefenkamera |
| Roboterarm | MyCobot (pymycobot) |
| Koordinaten-Transformation | Kamera → Arm (XYZ-Kalibrierung) |

