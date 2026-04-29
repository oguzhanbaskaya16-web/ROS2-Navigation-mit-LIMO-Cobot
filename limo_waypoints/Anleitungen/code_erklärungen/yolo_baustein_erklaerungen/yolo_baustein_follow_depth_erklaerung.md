# Erklärung zu `yolo_baustein_follow_depth.py`

Diese Datei steuert den LIMO-Roboter so, dass er einem erkannten Baustein folgt und dabei zusätzlich den Abstand aus dem Tiefenbild verwendet.

Der Unterschied zu `yolo_baustein_follow.py` ist: Diese Version fährt nicht einfach nur langsam auf den Baustein zu. Sie prüft auch, wie weit der Baustein entfernt ist. Wenn der Baustein im passenden Greifabstand ist, stoppt der Roboter und sendet ein Signal auf `/greif_start`.

Der Ablauf ist:

1. Der ROS-Knoten startet.
2. Er empfängt die Baustein-Erkennung über `/baustein_detected`.
3. Er empfängt die Baustein-Mitte über `/baustein_center`.
4. Er empfängt das Tiefenbild über `/camera/depth/image_raw`.
5. Er berechnet den Abstand am Baustein.
6. Er richtet den Roboter links/rechts auf den Baustein aus.
7. Er fährt vorwärts, bis der Baustein im Greifabstand ist.
8. Er wartet kurz zur Bestätigung.
9. Er sendet ein Greifsignal auf `/greif_start`.

## Wichtige Begriffe

| Begriff | Einfache Erklärung |
| --- | --- |
| ROS-Knoten | Ein einzelnes Programm in ROS. Hier steuert es das Folgen und Stoppen vor dem Baustein. |
| Topic | Ein Kommunikationskanal in ROS. Programme senden und empfangen darüber Nachrichten. |
| Publisher | Sendet Nachrichten auf ein Topic. |
| Subscriber | Empfängt Nachrichten von einem Topic. |
| Callback | Eine Funktion, die automatisch ausgeführt wird, wenn eine neue Nachricht ankommt. |
| `Twist` | ROS-Nachricht für Bewegungsbefehle. Sie enthält Vorwärtsgeschwindigkeit und Drehgeschwindigkeit. |
| `Point` | ROS-Nachricht mit `x`, `y` und `z`. Hier werden `x` und `y` für die Bausteinposition im Bild verwendet. |
| `Image` | ROS-Nachricht für Kamerabilder. Hier wird sie für das Tiefenbild genutzt. |
| `Bool` | ROS-Nachricht für `True` oder `False`. |
| Tiefenbild | Ein Bild, bei dem jeder Pixel eine Entfernung zur Kamera enthält. |
| Greiffenster | Der erlaubte Abstand, in dem der Roboter stoppen und den Greifvorgang starten darf. |

## Vollständiger Code

