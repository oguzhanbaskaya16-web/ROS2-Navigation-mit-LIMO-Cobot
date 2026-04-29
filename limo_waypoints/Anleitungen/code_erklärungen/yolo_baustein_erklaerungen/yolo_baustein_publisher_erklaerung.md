# Erklärung zu `yolo_baustein_publisher.py`

Diese Datei startet einen ROS-Knoten, der Kamerabilder empfängt und mit einem YOLO-Modell nach einem Baustein sucht.

Wenn ein Baustein erkannt wird, veröffentlicht der Knoten drei Informationen:

1. Ob ein Baustein erkannt wurde.
2. Wo sich die Mitte des Bausteins im Kamerabild befindet.
3. Wie sicher YOLO bei der Erkennung ist.

Kurz gesagt:

1. ROS wird gestartet.
2. Das YOLO-Modell wird geladen.
3. Der Knoten abonniert das Kamerabild.
4. Jedes Kamerabild wird in ein OpenCV-Bild umgewandelt.
5. YOLO sucht im Bild nach Bausteinen.
6. Die beste Erkennung wird ausgewählt.
7. Erkennung, Mittelpunkt und Sicherheit werden auf ROS-Topics veröffentlicht.

## Wichtige Begriffe

| Begriff | Bedeutung |
| --- | --- |
| ROS-Knoten | Ein einzelnes Programm in ROS. Dieser Knoten kümmert sich um die Baustein-Erkennung. |
| `rospy` | Die Python-Bibliothek für ROS1. Sie wird benutzt, um Publisher, Subscriber und Logs zu erstellen. |
| Topic | Ein Kanal in ROS, über den Nachrichten gesendet oder empfangen werden. |
| Publisher | Sendet Nachrichten auf ein ROS-Topic. |
| Subscriber | Hört auf ein ROS-Topic und reagiert auf neue Nachrichten. |
| Callback | Eine Funktion, die automatisch aufgerufen wird, wenn eine neue Nachricht ankommt. |
| YOLO | Ein KI-Modell zur Objekterkennung in Bildern. |
| Bounding Box | Ein Rechteck um ein erkanntes Objekt. Es beschreibt, wo das Objekt im Bild liegt. |
| Confidence | Die Sicherheit des Modells. Ein Wert von `0.8` bedeutet zum Beispiel: YOLO ist zu 80 Prozent sicher. |
| OpenCV | Eine Bibliothek zur Bildverarbeitung in Python. |
| CvBridge | Wandelt ROS-Bilder in OpenCV-Bilder um. |

## Vollständiger Code

```python
#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import Bool, Float32
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2

MODEL_PATH = "/home/agilex/best.pt"
IMAGE_TOPIC = "/camera/color/image_raw"
CONFIDENCE_THRESHOLD = 0.5

class BausteinDetector:
    def __init__(self):
        rospy.init_node("baustein_detector", anonymous=True)

        self.bridge = CvBridge()
        self.model = YOLO(MODEL_PATH)

        self.detected_pub = rospy.Publisher("/baustein_detected", Bool, queue_size=10)
        self.center_pub = rospy.Publisher("/baustein_center", Point, queue_size=10)
        self.conf_pub = rospy.Publisher("/baustein_confidence", Float32, queue_size=10)

        self.sub = rospy.Subscriber(
            IMAGE_TOPIC,
            Image,
            self.image_callback,
            queue_size=1,
            buff_size=2**24
        )

        rospy.loginfo("Baustein-Detektor gestartet.")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            results = self.model.predict(source=frame, conf=CONFIDENCE_THRESHOLD, verbose=False)

            detected = False
            best_conf = 0.0
            best_center = None

            if results and len(results) > 0:
                boxes = results[0].boxes
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        conf = float(box.conf[0].item())
                        xyxy = box.xyxy[0].tolist()
                        x1, y1, x2, y2 = xyxy

                        cx = (x1 + x2) / 2.0
                        cy = (y1 + y2) / 2.0

                        if conf > best_conf:
                            best_conf = conf
                            best_center = (cx, cy)

                    if best_center is not None:
                        detected = True

            self.detected_pub.publish(Bool(data=detected))

            if detected:
                p = Point()
                p.x = best_center[0]
                p.y = best_center[1]
                p.z = 0.0
                self.center_pub.publish(p)
                self.conf_pub.publish(Float32(data=best_conf))
            else:
                self.conf_pub.publish(Float32(data=0.0))

        except Exception as e:
            rospy.logerr(f"Fehler in image_callback: {e}")

if __name__ == "__main__":
    BausteinDetector()
    rospy.spin()
```

