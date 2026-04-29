# yolo_limo_view.py einfach erklaert

Diese Datei zeigt das Kamerabild des LIMO an und laesst gleichzeitig ein trainiertes YOLO-Modell auf jedem Kamerabild nach Objekten suchen. Erkannte Objekte werden direkt im Bild markiert.

Die Datei gehoert zu:

```text
limo_waypoints/limo_object_detection/yolo_limo_view.py
```

Kurz gesagt:

1. ROS-Node starten.
2. YOLO-Modell laden.
3. Kamerabild vom LIMO abonnieren.
4. ROS-Bild in ein OpenCV-Bild umwandeln.
5. YOLO-Erkennung auf dem Bild ausfuehren.
6. Erkannte Objekte ins Bild zeichnen.
7. Bild in einem Fenster anzeigen.

## Vollstaendiger Code

```python
#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2

MODEL_PATH = "/home/agilex/best.pt"
IMAGE_TOPIC = "/camera/color/image_raw"
CONFIDENCE = 0.5

class LimoYoloViewer:
    def __init__(self):
        rospy.init_node("limo_yolo_viewer", anonymous=True)
        self.bridge = CvBridge()
        self.model = YOLO(MODEL_PATH)
        self.sub = rospy.Subscriber(
            IMAGE_TOPIC,
            Image,
            self.image_callback,
            queue_size=1,
            buff_size=2**24
        )

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            results = self.model.predict(source=frame, conf=CONFIDENCE, verbose=False)
            annotated = results[0].plot()
            cv2.imshow("LIMO YOLO", annotated)
            cv2.waitKey(1)
        except Exception as e:
            rospy.logerr(f"Fehler in image_callback: {e}")

if __name__ == "__main__":
    LimoYoloViewer()
    rospy.spin()
```

## Zeile fuer Zeile erklaert

| Zeile | Code | Erklaerung |
|---|---|---|
| 1 | `#!/usr/bin/env python3` | Sagt dem System, dass diese Datei mit Python 3 ausgefuehrt werden soll. |
| 2 | `import rospy` | Laedt die ROS-Python-Bibliothek. Damit kann das Skript mit ROS kommunizieren. |
| 3 | `from sensor_msgs.msg import Image` | Importiert den ROS-Nachrichtentyp fuer Kamerabilder. |
| 4 | `from cv_bridge import CvBridge` | Laedt die Bruecke zwischen ROS-Bildern und OpenCV-Bildern. |
| 5 | `from ultralytics import YOLO` | Laedt die YOLO-Funktion aus der Ultralytics-Bibliothek. |
| 6 | `import cv2` | Laedt OpenCV. Damit kann das Bild angezeigt und verarbeitet werden. |
| 8 | `MODEL_PATH = "/home/agilex/best.pt"` | Gibt an, wo das trainierte YOLO-Modell auf dem LIMO gespeichert ist. |
| 9 | `IMAGE_TOPIC = "/camera/color/image_raw"` | Gibt an, von welchem ROS-Topic das Kamerabild gelesen wird. |
| 10 | `CONFIDENCE = 0.5` | Legt fest, ab welcher Sicherheit YOLO eine Erkennung akzeptiert. |
| 12 | `class LimoYoloViewer:` | Erstellt eine Klasse fuer die komplette YOLO-Anzeige. |
| 13 | `def __init__(self):` | Diese Funktion wird automatisch ausgefuehrt, wenn die Klasse gestartet wird. |
| 14 | `rospy.init_node("limo_yolo_viewer", anonymous=True)` | Startet eine ROS-Node mit dem Namen `limo_yolo_viewer`. |
| 15 | `self.bridge = CvBridge()` | Erstellt den Umwandler fuer ROS-Bilder zu OpenCV-Bildern. |
| 16 | `self.model = YOLO(MODEL_PATH)` | Laedt das trainierte YOLO-Modell aus `MODEL_PATH`. |
| 17 | `self.sub = rospy.Subscriber(` | Erstellt einen Subscriber. Er wartet auf neue Kamerabilder. |
| 18 | `IMAGE_TOPIC,` | Der Subscriber hoert auf das Kamera-Topic `/camera/color/image_raw`. |
| 19 | `Image,` | Erwartet Nachrichten vom Typ `Image`. |
| 20 | `self.image_callback,` | Bei jedem neuen Kamerabild wird `image_callback` aufgerufen. |
| 21 | `queue_size=1,` | Es wird nur das neueste Bild zwischengespeichert. Alte Bilder werden verworfen. |
| 22 | `buff_size=2**24` | Vergroessert den Speicherpuffer, damit grosse Kamerabilder sauber empfangen werden. |
| 23 | `)` | Beendet die Subscriber-Erstellung. |
| 25 | `def image_callback(self, msg):` | Diese Funktion wird jedes Mal ausgefuehrt, wenn ein neues Kamerabild ankommt. |
| 26 | `try:` | Startet einen geschuetzten Bereich. Fehler werden abgefangen, damit das Skript nicht sofort abstuerzt. |
| 27 | `frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")` | Wandelt das ROS-Kamerabild in ein OpenCV-Bild um. |
| 28 | `results = self.model.predict(source=frame, conf=CONFIDENCE, verbose=False)` | Fuehrt YOLO auf dem aktuellen Kamerabild aus. |
| 29 | `annotated = results[0].plot()` | Zeichnet die erkannten Objekte in das Bild ein. |
| 30 | `cv2.imshow("LIMO YOLO", annotated)` | Zeigt das bearbeitete Bild in einem Fenster mit dem Namen `LIMO YOLO`. |
| 31 | `cv2.waitKey(1)` | Aktualisiert das Bildfenster. |
| 32 | `except Exception as e:` | Falls in der Bildverarbeitung ein Fehler auftritt, wird er hier abgefangen. |
| 33 | `rospy.logerr(f"Fehler in image_callback: {e}")` | Gibt die Fehlermeldung in ROS aus. |
| 35 | `if __name__ == "__main__":` | Prueft, ob die Datei direkt gestartet wurde. |
| 36 | `LimoYoloViewer()` | Erstellt und startet die YOLO-Anzeige. |
| 37 | `rospy.spin()` | Haelt die ROS-Node am Leben, damit weiterhin Kamerabilder verarbeitet werden. |