```python
#!/usr/bin/env python3
import numpy as np
import rospy
from cv_bridge import CvBridge
from geometry_msgs.msg import Point, Twist
from sensor_msgs.msg import Image
from std_msgs.msg import Bool


COLOR_IMAGE_WIDTH = 640.0
COLOR_IMAGE_HEIGHT = 480.0
IMAGE_CENTER_X = COLOR_IMAGE_WIDTH / 2.0

CENTER_TOLERANCE = 40.0
CONFIRM_CENTER_TOLERANCE = 70.0
ANGULAR_SPEED = 0.25

TARGET_DISTANCE_M = 0.55
STOP_DISTANCE_MIN_M = 0.55
STOP_DISTANCE_MAX_M = 0.63
GRASP_CONFIRMATION_S = 3.0
MAX_LINEAR_SPEED = 0.06
MIN_LINEAR_SPEED = 0.02

DEPTH_WINDOW_SIZE = 31
LAST_DEPTH_TIMEOUT_S = 0.8
MAX_VALID_DISTANCE_M = 2.0
MAX_DISTANCE_JUMP_M = 0.45
BOTTOM_STOP_Y = 465.0


class BausteinDepthFollower:
    def __init__(self):
        rospy.init_node("baustein_depth_follower", anonymous=True)

        self.bridge = CvBridge()
        self.detected = False
        self.center_x = None
        self.center_y = None
        self.depth_image = None
        self.last_valid_distance_m = None
        self.last_valid_distance_time = rospy.Time(0)
        self.grasp_requested = False
        self.grasp_candidate_since = None

        self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        self.grasp_pub = rospy.Publisher("/greif_start", Bool, queue_size=1, latch=True)

        rospy.Subscriber("/baustein_detected", Bool, self.detected_callback)
        rospy.Subscriber("/baustein_center", Point, self.center_callback)
        rospy.Subscriber("/camera/depth/image_raw", Image, self.depth_callback, queue_size=1)

        self.rate = rospy.Rate(10)

    def detected_callback(self, msg):
        self.detected = msg.data

    def center_callback(self, msg):
        self.center_x = msg.x
        self.center_y = msg.y

    def depth_callback(self, msg):
        try:
            self.depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        except Exception as exc:
            rospy.logwarn_throttle(2.0, "Depth-Bild konnte nicht gelesen werden: %s", exc)

    def stop_robot(self):
        self.cmd_pub.publish(Twist())

    def reset_grasp_confirmation(self):
        if self.grasp_candidate_since is not None:
            rospy.loginfo("Greifbestaetigung abgebrochen.")
        self.grasp_candidate_since = None

    def get_depth_at_baustein(self):
        if self.depth_image is None or self.center_x is None or self.center_y is None:
            return None

        height, width = self.depth_image.shape[:2]
        depth_x = int(self.center_x * width / COLOR_IMAGE_WIDTH)
        depth_y = int(self.center_y * height / COLOR_IMAGE_HEIGHT)

        half_window = DEPTH_WINDOW_SIZE // 2
        x1 = max(0, depth_x - half_window)
        x2 = min(width, depth_x + half_window + 1)
        y1 = max(0, depth_y - half_window)
        y2 = min(height, depth_y + half_window + 1)

        depth_values = self.depth_image[y1:y2, x1:x2].astype(np.float32)

        if self.depth_image.dtype == np.uint16:
            depth_values = depth_values / 1000.0

        valid = depth_values[np.isfinite(depth_values)]
        valid = valid[(valid > 0.05) & (valid < MAX_VALID_DISTANCE_M)]

        if valid.size == 0:
            if self.last_valid_distance_m is None:
                return None

            age = (rospy.Time.now() - self.last_valid_distance_time).to_sec()
            if age <= LAST_DEPTH_TIMEOUT_S:
                return self.last_valid_distance_m

            return None

        distance_m = float(np.median(valid))

        if (
            self.last_valid_distance_m is not None
            and self.last_valid_distance_m < 0.9
            and distance_m - self.last_valid_distance_m > MAX_DISTANCE_JUMP_M
        ):
            return self.last_valid_distance_m

        self.last_valid_distance_m = distance_m
        self.last_valid_distance_time = rospy.Time.now()
        return distance_m

    def run(self):
        rospy.loginfo("Baustein-Depth-Follower gestartet. Zielabstand: %.2f m", TARGET_DISTANCE_M)

        while not rospy.is_shutdown():
            cmd = Twist()

            if self.grasp_requested:
                self.stop_robot()
                self.rate.sleep()
                continue

            if not self.detected or self.center_x is None:
                self.reset_grasp_confirmation()
                self.stop_robot()
                self.rate.sleep()
                continue

            distance_m = self.get_depth_at_baustein()
            if distance_m is None:
                self.reset_grasp_confirmation()
                rospy.logwarn_throttle(2.0, "Kein gueltiger Depth-Abstand am Baustein.")
                self.stop_robot()
                self.rate.sleep()
                continue

            error_x = self.center_x - IMAGE_CENTER_X

            rospy.loginfo_throttle(
                1.0,
                "Baustein: x=%.0f px, y=%.0f px, Abstand=%.2f m",
                self.center_x,
                self.center_y,
                distance_m,
            )

            if self.center_y is not None and self.center_y >= BOTTOM_STOP_Y:
                self.reset_grasp_confirmation()
                rospy.loginfo_throttle(
                    2.0,
                    "Baustein ist am unteren Bildrand. Stoppe bei %.2f m.",
                    distance_m,
                )
                self.stop_robot()
                self.rate.sleep()
                continue

            active_center_tolerance = (
                CONFIRM_CENTER_TOLERANCE
                if self.grasp_candidate_since is not None
                else CENTER_TOLERANCE
            )

            if abs(error_x) > active_center_tolerance:
                self.reset_grasp_confirmation()
                cmd.angular.z = ANGULAR_SPEED if error_x < 0 else -ANGULAR_SPEED
                cmd.linear.x = 0.0
            else:
                if STOP_DISTANCE_MIN_M <= distance_m <= STOP_DISTANCE_MAX_M:
                    self.stop_robot()

                    now = rospy.Time.now()
                    if self.grasp_candidate_since is None:
                        self.grasp_candidate_since = now
                        rospy.loginfo(
                            "Greiffenster erreicht bei %.2f m. Warte %.1f s zur Bestaetigung.",
                            distance_m,
                            GRASP_CONFIRMATION_S,
                        )

                    confirmation_age = (now - self.grasp_candidate_since).to_sec()
                    rospy.loginfo_throttle(
                        1.0,
                        "Greifabstand wird bestaetigt: %.1f/%.1f s",
                        confirmation_age,
                        GRASP_CONFIRMATION_S,
                    )

                    if confirmation_age >= GRASP_CONFIRMATION_S and not self.grasp_requested:
                        self.grasp_pub.publish(Bool(data=True))
                        self.grasp_requested = True
                        rospy.loginfo("Greifsignal auf /greif_start gesendet.")

                    self.rate.sleep()
                    continue

                if distance_m > STOP_DISTANCE_MAX_M:
                    self.reset_grasp_confirmation()
                    cmd.angular.z = 0.0
                    cmd.linear.x = min(
                        MAX_LINEAR_SPEED,
                        max(MIN_LINEAR_SPEED, (distance_m - STOP_DISTANCE_MAX_M) * 0.25),
                    )
                else:
                    self.stop_robot()
                    rospy.logwarn_throttle(
                        2.0,
                        "Baustein ist naeher als das Greiffenster: %.2f m < %.2f m.",
                        distance_m,
                        STOP_DISTANCE_MIN_M,
                    )
                    self.rate.sleep()
                    continue

            self.cmd_pub.publish(cmd)
            self.rate.sleep()


if __name__ == "__main__":
    try:
        BausteinDepthFollower().run()
    except rospy.ROSInterruptException:
        pass
```

## Erklärung Zeile für Zeile

