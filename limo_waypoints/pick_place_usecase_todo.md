# To-do: LIMO fährt zum Baustein, greift ihn und bringt ihn zum Zielpunkt

## Ziel

Der Roboter soll immer von derselben Startposition aus starten, zu einem festen Baustein-Punkt fahren, den Baustein mit dem MyCobot greifen, zu einem festen Ablagepunkt fahren und den Baustein dort ablegen.

```text
Startposition
    ↓
zum Pick-Punkt fahren
    ↓
Baustein greifen
    ↓
zum Place-Punkt fahren
    ↓
Baustein ablegen
```

## 1. Grundentscheidung

- [ ] Prüfen, ob der Roboter wirklich immer von derselben Position startet.
- [ ] Prüfen, ob der Baustein wirklich immer an derselben Position liegt.
- [ ] Prüfen, ob der Ablagepunkt immer gleich ist.
- [ ] Wenn alle drei Punkte fest sind: YOLO-Erkennung nicht verwenden.
- [ ] Wenn der Baustein später variabel liegt: YOLO-/Depth-Erkennung wieder einplanen.

## 2. Navigation vorbereiten

- [ ] Karte der Umgebung erstellen oder vorhandene Karte verwenden.
- [ ] Lokalisierung mit AMCL starten.
- [ ] Nav2 starten.
- [ ] Prüfen, ob der Roboter sich in der Karte korrekt lokalisiert.
- [ ] Prüfen, ob `/amcl_pose` gültige Positionsdaten liefert.
- [ ] Prüfen, ob der Roboter mit Nav2 zu einem Zielpunkt fahren kann.

## 3. Pick- und Place-Punkte festlegen

- [ ] Pick-Punkt bestimmen: Dort soll der Roboter vor dem Baustein stehen.
- [ ] Place-Punkt bestimmen: Dort soll der Roboter den Baustein ablegen.
- [ ] Für beide Punkte die Koordinaten notieren:

```text
Pick:
x =
y =
yaw =

Place:
x =
y =
yaw =
```

- [ ] Pick-Punkt in der Karte testen.
- [ ] Place-Punkt in der Karte testen.
- [ ] Prüfen, ob der Roboter an beiden Punkten passend ausgerichtet steht.

## 4. MyCobot vorbereiten

- [ ] Richtigen MyCobot-Port mit `test_port.py` prüfen.
- [ ] Funktionierenden Port notieren, zum Beispiel `/dev/ttyACM0`.
- [ ] Greifer mit `test_gripper.py` testen.
- [ ] Armbewegung mit `move_arm.py` testen.
- [ ] Manuelle Steuerung mit `keyboard_control.py` verwenden.
- [ ] Sichere Home-Position finden.
- [ ] Vor-Greifposition finden.
- [ ] Greifposition finden.
- [ ] Hebeposition finden.
- [ ] Ablageposition finden.
- [ ] Öffnen-Position beim Ablegen testen.

## 5. Armwinkel auslesen

- [ ] Arm mit `keyboard_control.py` in die gewünschte Home-Position fahren.
- [ ] Winkel mit `get_angles.py` auslesen.
- [ ] Home-Winkel notieren.
- [ ] Arm in die Vor-Greifposition fahren.
- [ ] Winkel auslesen und notieren.
- [ ] Arm in die Greifposition fahren.
- [ ] Winkel auslesen und notieren.
- [ ] Arm in die Hebeposition fahren.
- [ ] Winkel auslesen und notieren.
- [ ] Arm in die Ablageposition fahren.
- [ ] Winkel auslesen und notieren.

```text
HOME_ANGLES =
PRE_GRASP_ANGLES =
GRASP_ANGLES =
LIFT_ANGLES =
PLACE_ANGLES =
RELEASE_ANGLES =
```

## 6. Greifer-Node erweitern

Aktuelle Grundlage:

```text
limo_waypoints/limo_mycobot/mycobot_gripper_node.py
```

- [ ] Bestehende Greifsequenz prüfen.
- [ ] Feste Greifwinkel eintragen.
- [ ] Neue Ablege-Sequenz ergänzen.
- [ ] Separates Topic für Greifen einplanen, zum Beispiel `/greif_start`.
- [ ] Separates Topic für Ablegen einplanen, zum Beispiel `/place_start`.
- [ ] Optional ein Fertig-Signal einplanen, zum Beispiel `/gripper_done`.
- [ ] Prüfen, dass während einer Sequenz keine zweite Sequenz gestartet wird.
- [ ] Greifen ohne Fahrbewegung testen.
- [ ] Ablegen ohne Fahrbewegung testen.