## Die wichtigsten Bestandteile

### Das YOLO-Modell

```python
MODEL_PATH = "/home/agilex/best.pt"
self.model = YOLO(MODEL_PATH)
```

Hier wird das trainierte Modell geladen. Die Datei `best.pt` entsteht normalerweise nach dem Training eines eigenen YOLO-Modells.

Wenn die Datei nicht unter `/home/agilex/best.pt` liegt, muss der Pfad angepasst werden.

### Das Kamera-Topic

```python
IMAGE_TOPIC = "/camera/color/image_raw"
```

Dieses Topic liefert das Farbbild der Kamera. Das Skript liest also nicht direkt von einer USB-Kamera, sondern von ROS.

```text
Kamera -> ROS Topic -> yolo_limo_view.py -> YOLO-Erkennung -> Anzeige
```

### Die Confidence

```python
CONFIDENCE = 0.5
```

Dieser Wert legt fest, wie sicher YOLO sein muss, damit eine Erkennung angezeigt wird.

| Wert | Wirkung |
|---|---|
| `0.3` | Mehr Erkennungen, aber auch mehr falsche Treffer |
| `0.5` | Ausgewogener Standardwert |
| `0.7` | Weniger Erkennungen, dafuer meist sicherer |

### Die Callback-Funktion

```python
def image_callback(self, msg):
```

Diese Funktion ist der wichtigste Teil des Programms. Sie wird automatisch bei jedem neuen Kamerabild ausgefuehrt.

```text
ROS-Bild empfangen
-> in OpenCV-Bild umwandeln
-> YOLO ausfuehren
-> Ergebnis einzeichnen
-> Bild anzeigen
```

## Was das Skript noch nicht macht

Dieses Skript ist nur fuer die Live-Anzeige gedacht.

Es veroeffentlicht noch keine eigenen ROS-Topics wie:

```text
/baustein_detected
/baustein_center
/baustein_confidence
```

Dafuer gibt es im Projekt die Datei:

```text
yolo_baustein_publisher.py
```

Der Unterschied ist:

| Datei | Zweck |
|---|---|
| `yolo_limo_view.py` | Zeigt YOLO-Erkennung live im Kamerabild an |
| `yolo_baustein_publisher.py` | Gibt Erkennungsergebnisse als ROS-Topics weiter |

## Typische Fehler

| Problem | Moegliche Ursache |
|---|---|
| Fenster bleibt schwarz | Kamera-Topic liefert kein Bild |
| Modell wird nicht geladen | Pfad zu `best.pt` ist falsch |
| Keine Erkennung | Modell erkennt das Objekt nicht oder `CONFIDENCE` ist zu hoch |
| Fehlermeldung bei `cv_bridge` | ROS-Bildformat passt nicht oder `cv_bridge` fehlt |
| Kein Fenster sichtbar | Skript laeuft ohne grafische Oberflaeche oder per SSH ohne Display |

## Startvoraussetzungen

Vor dem Start des Skripts muessen ROS und die Kamera laufen.

Beispiel:

```bash
roscore
```

```bash
source ~/agilex_ws/devel_isolated/astra_camera/setup.bash
roslaunch astra_camera dabai_u3.launch
```

Danach kann die YOLO-Anzeige gestartet werden:

```bash
python3 yolo_limo_view.py
```

## Zusammenfassung

`yolo_limo_view.py` ist ein einfaches Anzeigeprogramm fuer die Objekterkennung auf dem LIMO. Es liest das Kamerabild aus ROS, laedt das trainierte YOLO-Modell, erkennt Objekte im Bild und zeigt das Ergebnis live mit Markierungen an.

Es eignet sich gut zum Testen, ob Kamera und YOLO-Modell korrekt funktionieren.
