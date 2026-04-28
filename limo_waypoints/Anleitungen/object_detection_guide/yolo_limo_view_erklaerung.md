# Erklärung zu `yolo_limo_view.py`

Diese Datei startet einen ROS-Knoten, empfängt Kamerabilder vom LIMO-Roboter, lässt darauf ein YOLO-Modell Objekte erkennen und zeigt das Ergebnis in einem OpenCV-Fenster an.

Kurz gesagt:

1. Kamera-Bild aus ROS empfangen.
2. ROS-Bild in ein OpenCV-Bild umwandeln.
3. YOLO-Modell auf das Bild anwenden.
4. Erkanntes Bild mit Boxen anzeigen.

## Vollständiger Code

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

## Erklärung Zeile für Zeile

| Zeile | Code | Erklärung |
| --- | --- | --- |
| 1 | `#!/usr/bin/env python3` | Sagt dem Betriebssystem, dass diese Datei mit Python 3 gestartet werden soll. Das ist vor allem unter Linux wichtig, wenn man die Datei direkt ausführt. |
| 2 | `import rospy` | Importiert die Python-Bibliothek für ROS 1. Damit kann das Programm einen ROS-Knoten starten, Topics abonnieren und Fehlermeldungen ausgeben. |
| 3 | `from sensor_msgs.msg import Image` | Importiert den ROS-Nachrichtentyp `Image`. Dieser Typ wird für Kamerabilder in ROS verwendet. |
| 4 | `from cv_bridge import CvBridge` | Importiert `CvBridge`. Diese Brücke wandelt ROS-Bilder in OpenCV-Bilder um. |
| 5 | `from ultralytics import YOLO` | Importiert YOLO aus der Ultralytics-Bibliothek. Damit wird das trainierte Objekterkennungsmodell geladen und benutzt. |
| 6 | `import cv2` | Importiert OpenCV. OpenCV wird hier benutzt, um das erkannte Bild in einem Fenster anzuzeigen. |
| 7 | Leerzeile | Macht den Code übersichtlicher. |
| 8 | `MODEL_PATH = "/home/agilex/best.pt"` | Speichert den Pfad zur YOLO-Modell-Datei. Die Datei `best.pt` enthält das trainierte Modell. |
| 9 | `IMAGE_TOPIC = "/camera/color/image_raw"` | Speichert den Namen des ROS-Topics, auf dem die Kamera ihre Bilder veröffentlicht. |
| 10 | `CONFIDENCE = 0.5` | Legt fest, ab welcher Sicherheit YOLO eine Erkennung akzeptieren soll. `0.5` bedeutet 50 Prozent. |
| 11 | Leerzeile | Trennt die Einstellungen von der Klasse. |
| 12 | `class LimoYoloViewer:` | Definiert eine Klasse. Diese Klasse bündelt alles, was zum Anzeigen der YOLO-Erkennung gebraucht wird. |
| 13 | `def __init__(self):` | Definiert den Konstruktor der Klasse. Diese Methode wird automatisch ausgeführt, wenn ein Objekt der Klasse erstellt wird. |
| 14 | `rospy.init_node("limo_yolo_viewer", anonymous=True)` | Startet einen ROS-Knoten mit dem Namen `limo_yolo_viewer`. `anonymous=True` sorgt dafür, dass ROS bei Bedarf eine eindeutige Nummer an den Namen anhängt. |
| 15 | `self.bridge = CvBridge()` | Erstellt ein `CvBridge`-Objekt. Es wird später gebraucht, um ROS-Bilder in OpenCV-Bilder umzuwandeln. |
| 16 | `self.model = YOLO(MODEL_PATH)` | Lädt das YOLO-Modell aus dem Pfad, der in `MODEL_PATH` gespeichert ist. |
| 17 | `self.sub = rospy.Subscriber(` | Erstellt einen Subscriber. Ein Subscriber hört auf ein ROS-Topic und reagiert, wenn neue Nachrichten ankommen. |
| 18 | `IMAGE_TOPIC,` | Gibt an, welches Topic abonniert wird. Hier ist es das Kamera-Topic `/camera/color/image_raw`. |
| 19 | `Image,` | Gibt an, welchen Nachrichtentyp das Topic liefert. Hier sind es ROS-Bilder vom Typ `Image`. |
| 20 | `self.image_callback,` | Gibt an, welche Funktion aufgerufen wird, wenn ein neues Bild empfangen wurde. |
| 21 | `queue_size=1,` | Speichert nur ein Bild in der Warteschlange. Das ist sinnvoll bei Kamerabildern, weil alte Bilder schnell uninteressant werden. |
| 22 | `buff_size=2**24` | Setzt die Puffergröße für große Bilddaten. `2**24` bedeutet 16.777.216 Bytes, also etwa 16 MB. |
| 23 | `)` | Beendet den Aufruf von `rospy.Subscriber`. |
| 24 | Leerzeile | Trennt den Konstruktor von der nächsten Methode. |
| 25 | `def image_callback(self, msg):` | Definiert die Callback-Funktion. Sie wird jedes Mal aufgerufen, wenn ein neues Kamerabild empfangen wird. `msg` ist die empfangene ROS-Bildnachricht. |
| 26 | `try:` | Startet einen geschützten Codeblock. Falls darin ein Fehler passiert, springt das Programm zum `except`-Block. |
| 27 | `frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")` | Wandelt das ROS-Bild `msg` in ein OpenCV-Bild um. `bgr8` ist das übliche Farbformat für OpenCV. |
| 28 | `results = self.model.predict(source=frame, conf=CONFIDENCE, verbose=False)` | Führt die YOLO-Erkennung auf dem aktuellen Bild aus. `conf=CONFIDENCE` nutzt den Mindestwert aus Zeile 10. `verbose=False` verhindert unnötige Konsolenausgaben. |
| 29 | `annotated = results[0].plot()` | Erstellt ein Bild mit eingezeichneten Erkennungen, zum Beispiel Boxen, Klassenname und Sicherheit. |
| 30 | `cv2.imshow("LIMO YOLO", annotated)` | Zeigt das bearbeitete Bild in einem Fenster mit dem Titel `LIMO YOLO` an. |
| 31 | `cv2.waitKey(1)` | Wartet 1 Millisekunde. Diese Zeile ist nötig, damit OpenCV das Fenster aktualisieren kann. |
| 32 | `except Exception as e:` | Fängt Fehler ab, die im `try`-Block passieren. Der Fehler wird in der Variable `e` gespeichert. |
| 33 | `rospy.logerr(f"Fehler in image_callback: {e}")` | Gibt eine Fehlermeldung über ROS aus, falls beim Verarbeiten eines Bildes etwas schiefgeht. |
| 34 | Leerzeile | Trennt die Klasse vom Startpunkt des Programms. |
| 35 | `if __name__ == "__main__":` | Prüft, ob diese Datei direkt gestartet wurde. Nur dann wird der Code darunter ausgeführt. |
| 36 | `LimoYoloViewer()` | Erstellt ein Objekt der Klasse. Dadurch wird automatisch `__init__` ausgeführt, der ROS-Knoten gestartet, das Modell geladen und das Kamera-Topic abonniert. |
| 37 | `rospy.spin()` | Hält das Programm am Leben. Ohne diese Zeile würde das Programm sofort wieder beendet werden. |