## 7. ROS-Versionen klären

Wichtig: Die Navigation nutzt aktuell ROS2, der MyCobot-Greifer-Code nutzt aktuell ROS1.

- [ ] Prüfen, ob Navigation und Greifer im selben ROS-System laufen sollen.
- [ ] Wenn alles in ROS2 laufen soll: `mycobot_gripper_node.py` auf ROS2 umbauen.
- [ ] Wenn ROS1 und ROS2 gemischt bleiben: ROS1-ROS2-Bridge einrichten.
- [ ] Empfohlene Lösung: Greifer-Node auf ROS2 umbauen, damit Navigation und Greifer direkt zusammenarbeiten.

## 8. Ablaufprogramm erstellen

Grundlage:

```text
limo_waypoints/limo_navigation/pickplace_navigator.py
```

Das Ablaufprogramm soll später diese Reihenfolge haben:

```text
1. Startposition lesen
2. zum Pick-Punkt fahren
3. Greifsignal senden
4. warten, bis Greifen fertig ist
5. zum Place-Punkt fahren
6. Ablegesignal senden
7. warten, bis Ablegen fertig ist
8. optional zurück zur Startposition fahren
```

- [ ] `pickplace_navigator.py` auf festen Pick-Punkt erweitern.
- [ ] Feste Place-Koordinaten ergänzen.
- [ ] Nach erfolgreicher Fahrt zum Pick-Punkt `/greif_start` senden.
- [ ] Warten, bis der Greifer fertig ist.
- [ ] Danach zum Place-Punkt fahren.
- [ ] Nach erfolgreicher Fahrt zum Place-Punkt `/place_start` senden.
- [ ] Warten, bis Ablegen fertig ist.
- [ ] Optional zurück zur Startposition fahren.

## 9. Testreihenfolge

- [ ] Nur Navigation zum Pick-Punkt testen.
- [ ] Nur Navigation zum Place-Punkt testen.
- [ ] Nur Greifsequenz testen.
- [ ] Nur Ablegesequenz testen.
- [ ] Pick-Punkt anfahren und Greifen testen.
- [ ] Place-Punkt anfahren und Ablegen testen.
- [ ] Gesamtablauf ohne Baustein testen.
- [ ] Gesamtablauf mit Baustein testen.
- [ ] Mehrere Wiederholungen testen.

## 10. Welche Dateien werden wahrscheinlich gebraucht?

| Datei | Verwendung |
| --- | --- |
| `limo_navigation/pickplace_navigator.py` | Grundlage für den kompletten Fahr- und Pick-and-Place-Ablauf. |
| `limo_navigation/waypoint_navigator.py` | Beispiel für Navigation zu einem Ziel. |
| `limo_mycobot/mycobot_gripper_node.py` | Grundlage für Greifen und Ablegen mit festen Winkeln. |
| `limo_mycobot/keyboard_control.py` | Manuelles Finden der passenden Armpositionen. |
| `limo_mycobot/get_angles.py` | Auslesen der passenden Winkel. |
| `limo_mycobot/test_gripper.py` | Testen des Greifers. |
| `limo_mycobot/test_port.py` | Finden des richtigen MyCobot-Ports. |

## 11. Welche Dateien werden bei festem Bausteinpunkt wahrscheinlich nicht gebraucht?

| Datei | Warum nicht nötig? |
| --- | --- |
| `yolo_baustein_publisher.py` | Bausteinerkennung ist nicht nötig, wenn der Baustein immer gleich liegt. |
| `yolo_baustein_follow.py` | Der Roboter muss dem Baustein nicht visuell folgen. |
| `yolo_baustein_follow_depth.py` | Tiefenbasierte Annäherung ist nicht nötig, wenn der Pick-Punkt fest ist. |
| `baustein_auto_grabber.py` | Flexible Kamera-zu-Arm-Greifberechnung ist nicht nötig, wenn die Greifposition fest ist. |

## 12. Minimaler Zielaufbau

Für die einfache feste Variante reicht am Ende ungefähr:

```text
Nav2 + AMCL
    ↓
pickplace_navigator.py
    ↓
mycobot_gripper_node.py
    ↓
MyCobot greift und legt ab
```

## 13. Merksatz

```text
Wenn Startposition, Bausteinposition und Ablagepunkt fest sind,
brauchst du keine Objekterkennung.

Du brauchst feste Navigationspunkte
und feste MyCobot-Winkel für Greifen und Ablegen.
```
