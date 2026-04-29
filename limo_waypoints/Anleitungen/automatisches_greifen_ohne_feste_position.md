# Automatisches Greifen ohne feste Positionsuebergabe

## Ziel

Der LIMO soll einen Baustein nicht nur an einer festen, vorher definierten Position greifen, sondern die Position des Bausteins automatisch erkennen und daraus eine Greifposition fuer den MyCobot berechnen.

Aktueller Ablauf:

```text
YOLO erkennt Baustein
-> LIMO richtet sich aus und faehrt bis zum Greifabstand
-> /greif_start wird gesendet
-> MyCobot faehrt feste Gelenkwinkel ab
```

Ziel-Ablauf:

```text
YOLO erkennt Baustein
-> Mittelpunkt im Kamerabild wird bestimmt
-> Tiefenbild liefert Abstand zum Baustein
-> 3D-Position des Bausteins wird berechnet
-> Position wird in das Koordinatensystem des Arms transformiert
-> MyCobot faehrt dynamisch zur berechneten Greifposition
-> Greifer schliesst und hebt den Baustein an
```

## Warum feste Winkel nicht ausreichen

In der aktuellen Loesung greift der MyCobot mit festen Gelenkwinkeln:

```python
PRE_GRASP_ANGLES = [0, -35, 45, 0, 0, 0]
GRASP_ANGLES = [0, -45, 55, 0, 0, 0]
LIFT_ANGLES = [0, -20, 35, 0, 0, 0]
```

Das funktioniert nur dann zuverlaessig, wenn der Baustein nach dem Anfahren immer an derselben Stelle vor dem Roboter liegt. Wenn der Baustein weiter links, rechts, naeher oder weiter entfernt liegt, greift der Arm daneben.

Fuer echtes automatisches Greifen muss der Arm daher eine berechnete Zielposition bekommen.

## Benutzte Sensorinformationen

Fuer die automatische Greifposition werden drei Informationen benoetigt:

| Information | Quelle | Zweck |
|---|---|---|
| Baustein erkannt | `/baustein_detected` | Startbedingung fuer den Greifablauf |
| Baustein-Mittelpunkt im Bild | `/baustein_center` | Pixelposition des Bausteins |
| Tiefe/Abstand | `/camera/depth/image_raw` | Abstand des Bausteins zur Kamera |
| Kameraparameter | `/camera/depth/camera_info` oder `/camera/color/camera_info` | Umrechnung von Pixel zu 3D-Punkt |

## Umrechnung von Pixelposition zu 3D-Position

YOLO liefert zunaechst nur einen Mittelpunkt im Bild, zum Beispiel:

```text
pixel_x = 340
pixel_y = 260
```

Aus dem Tiefenbild wird an dieser Stelle der Abstand gelesen, zum Beispiel:

```text
depth = 0.58 m
```

Mit den Kameraparametern kann daraus ein 3D-Punkt im Kamera-Koordinatensystem berechnet werden:

```text
X = (pixel_x - cx) * depth / fx
Y = (pixel_y - cy) * depth / fy
Z = depth
```

Bedeutung der Werte:

| Wert | Bedeutung |
|---|---|
| `pixel_x`, `pixel_y` | Mittelpunkt des Bausteins im Kamerabild |
| `depth` | Abstand aus dem Tiefenbild |
| `fx`, `fy` | Brennweiten der Kamera |
| `cx`, `cy` | optischer Mittelpunkt der Kamera |
| `X`, `Y`, `Z` | 3D-Position relativ zur Kamera |

## Transformation in das Arm-Koordinatensystem

Der berechnete 3D-Punkt liegt zuerst im Kamera-Koordinatensystem. Der MyCobot braucht die Position aber relativ zu seiner Basis.

Daher wird eine Transformation benoetigt:

```text
camera_frame -> arm_base_frame
```

Diese Transformation beschreibt, wo die Kamera im Vergleich zum Arm montiert ist:

```text
Position der Kamera relativ zur Armbasis:
- Abstand nach vorne
- Abstand zur Seite
- Hoehe
- Neigung/Rotation
```

In ROS wird das normalerweise mit `tf` oder `tf2` geloest. Falls die Kamera fest am LIMO montiert ist, kann ein statischer Transform verwendet werden.

Beispiel:

```bash
rosrun tf static_transform_publisher x y z roll pitch yaw arm_base_link camera_link 100
```

Die genauen Werte muessen am realen Roboter gemessen oder kalibriert werden.

## Dynamisches Greifen mit MyCobot

Statt feste Gelenkwinkel zu verwenden, sollte der MyCobot eine Zielkoordinate bekommen.

Prinzip:

```python
mc.send_coords([x_mm, y_mm, z_mm, rx, ry, rz], speed, mode)
```

Beispiel:

```python
target = [180, -30, 60, 180, 0, 0]
mc.send_coords(target, 25, 1)
```

Wichtig: Die Koordinaten muessen in Millimeter angegeben werden. Die Tiefenkamera liefert normalerweise Meter. Daher:

```text
meter * 1000 = millimeter
```

## Empfohlene Node-Struktur