## Wichtige Begriffe

### ROS-Knoten

Ein ROS-Knoten ist ein einzelnes Programm innerhalb eines ROS-Systems. In dieser Datei heißt der Knoten `limo_yolo_viewer`.

### Topic

Ein Topic ist ein Kommunikationskanal in ROS. Die Kamera veröffentlicht Bilder auf dem Topic `/camera/color/image_raw`. Dieses Skript hört auf dieses Topic.

### Subscriber

Ein Subscriber ist ein Empfänger. Er wartet auf neue Nachrichten von einem Topic. Sobald ein neues Bild kommt, ruft ROS automatisch `image_callback` auf.

### Callback

Eine Callback-Funktion wird nicht direkt von uns aufgerufen. Stattdessen ruft ROS sie automatisch auf, wenn ein Ereignis passiert. Hier ist das Ereignis: Ein neues Kamerabild wurde empfangen.

### CvBridge

ROS und OpenCV verwenden unterschiedliche Bildformate. `CvBridge` übersetzt zwischen diesen Formaten.

### YOLO

YOLO ist ein Verfahren zur Objekterkennung. Es kann in einem Bild Objekte finden und meistens auch anzeigen, zu welcher Klasse sie gehören.

### Confidence

Die Confidence ist die Sicherheit einer Erkennung. Wenn `CONFIDENCE = 0.5` gesetzt ist, werden nur Erkennungen angezeigt, bei denen das Modell mindestens 50 Prozent sicher ist.

## Ablauf des Programms

1. Das Programm wird gestartet.
2. ROS-Knoten `limo_yolo_viewer` wird erstellt.
3. `CvBridge` wird vorbereitet.
4. Das YOLO-Modell `best.pt` wird geladen.
5. Das Kamera-Topic wird abonniert.
6. Bei jedem neuen Kamerabild wird `image_callback` aufgerufen.
7. Das ROS-Bild wird in ein OpenCV-Bild umgewandelt.
8. YOLO erkennt Objekte im Bild.
9. Die Erkennungen werden ins Bild eingezeichnet.
10. Das Ergebnis wird in einem Fenster angezeigt.

## Was kann man leicht anpassen?

### Anderes Modell benutzen

```python
MODEL_PATH = "/home/agilex/best.pt"
```

Hier kann ein anderer Pfad zu einer `.pt`-Datei eingetragen werden.

### Anderes Kamera-Topic benutzen

```python
IMAGE_TOPIC = "/camera/color/image_raw"
```

Wenn die Kamera ihre Bilder auf einem anderen Topic veröffentlicht, muss dieser Wert angepasst werden.

### Strengere oder lockerere Erkennung

```python
CONFIDENCE = 0.5
```

Ein höherer Wert, zum Beispiel `0.7`, zeigt nur sichere Erkennungen an. Ein niedrigerer Wert, zum Beispiel `0.3`, zeigt mehr Erkennungen an, aber auch mehr mögliche Fehler.

## Zusammenfassung

`yolo_limo_view.py` ist ein kleines ROS-Programm zur Live-Objekterkennung. Es nimmt Kamerabilder vom LIMO-Roboter, verarbeitet sie mit einem YOLO-Modell und zeigt die erkannten Objekte direkt in einem Fenster an.