## Erklärung Zeile für Zeile

| Zeile | Code | Erklärung |
| --- | --- | --- |
| 1 | `#!/usr/bin/env python3` | Diese Zeile sagt dem System, dass die Datei mit Python 3 ausgeführt werden soll. Das ist besonders nützlich, wenn die Datei direkt als Programm gestartet wird. |
| 2 | `import rospy` | Importiert `rospy`, die Python-Bibliothek für ROS1. Damit kann der Code einen ROS-Knoten starten, Topics benutzen und Meldungen ausgeben. |
| 3 | `from sensor_msgs.msg import Image` | Importiert den Nachrichtentyp `Image`. Dieser Typ wird für Kamerabilder in ROS verwendet. |
| 4 | `from std_msgs.msg import Bool, Float32` | Importiert zwei einfache Nachrichtentypen. `Bool` speichert `True` oder `False`, `Float32` speichert eine Kommazahl. |
| 5 | `from geometry_msgs.msg import Point` | Importiert den Nachrichtentyp `Point`. Hier wird er benutzt, um die x- und y-Position der Bausteinmitte zu senden. |
| 6 | `from cv_bridge import CvBridge` | Importiert `CvBridge`. Diese Brücke wandelt ROS-Bilder in OpenCV-Bilder um. |
| 7 | `from ultralytics import YOLO` | Importiert YOLO aus der Ultralytics-Bibliothek. Damit kann das trainierte Erkennungsmodell geladen und benutzt werden. |
| 8 | `import cv2` | Importiert OpenCV. In dieser Datei wird `cv2` aktuell nicht direkt benutzt, wäre aber typisch für Bildverarbeitung oder Bildanzeige. |
| 9 | Leerzeile | Macht den Code übersichtlicher. |
| 10 | `MODEL_PATH = "/home/agilex/best.pt"` | Speichert den Pfad zum trainierten YOLO-Modell. Die Datei `best.pt` enthält die gelernten Erkennungsdaten. |
| 11 | `IMAGE_TOPIC = "/camera/color/image_raw"` | Speichert den Namen des Kamera-Topics. Von diesem Topic kommen die Farbbilder der Kamera. |
| 12 | `CONFIDENCE_THRESHOLD = 0.5` | Legt die Mindest-Sicherheit fest. YOLO-Erkennungen unter `0.5` werden ignoriert. |
| 13 | Leerzeile | Trennt die Einstellungen von der Klasse. |
| 14 | `class BausteinDetector:` | Definiert die Klasse `BausteinDetector`. In dieser Klasse steckt die gesamte Logik für die Baustein-Erkennung. |
| 15 | `def __init__(self):` | Definiert den Konstruktor. Diese Methode wird automatisch ausgeführt, wenn ein `BausteinDetector` erstellt wird. |
| 16 | `rospy.init_node("baustein_detector", anonymous=True)` | Startet den ROS-Knoten mit dem Namen `baustein_detector`. `anonymous=True` erlaubt ROS, bei Bedarf eine eindeutige Nummer an den Namen anzuhängen. |
| 17 | Leerzeile | Trennt die Knotenerstellung von den Hilfsobjekten. |
| 18 | `self.bridge = CvBridge()` | Erstellt ein `CvBridge`-Objekt. Damit werden später ROS-Bilder in OpenCV-Bilder umgewandelt. |
| 19 | `self.model = YOLO(MODEL_PATH)` | Lädt das YOLO-Modell aus dem angegebenen Pfad. Ab jetzt kann das Modell Bilder analysieren. |
| 20 | Leerzeile | Trennt das Laden des Modells von den Publishern. |
| 21 | `self.detected_pub = rospy.Publisher("/baustein_detected", Bool, queue_size=10)` | Erstellt einen Publisher für das Topic `/baustein_detected`. Dort wird `True` gesendet, wenn ein Baustein erkannt wurde, sonst `False`. |
| 22 | `self.center_pub = rospy.Publisher("/baustein_center", Point, queue_size=10)` | Erstellt einen Publisher für das Topic `/baustein_center`. Dort wird die Bildposition der Bausteinmitte gesendet. |
| 23 | `self.conf_pub = rospy.Publisher("/baustein_confidence", Float32, queue_size=10)` | Erstellt einen Publisher für das Topic `/baustein_confidence`. Dort wird die beste Erkennungs-Sicherheit gesendet. |
| 24 | Leerzeile | Trennt die Publisher vom Subscriber. |
| 25 | `self.sub = rospy.Subscriber(` | Beginnt die Erstellung eines Subscribers. Dieser Subscriber hört auf neue Kamerabilder. |
| 26 | `IMAGE_TOPIC,` | Gibt an, auf welchem Topic gehört wird. Hier ist es `/camera/color/image_raw`. |
| 27 | `Image,` | Gibt den Nachrichtentyp des Topics an. Das Kameratopic sendet Nachrichten vom Typ `Image`. |
| 28 | `self.image_callback,` | Gibt an, welche Methode bei jedem neuen Kamerabild aufgerufen wird. |
| 29 | `queue_size=1,` | Legt fest, dass nur ein Bild zwischengespeichert wird. Das hilft, möglichst aktuelle Kamerabilder zu verarbeiten. |
| 30 | `buff_size=2**24` | Legt die Puffergröße für große Bildnachrichten fest. `2**24` bedeutet 2 hoch 24 Bytes. |
| 31 | `)` | Beendet den Aufruf von `rospy.Subscriber`. |
| 32 | Leerzeile | Trennt den Subscriber von der Startmeldung. |
| 33 | `rospy.loginfo("Baustein-Detektor gestartet.")` | Gibt im Terminal aus, dass der Baustein-Detektor gestartet wurde. |
| 34 | Leerzeile | Trennt den Konstruktor von der Callback-Methode. |
| 35 | `def image_callback(self, msg):` | Definiert die Callback-Methode. Sie wird automatisch aufgerufen, sobald ein neues Kamerabild ankommt. |
| 36 | `try:` | Startet einen geschützten Codebereich. Wenn darin ein Fehler passiert, springt das Programm zur Fehlerbehandlung bei `except`. |
| 37 | `frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")` | Wandelt das ROS-Kamerabild in ein OpenCV-Bild um. `bgr8` ist ein übliches Farbformat für OpenCV. |
| 38 | `results = self.model.predict(source=frame, conf=CONFIDENCE_THRESHOLD, verbose=False)` | Übergibt das Bild an YOLO. YOLO sucht nach Objekten und gibt Erkennungsergebnisse zurück. |
| 39 | Leerzeile | Trennt die YOLO-Auswertung von den Startwerten. |
| 40 | `detected = False` | Setzt zuerst: Es wurde noch kein Baustein erkannt. |
| 41 | `best_conf = 0.0` | Speichert die bisher beste Sicherheit. Am Anfang ist sie `0.0`, weil noch keine Erkennung ausgewertet wurde. |
| 42 | `best_center = None` | Speichert später den Mittelpunkt der besten Erkennung. `None` bedeutet: Noch kein Mittelpunkt vorhanden. |
| 43 | Leerzeile | Trennt die Startwerte von der Prüfung der YOLO-Ergebnisse. |
| 44 | `if results and len(results) > 0:` | Prüft, ob YOLO überhaupt Ergebnisse zurückgegeben hat. |
| 45 | `boxes = results[0].boxes` | Holt die Bounding Boxes aus dem ersten Ergebnis. Eine Bounding Box ist das Rechteck um ein erkanntes Objekt. |
| 46 | `if boxes is not None and len(boxes) > 0:` | Prüft, ob wirklich Bounding Boxes vorhanden sind. |
| 47 | `for box in boxes:` | Geht jede erkannte Box einzeln durch. |
| 48 | `conf = float(box.conf[0].item())` | Liest die Sicherheit dieser Box aus und wandelt sie in eine normale Python-Kommazahl um. |
| 49 | `xyxy = box.xyxy[0].tolist()` | Liest die Koordinaten der Box aus. Das Format ist `x1, y1, x2, y2`. |
| 50 | `x1, y1, x2, y2 = xyxy` | Teilt die vier Koordinaten in einzelne Variablen auf. |
| 51 | Leerzeile | Trennt die Box-Koordinaten von der Mittelpunktberechnung. |
| 52 | `cx = (x1 + x2) / 2.0` | Berechnet die x-Koordinate der Mitte der Box. |
| 53 | `cy = (y1 + y2) / 2.0` | Berechnet die y-Koordinate der Mitte der Box. |
| 54 | Leerzeile | Trennt die Mittelpunktberechnung von der Auswahl der besten Box. |
| 55 | `if conf > best_conf:` | Prüft, ob diese Box sicherer ist als alle vorherigen Boxen. |
| 56 | `best_conf = conf` | Speichert die neue beste Sicherheit. |
| 57 | `best_center = (cx, cy)` | Speichert den Mittelpunkt der besten Box als Tupel mit x- und y-Wert. |
| 58 | Leerzeile | Trennt die Box-Schleife von der Erkennungsprüfung. |
| 59 | `if best_center is not None:` | Prüft, ob am Ende mindestens eine passende Box gefunden wurde. |
| 60 | `detected = True` | Setzt die Erkennung auf `True`, weil ein Baustein gefunden wurde. |
| 61 | Leerzeile | Trennt die Auswertung von der Veröffentlichung. |
| 62 | `self.detected_pub.publish(Bool(data=detected))` | Veröffentlicht auf `/baustein_detected`, ob ein Baustein erkannt wurde. |
| 63 | Leerzeile | Trennt die allgemeine Erkennung von den Details. |
| 64 | `if detected:` | Prüft, ob wirklich ein Baustein erkannt wurde. Nur dann werden Mittelpunkt und echte Sicherheit gesendet. |
| 65 | `p = Point()` | Erstellt eine neue `Point`-Nachricht für den Mittelpunkt. |
| 66 | `p.x = best_center[0]` | Speichert die x-Koordinate des Mittelpunkts in der Nachricht. |
| 67 | `p.y = best_center[1]` | Speichert die y-Koordinate des Mittelpunkts in der Nachricht. |
| 68 | `p.z = 0.0` | Setzt `z` auf `0.0`, weil der Mittelpunkt nur im 2D-Kamerabild liegt. |
| 69 | `self.center_pub.publish(p)` | Veröffentlicht den Mittelpunkt auf `/baustein_center`. |
| 70 | `self.conf_pub.publish(Float32(data=best_conf))` | Veröffentlicht die beste Erkennungs-Sicherheit auf `/baustein_confidence`. |
| 71 | `else:` | Wird ausgeführt, wenn kein Baustein erkannt wurde. |
| 72 | `self.conf_pub.publish(Float32(data=0.0))` | Veröffentlicht eine Sicherheit von `0.0`, damit andere Knoten wissen: aktuell gibt es keine gültige Erkennung. |
| 73 | Leerzeile | Trennt die normale Verarbeitung von der Fehlerbehandlung. |
| 74 | `except Exception as e:` | Fängt Fehler ab, die während der Bildverarbeitung passieren können. |
| 75 | `rospy.logerr(f"Fehler in image_callback: {e}")` | Gibt den Fehler als ROS-Fehlermeldung aus. Dadurch stürzt der Knoten nicht sofort wegen eines einzelnen fehlerhaften Bildes ab. |
| 76 | Leerzeile | Trennt die Klasse vom Startblock. |
| 77 | `if __name__ == "__main__":` | Prüft, ob diese Datei direkt gestartet wurde. Nur dann wird der folgende Code ausgeführt. |
| 78 | `BausteinDetector()` | Erstellt ein Objekt der Klasse `BausteinDetector`. Dadurch werden ROS-Knoten, Modell, Publisher und Subscriber eingerichtet. |
| 79 | `rospy.spin()` | Hält das Programm am Laufen. Ohne `spin()` würde das Programm direkt enden und keine Kamerabilder verarbeiten. |