| Zeile | Code | Anfängerfreundliche Erklärung |
| --- | --- | --- |
| 1 | `#!/usr/bin/env python3` | Sagt dem Betriebssystem, dass diese Datei mit Python 3 gestartet werden soll. |
| 2 | `import numpy as np` | Importiert NumPy. Das wird später benutzt, um Tiefenwerte im Bild auszuwerten. |
| 3 | `import rospy` | Importiert die Python-Bibliothek für ROS1. Damit kann der Code mit ROS-Topics arbeiten. |
| 4 | `from cv_bridge import CvBridge` | Importiert `CvBridge`. Damit werden ROS-Bilder in normale Python/OpenCV-Bilder umgewandelt. |
| 5 | `from geometry_msgs.msg import Point, Twist` | Importiert `Point` für Bildpositionen und `Twist` für Bewegungsbefehle. |
| 6 | `from sensor_msgs.msg import Image` | Importiert den Nachrichtentyp `Image`, der für Kamerabilder und Tiefenbilder verwendet wird. |
| 7 | `from std_msgs.msg import Bool` | Importiert `Bool`, also einen Nachrichtentyp für `True` oder `False`. |
| 8 | Leerzeile | Macht den Importbereich übersichtlicher. |
| 9 | Leerzeile | Trennt die Imports deutlich von den Einstellungen. |
| 10 | `COLOR_IMAGE_WIDTH = 640.0` | Speichert die Breite des Farbbildes. Diese Breite wird für die Umrechnung zur Tiefenbildposition genutzt. |
| 11 | `COLOR_IMAGE_HEIGHT = 480.0` | Speichert die Höhe des Farbbildes. Auch sie wird für die Umrechnung zur Tiefenbildposition genutzt. |
| 12 | `IMAGE_CENTER_X = COLOR_IMAGE_WIDTH / 2.0` | Berechnet die horizontale Bildmitte. Bei 640 Pixeln ist das 320. |
| 13 | Leerzeile | Trennt die Bildgröße von den Steuerwerten. |
| 14 | `CENTER_TOLERANCE = 40.0` | Legt fest, wie weit der Baustein von der Bildmitte abweichen darf, bevor der Roboter sich drehen muss. |
| 15 | `CONFIRM_CENTER_TOLERANCE = 70.0` | Legt eine etwas größere Toleranz während der Greifbestätigung fest. Dadurch wird die Bestätigung nicht zu schnell abgebrochen. |
| 16 | `ANGULAR_SPEED = 0.25` | Speichert die Drehgeschwindigkeit des Roboters. |
| 17 | Leerzeile | Trennt die Ausrichtungseinstellungen von den Abstandseinstellungen. |
| 18 | `TARGET_DISTANCE_M = 0.55` | Speichert den gewünschten Zielabstand in Metern. Dieser Wert wird vor allem für die Startmeldung verwendet. |
| 19 | `STOP_DISTANCE_MIN_M = 0.55` | Untere Grenze des Greiffensters. Näher als 0,55 m ist zu nah. |
| 20 | `STOP_DISTANCE_MAX_M = 0.63` | Obere Grenze des Greiffensters. Weiter als 0,63 m ist noch zu weit weg. |
| 21 | `GRASP_CONFIRMATION_S = 3.0` | Der Roboter muss 3 Sekunden im Greiffenster bleiben, bevor das Greifsignal gesendet wird. |
| 22 | `MAX_LINEAR_SPEED = 0.06` | Maximale Vorwärtsgeschwindigkeit. Der Roboter soll langsam und kontrolliert fahren. |
| 23 | `MIN_LINEAR_SPEED = 0.02` | Minimale Vorwärtsgeschwindigkeit. So fährt der Roboter auch bei kleiner Entfernung noch mit einer Mindestgeschwindigkeit. |
| 24 | Leerzeile | Trennt die Fahrwerte von den Tiefenbildwerten. |
| 25 | `DEPTH_WINDOW_SIZE = 31` | Legt fest, wie groß der Bereich um die Bausteinmitte ist, aus dem Tiefenwerte gelesen werden. Hier sind es 31 mal 31 Pixel. |
| 26 | `LAST_DEPTH_TIMEOUT_S = 0.8` | Ein alter gültiger Abstand darf maximal 0,8 Sekunden weiterverwendet werden. |
| 27 | `MAX_VALID_DISTANCE_M = 2.0` | Tiefenwerte über 2 Meter werden ignoriert, weil sie für diesen Greifvorgang nicht sinnvoll sind. |
| 28 | `MAX_DISTANCE_JUMP_M = 0.45` | Wenn der Abstand plötzlich stark springt, wird dieser Sprung ignoriert. Das schützt vor fehlerhaften Tiefenwerten. |
| 29 | `BOTTOM_STOP_Y = 465.0` | Wenn der Baustein sehr weit unten im Bild ist, stoppt der Roboter. Das kann bedeuten, dass der Baustein sehr nah ist. |
| 30 | Leerzeile | Trennt die Einstellungen von der Klasse. |
| 31 | Leerzeile | Macht den Beginn der Klasse optisch klarer. |
| 32 | `class BausteinDepthFollower:` | Definiert die Klasse, in der die komplette Steuerlogik steckt. |
| 33 | `def __init__(self):` | Definiert den Konstruktor. Er wird automatisch beim Erstellen des Objekts ausgeführt. |
| 34 | `rospy.init_node("baustein_depth_follower", anonymous=True)` | Startet den ROS-Knoten mit dem Namen `baustein_depth_follower`. |
| 35 | Leerzeile | Trennt den ROS-Start von den internen Variablen. |
| 36 | `self.bridge = CvBridge()` | Erstellt eine Brücke zum Umwandeln von ROS-Bildern in auswertbare Bilddaten. |
| 37 | `self.detected = False` | Speichert, ob aktuell ein Baustein erkannt wurde. Am Anfang ist das `False`. |
| 38 | `self.center_x = None` | Speichert später die x-Position der Bausteinmitte. Am Anfang ist noch keine Position bekannt. |
| 39 | `self.center_y = None` | Speichert später die y-Position der Bausteinmitte. |
| 40 | `self.depth_image = None` | Speichert später das aktuelle Tiefenbild. Am Anfang gibt es noch kein Tiefenbild. |
| 41 | `self.last_valid_distance_m = None` | Speichert den letzten gültigen Abstand in Metern. Am Anfang gibt es noch keinen. |
| 42 | `self.last_valid_distance_time = rospy.Time(0)` | Speichert den Zeitpunkt des letzten gültigen Abstands. `rospy.Time(0)` ist ein Startwert. |
| 43 | `self.grasp_requested = False` | Speichert, ob das Greifsignal bereits gesendet wurde. Am Anfang wurde noch nichts gesendet. |
| 44 | `self.grasp_candidate_since = None` | Speichert später, seit wann der Baustein im passenden Greifabstand ist. |
| 45 | Leerzeile | Trennt die internen Variablen von den Publishern. |
| 46 | `self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)` | Erstellt den Publisher für Fahrbefehle. Über `/cmd_vel` wird der Roboter bewegt oder gestoppt. |
| 47 | `self.grasp_pub = rospy.Publisher("/greif_start", Bool, queue_size=1, latch=True)` | Erstellt den Publisher für das Greifsignal. `latch=True` bedeutet: Die letzte Nachricht bleibt für neue Empfänger verfügbar. |
| 48 | Leerzeile | Trennt die Publisher von den Subscribern. |
| 49 | `rospy.Subscriber("/baustein_detected", Bool, self.detected_callback)` | Abonniert das Topic, das sagt, ob ein Baustein erkannt wurde. |
| 50 | `rospy.Subscriber("/baustein_center", Point, self.center_callback)` | Abonniert das Topic mit der Bausteinmitte im Bild. |
| 51 | `rospy.Subscriber("/camera/depth/image_raw", Image, self.depth_callback, queue_size=1)` | Abonniert das Tiefenbild der Kamera. `queue_size=1` sorgt dafür, dass möglichst aktuelle Bilder verwendet werden. |
| 52 | Leerzeile | Trennt die Subscriber von der Schleifenrate. |
| 53 | `self.rate = rospy.Rate(10)` | Legt fest, dass die Hauptschleife ungefähr 10-mal pro Sekunde laufen soll. |
| 54 | Leerzeile | Trennt den Konstruktor von der ersten Callback-Funktion. |
| 55 | `def detected_callback(self, msg):` | Definiert die Funktion, die bei neuen Nachrichten auf `/baustein_detected` ausgeführt wird. |
| 56 | `self.detected = msg.data` | Speichert den empfangenen Wert. `True` bedeutet erkannt, `False` bedeutet nicht erkannt. |
| 57 | Leerzeile | Trennt die Callback-Funktionen. |
| 58 | `def center_callback(self, msg):` | Definiert die Funktion, die bei neuen Nachrichten auf `/baustein_center` ausgeführt wird. |
| 59 | `self.center_x = msg.x` | Speichert die x-Position der Bausteinmitte. |
| 60 | `self.center_y = msg.y` | Speichert die y-Position der Bausteinmitte. |
| 61 | Leerzeile | Trennt die Positions-Callback-Funktion von der Tiefenbild-Callback-Funktion. |
| 62 | `def depth_callback(self, msg):` | Definiert die Funktion, die bei neuen Tiefenbildern ausgeführt wird. |
| 63 | `try:` | Startet einen geschützten Bereich. Falls beim Lesen des Tiefenbildes ein Fehler passiert, stürzt das Programm nicht sofort ab. |
| 64 | `self.depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")` | Wandelt das ROS-Tiefenbild in ein Bildformat um, das Python auswerten kann. `passthrough` übernimmt das Originalformat. |
| 65 | `except Exception as exc:` | Fängt Fehler ab, die beim Umwandeln des Tiefenbildes auftreten können. |
| 66 | `rospy.logwarn_throttle(2.0, "Depth-Bild konnte nicht gelesen werden: %s", exc)` | Gibt höchstens alle 2 Sekunden eine Warnung aus, falls das Tiefenbild nicht gelesen werden kann. |
| 67 | Leerzeile | Trennt die Tiefenbild-Funktion von der Stopp-Funktion. |
| 68 | `def stop_robot(self):` | Definiert eine Funktion zum Stoppen des Roboters. |
| 69 | `self.cmd_pub.publish(Twist())` | Sendet eine leere `Twist`-Nachricht. Das bedeutet: keine Vorwärtsbewegung und keine Drehung. |
| 70 | Leerzeile | Trennt die Stopp-Funktion von der Greifbestätigung. |
| 71 | `def reset_grasp_confirmation(self):` | Definiert eine Funktion, die eine laufende Greifbestätigung zurücksetzt. |
| 72 | `if self.grasp_candidate_since is not None:` | Prüft, ob gerade eine Greifbestätigung aktiv ist. |
| 73 | `rospy.loginfo("Greifbestaetigung abgebrochen.")` | Gibt aus, dass die Greifbestätigung abgebrochen wurde. |
| 74 | `self.grasp_candidate_since = None` | Setzt die Startzeit der Greifbestätigung zurück. Danach muss die Bestätigung neu beginnen. |
| 75 | Leerzeile | Trennt die Greifbestätigung von der Abstandsmessung. |
| 76 | `def get_depth_at_baustein(self):` | Definiert eine Funktion, die den Abstand am Baustein aus dem Tiefenbild berechnet. |
| 77 | `if self.depth_image is None or self.center_x is None or self.center_y is None:` | Prüft, ob Tiefenbild oder Bausteinposition fehlen. Ohne diese Daten kann kein Abstand berechnet werden. |
| 78 | `return None` | Gibt `None` zurück. Das bedeutet: Es gibt aktuell keinen gültigen Abstand. |
| 79 | Leerzeile | Trennt die Datenprüfung von der Bildgrößenberechnung. |
| 80 | `height, width = self.depth_image.shape[:2]` | Liest Höhe und Breite des Tiefenbildes aus. |
| 81 | `depth_x = int(self.center_x * width / COLOR_IMAGE_WIDTH)` | Rechnet die x-Position aus dem Farbbild auf die x-Position im Tiefenbild um. |
| 82 | `depth_y = int(self.center_y * height / COLOR_IMAGE_HEIGHT)` | Rechnet die y-Position aus dem Farbbild auf die y-Position im Tiefenbild um. |
| 83 | Leerzeile | Trennt die Umrechnung von der Fensterberechnung. |
| 84 | `half_window = DEPTH_WINDOW_SIZE // 2` | Berechnet die halbe Fenstergröße. Bei 31 ergibt das 15. |
| 85 | `x1 = max(0, depth_x - half_window)` | Berechnet den linken Rand des Tiefenbereichs. `max(0, ...)` verhindert Werte außerhalb des Bildes. |
| 86 | `x2 = min(width, depth_x + half_window + 1)` | Berechnet den rechten Rand des Tiefenbereichs. `min(width, ...)` verhindert Werte außerhalb des Bildes. |
| 87 | `y1 = max(0, depth_y - half_window)` | Berechnet den oberen Rand des Tiefenbereichs. |
| 88 | `y2 = min(height, depth_y + half_window + 1)` | Berechnet den unteren Rand des Tiefenbereichs. |
| 89 | Leerzeile | Trennt die Fenstergrenzen vom Ausschneiden der Tiefenwerte. |
| 90 | `depth_values = self.depth_image[y1:y2, x1:x2].astype(np.float32)` | Schneidet den Bereich um den Baustein aus dem Tiefenbild aus und wandelt die Werte in Kommazahlen um. |
| 91 | Leerzeile | Trennt das Ausschneiden von der Einheit-Umrechnung. |
| 92 | `if self.depth_image.dtype == np.uint16:` | Prüft, ob die Tiefenwerte als 16-Bit-Ganzzahlen vorliegen. Das ist häufig bei Tiefenkameras der Fall. |
| 93 | `depth_values = depth_values / 1000.0` | Wandelt Millimeter in Meter um. Beispiel: 550 mm werden zu 0,55 m. |
| 94 | Leerzeile | Trennt die Umrechnung vom Filtern der Werte. |
| 95 | `valid = depth_values[np.isfinite(depth_values)]` | Entfernt ungültige Werte wie `NaN` oder unendliche Werte. |
| 96 | `valid = valid[(valid > 0.05) & (valid < MAX_VALID_DISTANCE_M)]` | Behält nur sinnvolle Abstände: größer als 5 cm und kleiner als der maximale gültige Abstand. |
| 97 | Leerzeile | Trennt das Filtern von der Prüfung, ob gültige Werte vorhanden sind. |
| 98 | `if valid.size == 0:` | Prüft, ob nach dem Filtern kein einziger gültiger Tiefenwert übrig ist. |
| 99 | `if self.last_valid_distance_m is None:` | Prüft, ob es auch keinen alten gültigen Abstand gibt. |
| 100 | `return None` | Gibt `None` zurück, weil kein aktueller und kein alter Abstand verfügbar ist. |
| 101 | Leerzeile | Trennt die erste Notfallprüfung von der Zeitprüfung. |
| 102 | `age = (rospy.Time.now() - self.last_valid_distance_time).to_sec()` | Berechnet, wie alt der letzte gültige Abstand ist. |
| 103 | `if age <= LAST_DEPTH_TIMEOUT_S:` | Prüft, ob der alte Abstand noch frisch genug ist. |
| 104 | `return self.last_valid_distance_m` | Verwendet den letzten gültigen Abstand weiter. |
| 105 | Leerzeile | Trennt die Nutzung alter Werte vom endgültigen Fehlerfall. |
| 106 | `return None` | Gibt `None` zurück, wenn auch der alte Abstand zu alt ist. |
| 107 | Leerzeile | Trennt den Fall ohne gültige Werte von der normalen Abstandberechnung. |
| 108 | `distance_m = float(np.median(valid))` | Berechnet den mittleren Abstand mit dem Median. Der Median ist robust gegen einzelne falsche Messwerte. |
| 109 | Leerzeile | Trennt die Abstandberechnung von der Sprungprüfung. |
| 110 | `if (` | Beginnt eine mehrzeilige Prüfung für unrealistische Abstandssprünge. |
| 111 | `self.last_valid_distance_m is not None` | Erste Bedingung: Es muss bereits einen alten gültigen Abstand geben. |
| 112 | `and self.last_valid_distance_m < 0.9` | Zweite Bedingung: Der alte Abstand war relativ nah am Roboter. |
| 113 | `and distance_m - self.last_valid_distance_m > MAX_DISTANCE_JUMP_M` | Dritte Bedingung: Der neue Abstand ist plötzlich viel größer als der alte. |
| 114 | `):` | Beendet die mehrzeilige `if`-Bedingung. |
| 115 | `return self.last_valid_distance_m` | Ignoriert den plötzlichen Sprung und verwendet den letzten gültigen Abstand weiter. |
| 116 | Leerzeile | Trennt die Sprungprüfung vom Speichern des neuen Wertes. |
| 117 | `self.last_valid_distance_m = distance_m` | Speichert den neu berechneten Abstand als letzten gültigen Abstand. |
| 118 | `self.last_valid_distance_time = rospy.Time.now()` | Speichert den aktuellen Zeitpunkt für diesen Abstand. |
| 119 | `return distance_m` | Gibt den berechneten Abstand in Metern zurück. |
| 120 | Leerzeile | Trennt die Abstandsfunktion von der Hauptfunktion. |
| 121 | `def run(self):` | Definiert die Hauptfunktion, in der der Roboter dauerhaft gesteuert wird. |
| 122 | `rospy.loginfo("Baustein-Depth-Follower gestartet. Zielabstand: %.2f m", TARGET_DISTANCE_M)` | Gibt beim Start eine Info-Meldung mit dem Zielabstand aus. |
| 123 | Leerzeile | Trennt die Startmeldung von der Hauptschleife. |
| 124 | `while not rospy.is_shutdown():` | Startet eine Schleife, die läuft, bis ROS beendet wird. |
| 125 | `cmd = Twist()` | Erstellt eine neue Bewegungsnachricht für diesen Schleifendurchlauf. |
| 126 | Leerzeile | Trennt die neue Bewegungsnachricht von der ersten Prüfung. |
| 127 | `if self.grasp_requested:` | Prüft, ob das Greifsignal bereits gesendet wurde. |
| 128 | `self.stop_robot()` | Stoppt den Roboter, sobald der Greifvorgang angefordert wurde. |
| 129 | `self.rate.sleep()` | Wartet kurz, damit die Schleife bei ungefähr 10 Durchläufen pro Sekunde bleibt. |
| 130 | `continue` | Springt direkt zum nächsten Schleifendurchlauf. |
| 131 | Leerzeile | Trennt die Greifprüfung von der Erkennungsprüfung. |
| 132 | `if not self.detected or self.center_x is None:` | Prüft, ob kein Baustein erkannt wurde oder keine x-Position vorhanden ist. |
| 133 | `self.reset_grasp_confirmation()` | Bricht eine mögliche Greifbestätigung ab, weil die Erkennung nicht sicher ist. |
| 134 | `self.stop_robot()` | Stoppt den Roboter. |
| 135 | `self.rate.sleep()` | Wartet kurz bis zum nächsten Schleifendurchlauf. |
| 136 | `continue` | Überspringt den restlichen Code in diesem Durchlauf. |
| 137 | Leerzeile | Trennt die Erkennungsprüfung von der Abstandsmessung. |
| 138 | `distance_m = self.get_depth_at_baustein()` | Berechnet den Abstand zum Baustein aus dem Tiefenbild. |
| 139 | `if distance_m is None:` | Prüft, ob kein gültiger Abstand berechnet werden konnte. |
| 140 | `self.reset_grasp_confirmation()` | Bricht die Greifbestätigung ab, weil der Abstand fehlt. |
| 141 | `rospy.logwarn_throttle(2.0, "Kein gueltiger Depth-Abstand am Baustein.")` | Gibt höchstens alle 2 Sekunden eine Warnung aus, dass kein gültiger Abstand vorhanden ist. |
| 142 | `self.stop_robot()` | Stoppt den Roboter aus Sicherheitsgründen. |
| 143 | `self.rate.sleep()` | Wartet kurz. |
| 144 | `continue` | Springt zum nächsten Schleifendurchlauf. |
| 145 | Leerzeile | Trennt die Abstandskontrolle von der Ausrichtung. |
| 146 | `error_x = self.center_x - IMAGE_CENTER_X` | Berechnet, wie weit der Baustein links oder rechts von der Bildmitte liegt. |
| 147 | Leerzeile | Trennt die Berechnung von der Statusmeldung. |
| 148 | `rospy.loginfo_throttle(` | Beginnt eine gedrosselte Info-Meldung. Gedrosselt bedeutet: Sie wird nicht zu oft ausgegeben. |
| 149 | `1.0,` | Die Meldung darf höchstens einmal pro Sekunde erscheinen. |
| 150 | `"Baustein: x=%.0f px, y=%.0f px, Abstand=%.2f m",` | Text der Meldung. Er zeigt x-Position, y-Position und Abstand. |
| 151 | `self.center_x,` | Übergibt die x-Position für die Meldung. |
| 152 | `self.center_y,` | Übergibt die y-Position für die Meldung. |
| 153 | `distance_m,` | Übergibt den gemessenen Abstand für die Meldung. |
| 154 | `)` | Beendet den Aufruf von `rospy.loginfo_throttle`. |
| 155 | Leerzeile | Trennt die Statusmeldung von der unteren Bildrandprüfung. |
| 156 | `if self.center_y is not None and self.center_y >= BOTTOM_STOP_Y:` | Prüft, ob der Baustein sehr weit unten im Bild liegt. Das kann bedeuten, dass er sehr nah am Roboter ist. |
| 157 | `self.reset_grasp_confirmation()` | Bricht die Greifbestätigung ab. |
| 158 | `rospy.loginfo_throttle(` | Beginnt eine Info-Meldung, die nicht zu oft ausgegeben wird. |
| 159 | `2.0,` | Diese Meldung erscheint höchstens alle 2 Sekunden. |
| 160 | `"Baustein ist am unteren Bildrand. Stoppe bei %.2f m.",` | Meldung: Der Baustein ist unten im Bild, deshalb wird gestoppt. |
| 161 | `distance_m,` | Übergibt den aktuellen Abstand für die Meldung. |
| 162 | `)` | Beendet den Log-Aufruf. |
| 163 | `self.stop_robot()` | Stoppt den Roboter. |
| 164 | `self.rate.sleep()` | Wartet kurz. |
| 165 | `continue` | Springt zum nächsten Schleifendurchlauf. |
| 166 | Leerzeile | Trennt die Sicherheitsprüfung von der Toleranz-Auswahl. |
| 167 | `active_center_tolerance = (` | Beginnt die Berechnung der aktuell verwendeten Mittentoleranz. |
| 168 | `CONFIRM_CENTER_TOLERANCE` | Nutzt die größere Toleranz, wenn gerade eine Greifbestätigung läuft. |
| 169 | `if self.grasp_candidate_since is not None` | Bedingung: Eine Greifbestätigung läuft, wenn dieser Wert nicht `None` ist. |
| 170 | `else CENTER_TOLERANCE` | Sonst wird die normale kleinere Toleranz verwendet. |
| 171 | `)` | Beendet die Berechnung der aktiven Toleranz. |
| 172 | Leerzeile | Trennt die Toleranz-Auswahl von der Bewegungsentscheidung. |
| 173 | `if abs(error_x) > active_center_tolerance:` | Prüft, ob der Baustein zu weit links oder rechts von der Bildmitte ist. |
| 174 | `self.reset_grasp_confirmation()` | Bricht die Greifbestätigung ab, weil der Baustein nicht mehr mittig genug ist. |
| 175 | `cmd.angular.z = ANGULAR_SPEED if error_x < 0 else -ANGULAR_SPEED` | Setzt die Drehrichtung. Ist der Baustein links, wird positiv gedreht, sonst negativ. |
| 176 | `cmd.linear.x = 0.0` | Setzt die Vorwärtsgeschwindigkeit auf 0. Während der Ausrichtung fährt der Roboter nicht vorwärts. |
| 177 | `else:` | Dieser Block läuft, wenn der Baustein mittig genug ist. |
| 178 | `if STOP_DISTANCE_MIN_M <= distance_m <= STOP_DISTANCE_MAX_M:` | Prüft, ob der Abstand im Greiffenster liegt. |
| 179 | `self.stop_robot()` | Stoppt den Roboter im passenden Greifabstand. |
| 180 | Leerzeile | Trennt das Stoppen von der Zeitmessung. |
| 181 | `now = rospy.Time.now()` | Speichert die aktuelle ROS-Zeit. |
| 182 | `if self.grasp_candidate_since is None:` | Prüft, ob die Greifbestätigung gerade erst beginnen soll. |
| 183 | `self.grasp_candidate_since = now` | Speichert den Startzeitpunkt der Greifbestätigung. |
| 184 | `rospy.loginfo(` | Beginnt eine Info-Meldung. |
| 185 | `"Greiffenster erreicht bei %.2f m. Warte %.1f s zur Bestaetigung.",` | Meldung: Der passende Abstand wurde erreicht und es wird zur Bestätigung gewartet. |
| 186 | `distance_m,` | Übergibt den aktuellen Abstand. |
| 187 | `GRASP_CONFIRMATION_S,` | Übergibt die benötigte Bestätigungszeit. |
| 188 | `)` | Beendet die Info-Meldung. |
| 189 | Leerzeile | Trennt den Start der Bestätigung von der Zeitberechnung. |
| 190 | `confirmation_age = (now - self.grasp_candidate_since).to_sec()` | Berechnet, wie lange der Roboter schon im Greiffenster steht. |
| 191 | `rospy.loginfo_throttle(` | Beginnt eine gedrosselte Info-Meldung. |
| 192 | `1.0,` | Die Meldung erscheint höchstens einmal pro Sekunde. |
| 193 | `"Greifabstand wird bestaetigt: %.1f/%.1f s",` | Meldung: Zeigt, wie viele Sekunden schon bestätigt wurden. |
| 194 | `confirmation_age,` | Übergibt die bisherige Bestätigungszeit. |
| 195 | `GRASP_CONFIRMATION_S,` | Übergibt die benötigte Gesamtzeit. |
| 196 | `)` | Beendet die Log-Meldung. |
| 197 | Leerzeile | Trennt die Anzeige von der Entscheidung, ob gegriffen werden darf. |
| 198 | `if confirmation_age >= GRASP_CONFIRMATION_S and not self.grasp_requested:` | Prüft, ob lange genug bestätigt wurde und noch kein Greifsignal gesendet wurde. |
| 199 | `self.grasp_pub.publish(Bool(data=True))` | Sendet `True` auf `/greif_start`. Das ist das Startsignal für den Greifvorgang. |
| 200 | `self.grasp_requested = True` | Merkt sich, dass das Greifsignal gesendet wurde. |
| 201 | `rospy.loginfo("Greifsignal auf /greif_start gesendet.")` | Gibt aus, dass das Greifsignal gesendet wurde. |
| 202 | Leerzeile | Trennt die Greifentscheidung vom Schleifenende. |
| 203 | `self.rate.sleep()` | Wartet kurz. |
| 204 | `continue` | Springt zum nächsten Schleifendurchlauf, ohne weitere Fahrbefehle zu berechnen. |
| 205 | Leerzeile | Trennt das Greiffenster vom Fall "noch zu weit weg". |
| 206 | `if distance_m > STOP_DISTANCE_MAX_M:` | Prüft, ob der Baustein noch weiter entfernt ist als das Greiffenster. |
| 207 | `self.reset_grasp_confirmation()` | Setzt eine mögliche Greifbestätigung zurück, weil der Abstand noch nicht passt. |
| 208 | `cmd.angular.z = 0.0` | Setzt die Drehgeschwindigkeit auf 0. Der Roboter fährt geradeaus. |
| 209 | `cmd.linear.x = min(` | Beginnt die Berechnung der Vorwärtsgeschwindigkeit mit einer oberen Grenze. |
| 210 | `MAX_LINEAR_SPEED,` | Die Geschwindigkeit darf nie größer als `MAX_LINEAR_SPEED` werden. |
| 211 | `max(MIN_LINEAR_SPEED, (distance_m - STOP_DISTANCE_MAX_M) * 0.25),` | Berechnet eine Geschwindigkeit abhängig vom Abstand und stellt sicher, dass sie nicht kleiner als `MIN_LINEAR_SPEED` wird. |
| 212 | `)` | Beendet die Berechnung der Vorwärtsgeschwindigkeit. |
| 213 | `else:` | Dieser Block läuft, wenn der Baustein näher ist als die untere Grenze des Greiffensters. |
| 214 | `self.stop_robot()` | Stoppt den Roboter, weil der Baustein zu nah ist. |
| 215 | `rospy.logwarn_throttle(` | Beginnt eine Warnmeldung, die nicht zu oft ausgegeben wird. |
| 216 | `2.0,` | Die Warnung erscheint höchstens alle 2 Sekunden. |
| 217 | `"Baustein ist naeher als das Greiffenster: %.2f m < %.2f m.",` | Meldung: Der Baustein ist zu nah am Roboter. |
| 218 | `distance_m,` | Übergibt den aktuellen Abstand. |
| 219 | `STOP_DISTANCE_MIN_M,` | Übergibt die untere Grenze des Greiffensters. |
| 220 | `)` | Beendet die Warnmeldung. |
| 221 | `self.rate.sleep()` | Wartet kurz. |
| 222 | `continue` | Springt zum nächsten Schleifendurchlauf. |
| 223 | Leerzeile | Trennt die Bewegungsentscheidung vom Senden des Fahrbefehls. |
| 224 | `self.cmd_pub.publish(cmd)` | Sendet den berechneten Fahrbefehl auf `/cmd_vel`. |
| 225 | `self.rate.sleep()` | Wartet kurz, damit die Schleife bei ungefähr 10 Durchläufen pro Sekunde bleibt. |
| 226 | Leerzeile | Trennt die Hauptschleife vom Startbereich der Datei. |
| 227 | Leerzeile | Macht den Startbereich optisch klarer. |
| 228 | `if __name__ == "__main__":` | Prüft, ob diese Datei direkt gestartet wurde. |
| 229 | `try:` | Startet einen geschützten Bereich für den Programmstart. |
| 230 | `BausteinDepthFollower().run()` | Erstellt den Follower und startet direkt die Hauptschleife. |
| 231 | `except rospy.ROSInterruptException:` | Fängt eine normale ROS-Unterbrechung ab, zum Beispiel beim Beenden des Programms. |
| 232 | `pass` | Macht in diesem Ausnahmefall nichts weiter. Das Programm beendet sich sauber. |