### 1. YOLO Detection Node

Vorhandene Datei:

```text
limo_object_detection/yolo_baustein_publisher.py
```

Aufgabe:

```text
Kamerabild lesen
Baustein erkennen
/baustein_detected veroeffentlichen
/baustein_center veroeffentlichen
```

### 2. 3D Position Node

Neue moegliche Node:

```text
baustein_3d_pose_node.py
```

Aufgabe:

```text
/baustein_center lesen
/camera/depth/image_raw lesen
/camera/depth/camera_info lesen
3D-Position berechnen
Position in Arm-Koordinaten transformieren
/baustein_pose_arm veroeffentlichen
```

Moegliches Topic:

```text
/baustein_pose_arm
```

Nachrichtentyp:

```text
geometry_msgs/PoseStamped
```

### 3. Dynamische MyCobot Greifnode

Erweiterung der vorhandenen Datei:

```text
limo_mycobot/mycobot_gripper_node.py
```

Neue Aufgabe:

```text
/baustein_pose_arm lesen
Greifposition pruefen
Greifer oeffnen
Vorposition ueber dem Baustein anfahren
Zum Baustein absenken
Greifer schliessen
Baustein anheben
```

## Greifstrategie

Der Arm sollte nicht direkt exakt zum Mittelpunkt des Bausteins fahren. Sicherer ist ein mehrstufiger Ablauf:

```text
1. Zielposition des Bausteins berechnen
2. Greifposition auf gueltigen Arbeitsbereich pruefen
3. Greifer oeffnen
4. Vorposition ueber dem Baustein anfahren
5. Langsam nach unten fahren
6. Greifer schliessen
7. Arm wieder anheben
```

Beispiel mit Offset:

```text
Bausteinposition:
x = 180 mm
y = -20 mm
z = 25 mm

Vorposition:
x = 180 mm
y = -20 mm
z = 90 mm

Greifposition:
x = 180 mm
y = -20 mm
z = 35 mm
```

Der Offset ist wichtig, damit der Arm zuerst oberhalb des Bausteins steht und danach kontrolliert absenkt.

## Sicherheitspruefungen

Vor jeder Armbewegung sollten Grenzwerte geprueft werden:

```text
x_min <= x <= x_max
y_min <= y <= y_max
z_min <= z <= z_max
```

Beispiel:

```text
x: 100 mm bis 260 mm
y: -120 mm bis 120 mm
z: 20 mm bis 180 mm
```

Wenn die berechnete Position ausserhalb des Arbeitsbereichs liegt, darf der Arm nicht fahren.

## Stabilisierung der Erkennung

Die Greifposition sollte nicht aus nur einem einzelnen Bild berechnet werden. Besser ist:

```text
Baustein muss fuer 1 bis 2 Sekunden erkannt werden
Mittelpunkt darf nur wenig schwanken
Depth-Wert muss gueltig sein
mehrere Messungen werden gemittelt oder per Median gefiltert
```

Dadurch wird verhindert, dass der Roboter wegen einer fehlerhaften Erkennung falsch greift.

## Moeglicher Gesamtprozess

```text
1. Kamera starten
2. YOLO Detection starten
3. LIMO richtet sich auf den Baustein aus
4. LIMO faehrt bis zum Greifabstand
5. 3D-Position des Bausteins wird berechnet
6. Position wird in das Arm-Koordinatensystem transformiert
7. MyCobot faehrt dynamisch zur Greifposition
8. Greifer schliesst
9. MyCobot hebt den Baustein an
```

## Vorteile dieser Loesung

| Vorteil | Beschreibung |
|---|---|
| Flexibler | Baustein muss nicht exakt an einer festen Stelle liegen |
| Robuster | Kamera und Tiefenbild bestimmen die reale Position |
| Erweiterbar | Spaeter koennen mehrere Objekte oder Ablagepositionen ergaenzt werden |
| Realistischer | Der Arm greift auf Basis der erkannten Umgebung |

## Herausforderungen

| Herausforderung | Bedeutung |
|---|---|
| Kamera-Arm-Kalibrierung | Die Transformation zwischen Kamera und MyCobot muss genau sein |
| Tiefenrauschen | Depth-Werte koennen springen oder ungueltig sein |
| Greifer-Offset | Der Greifer muss passend zum Baustein ausgerichtet werden |
| Arbeitsbereich | Nicht jede erkannte Position ist fuer den Arm erreichbar |
| Synchronisation | LIMO darf waehrend des Greifens nicht weiterfahren |

## Fazit

Automatisches Greifen ohne feste Positionsuebergabe ist moeglich, wenn aus YOLO-Erkennung und Tiefenbild eine echte 3D-Position berechnet wird. Diese Position muss anschliessend vom Kamera-Koordinatensystem in das Koordinatensystem des MyCobot transformiert werden.

Der wichtigste Unterschied zur aktuellen Loesung ist:

```text
Nicht mehr: Arm faehrt feste Winkel
Sondern: Arm faehrt zur berechneten Bausteinposition
```

Damit kann der LIMO den Baustein deutlich flexibler und autonomer greifen.