## Ablauf des Programms

```text
Programm starten
        ↓
ROS-Knoten baustein_detector erstellen
        ↓
YOLO-Modell best.pt laden
        ↓
Publisher für detected, center und confidence erstellen
        ↓
Kamerabild-Topic abonnieren
        ↓
Neues Kamerabild kommt an
        ↓
ROS-Bild in OpenCV-Bild umwandeln
        ↓
YOLO erkennt mögliche Bausteine
        ↓
Beste Erkennung auswählen
        ↓
Ergebnis auf ROS-Topics veröffentlichen
        ↓
Auf das nächste Kamerabild warten
```

## Welche Topics werden benutzt?

| Topic | Richtung | Nachrichtentyp | Bedeutung |
| --- | --- | --- | --- |
| `/camera/color/image_raw` | Eingang | `sensor_msgs/Image` | Von hier kommen die Kamerabilder. |
| `/baustein_detected` | Ausgang | `std_msgs/Bool` | `True`, wenn ein Baustein erkannt wurde, sonst `False`. |
| `/baustein_center` | Ausgang | `geometry_msgs/Point` | Mittelpunkt der besten Erkennung im Bild. |
| `/baustein_confidence` | Ausgang | `std_msgs/Float32` | Sicherheit der besten Erkennung. |