## Wie entscheidet der Roboter?

Der Roboter kombiniert zwei Informationen:

1. Wo ist der Baustein links/rechts im Bild?
2. Wie weit ist der Baustein entfernt?

Die horizontale Abweichung wird so berechnet:

```python
error_x = self.center_x - IMAGE_CENTER_X
```

| Fall | Bedeutung | Reaktion |
| --- | --- | --- |
| `error_x < 0` | Baustein ist links im Bild. | Roboter dreht sich in Richtung Baustein. |
| `error_x > 0` | Baustein ist rechts im Bild. | Roboter dreht sich in die andere Richtung. |
| `abs(error_x)` ist klein | Baustein ist ungefähr mittig. | Roboter darf den Abstand prüfen und vorwärts fahren. |

Danach wird der Abstand geprüft:

| Abstand | Bedeutung | Reaktion |
| --- | --- | --- |
| `distance_m > 0.63` | Baustein ist noch zu weit weg. | Roboter fährt langsam vorwärts. |
| `0.55 <= distance_m <= 0.63` | Baustein ist im Greiffenster. | Roboter stoppt und bestätigt 3 Sekunden lang. |
| `distance_m < 0.55` | Baustein ist zu nah. | Roboter stoppt. |
| Kein gültiger Abstand | Tiefenmessung ist unsicher. | Roboter stoppt. |

