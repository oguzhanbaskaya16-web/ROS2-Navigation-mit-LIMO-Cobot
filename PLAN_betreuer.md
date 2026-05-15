# Autonomes Greif-Szenario mit LIMO Cobot

## Zielsetzung

Der LIMO Cobot soll vollständig autonom einen Baustein erkennen, anfahren und greifen —
ohne manuellen Eingriff.

---

## Ablauf

```
1. Navigation  →  2. Suche  →  3. Ausrichten  →  4. Annähern  →  5. Greifen
```

**1. Navigation zum Zielpunkt**
Der Roboter fährt autonom zu einem vordefinierten Punkt in der Karte (Nav2 + AMCL).

**2. Suche nach dem Baustein**
Am Zielpunkt dreht sich der Roboter langsam, bis die Kamera den trainierten Baustein erkennt (YOLOv8).

**3. Baustein ausrichten**
Der Roboter dreht sich feinjustiert, bis der Baustein mittig im Kamerabild liegt.

**4. Autonomes Annähern**
Der Roboter fährt auf den Baustein zu, bis ein definierter Greifabstand erreicht ist.
Die Ausrichtung wird dabei kontinuierlich gehalten.

**5. Automatisches Greifen**
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

---

## Vorhandene Basis

Das Projekt baut auf bestehenden Komponenten auf:
- Navigation und Kartierung sind bereits implementiert
- YOLOv8-Erkennung des Bausteins ist vorhanden
- Grundlegende Greifsequenz des Arms ist definiert

Neu entwickelt werden der übergeordnete Ablauf-Controller sowie die
Suchdrehung, Zentrierung und das autonome Annähern.

---

*Stand: Mai 2026*