## Wo werden die wichtigsten Einstellungen geändert?

Die wichtigsten Einstellungen stehen oben in der Datei:

```python
MODEL_PATH = "/home/agilex/best.pt"
IMAGE_TOPIC = "/camera/color/image_raw"
CONFIDENCE_THRESHOLD = 0.5
```

| Einstellung | Bedeutung |
| --- | --- |
| `MODEL_PATH` | Pfad zur trainierten YOLO-Datei. Wenn das Modell woanders liegt, muss dieser Pfad angepasst werden. |
| `IMAGE_TOPIC` | Name des Kamera-Topics. Wenn deine Kamera ein anderes Topic nutzt, muss dieser Wert geändert werden. |
| `CONFIDENCE_THRESHOLD` | Mindest-Sicherheit für Erkennungen. Ein höherer Wert macht die Erkennung strenger. |

## Was bedeutet der Mittelpunkt?

YOLO liefert für jedes erkannte Objekt ein Rechteck:

```python
x1, y1, x2, y2
```

Diese Werte bedeuten:

| Wert | Bedeutung |
| --- | --- |
| `x1` | Linke Kante der Box im Bild. |
| `y1` | Obere Kante der Box im Bild. |
| `x2` | Rechte Kante der Box im Bild. |
| `y2` | Untere Kante der Box im Bild. |

Der Code berechnet daraus die Mitte:

```python
cx = (x1 + x2) / 2.0
cy = (y1 + y2) / 2.0
```

`cx` sagt, wie weit links oder rechts der Baustein im Bild ist. `cy` sagt, wie weit oben oder unten der Baustein im Bild ist.

## Wichtig zu wissen

- Dieser Code benutzt `rospy` und ist damit im ROS1-Stil geschrieben.
- Das YOLO-Modell muss unter `/home/agilex/best.pt` vorhanden sein, sonst kann der Knoten nicht richtig starten.
- Das Kamera-Topic `/camera/color/image_raw` muss Bilder liefern.
- Es wird immer nur die Erkennung mit der höchsten Sicherheit weitergegeben.
- Wenn kein Baustein erkannt wird, sendet `/baustein_detected` den Wert `False` und `/baustein_confidence` den Wert `0.0`.
- `/baustein_center` wird nur veröffentlicht, wenn tatsächlich ein Baustein erkannt wurde.
- `cv2` wird importiert, aber in dieser Datei aktuell nicht verwendet.