## Benutzte ROS-Topics

| Topic | Richtung | Nachrichtentyp | Bedeutung |
| --- | --- | --- | --- |
| `/baustein_detected` | Eingang | `std_msgs/Bool` | Sagt, ob ein Baustein erkannt wurde. |
| `/baustein_center` | Eingang | `geometry_msgs/Point` | Enthält die Position der Bausteinmitte im Farbbild. |
| `/camera/depth/image_raw` | Eingang | `sensor_msgs/Image` | Liefert das Tiefenbild der Kamera. |
| `/cmd_vel` | Ausgang | `geometry_msgs/Twist` | Sendet Fahrbefehle an den Roboter. |
| `/greif_start` | Ausgang | `std_msgs/Bool` | Sendet `True`, wenn der Greifvorgang starten soll. |

## Wichtige Einstellungen

```python
CENTER_TOLERANCE = 40.0
CONFIRM_CENTER_TOLERANCE = 70.0
STOP_DISTANCE_MIN_M = 0.55
STOP_DISTANCE_MAX_M = 0.63
GRASP_CONFIRMATION_S = 3.0
MAX_LINEAR_SPEED = 0.06
MIN_LINEAR_SPEED = 0.02
```

| Einstellung | Bedeutung |
| --- | --- |
| `CENTER_TOLERANCE` | Wie genau der Baustein horizontal mittig sein muss. |
| `CONFIRM_CENTER_TOLERANCE` | Größere Toleranz während der Greifbestätigung. |
| `STOP_DISTANCE_MIN_M` | Untere Grenze des erlaubten Greifabstands. |
| `STOP_DISTANCE_MAX_M` | Obere Grenze des erlaubten Greifabstands. |
| `GRASP_CONFIRMATION_S` | Wie lange der Abstand stabil passen muss, bevor gegriffen wird. |
| `MAX_LINEAR_SPEED` | Höchste Vorwärtsgeschwindigkeit. |
| `MIN_LINEAR_SPEED` | Niedrigste Vorwärtsgeschwindigkeit beim Annähern. |

## Merksatz

```text
Kein Baustein erkannt?
-> stoppen

Kein gültiger Abstand?
-> stoppen

Baustein nicht mittig?
-> drehen

Baustein mittig, aber zu weit weg?
-> langsam vorwärts fahren

Baustein im Greifabstand?
-> stoppen, 3 Sekunden bestätigen, Greifsignal senden

Baustein zu nah?
-> stoppen
```

## Wichtig zu wissen

- Dieser Code verwendet `rospy` und ist damit ROS1-Code.
- Der Erkennungsknoten muss `/baustein_detected` und `/baustein_center` veröffentlichen.
- Die Tiefenkamera muss Daten auf `/camera/depth/image_raw` liefern.
- Der Abstand wird nicht aus einem einzelnen Pixel gelesen, sondern aus einem Fenster um die Bausteinmitte.
- Der Median wird verwendet, damit einzelne falsche Tiefenwerte nicht sofort stören.
- Das Greifsignal wird erst gesendet, wenn der Baustein 3 Sekunden lang im passenden Abstand bestätigt wurde.
- Nach dem Greifsignal bleibt der Roboter stehen.
