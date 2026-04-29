# Erklärung zu `yolo_baustein_follow.py`

Diese Datei startet einen ROS-Knoten, der den LIMO-Roboter zu einem erkannten Baustein ausrichtet und langsam darauf zufahren lässt.

Der Code erkennt den Baustein nicht selbst. Er benutzt die Ergebnisse von `yolo_baustein_publisher.py`:

1. `/baustein_detected` sagt, ob ein Baustein erkannt wurde.
2. `/baustein_center` sagt, wo die Mitte des Bausteins im Kamerabild liegt.

Kurz gesagt:

1. ROS wird gestartet.
2. Der Knoten hört auf die Baustein-Erkennungs-Topics.
3. Wenn kein Baustein erkannt wird, bleibt der Roboter stehen.
4. Wenn der Baustein links oder rechts im Bild liegt, dreht sich der Roboter.
5. Wenn der Baustein ungefähr in der Bildmitte liegt, fährt der Roboter langsam vorwärts.
6. Die Bewegungsbefehle werden auf `/cmd_vel` veröffentlicht.

## Wichtige Begriffe

| Begriff | Bedeutung |
| --- | --- |
| ROS-Knoten | Ein einzelnes Programm in ROS. Dieser Knoten steuert das Folgen des Bausteins. |
| `rospy` | Die Python-Bibliothek für ROS1. Sie wird benutzt, um Publisher, Subscriber und Schleifen zu erstellen. |
| Topic | Ein Kanal in ROS, über den Nachrichten gesendet oder empfangen werden. |
| Subscriber | Hört auf ein ROS-Topic und reagiert auf neue Nachrichten. |
| Publisher | Sendet Nachrichten auf ein ROS-Topic. |
| Callback | Eine Funktion, die automatisch aufgerufen wird, wenn eine neue Nachricht ankommt. |
| `/cmd_vel` | Das ROS-Topic für Fahrbefehle. Darüber bekommt der Roboter seine Geschwindigkeit. |
| `Twist` | Nachrichtentyp für Bewegung. Er enthält lineare Geschwindigkeit und Drehgeschwindigkeit. |
| `Point` | Nachrichtentyp mit `x`, `y` und `z`. Hier wird vor allem `x` für die Bildposition benutzt. |
| Bildmitte | Die x-Position in der Mitte des Kamerabildes. Bei 640 Pixel Breite ist das `320`. |
| Toleranzbereich | Ein Bereich um die Bildmitte, in dem der Baustein als "mittig genug" gilt. |

## Vollständiger Code

```python
#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist, Point
from std_msgs.msg import Bool

IMAGE_WIDTH = 640.0
IMAGE_CENTER_X = IMAGE_WIDTH / 2.0

# Toleranzbereich um die Bildmitte
CENTER_TOLERANCE = 40.0

# Drehgeschwindigkeit
ANGULAR_SPEED = 0.25

# Vorwärtsgeschwindigkeit
LINEAR_SPEED = 0.05

class BausteinFollower:
    def __init__(self):
        rospy.init_node("baustein_follower", anonymous=True)

        self.detected = False
        self.center_x = None

        self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)

        rospy.Subscriber("/baustein_detected", Bool, self.detected_callback)
        rospy.Subscriber("/baustein_center", Point, self.center_callback)

        self.rate = rospy.Rate(10)

    def detected_callback(self, msg):
        self.detected = msg.data

    def center_callback(self, msg):
        self.center_x = msg.x

    def stop_robot(self):
        cmd = Twist()
        self.cmd_pub.publish(cmd)

    def run(self):
        rospy.loginfo("Baustein-Follower gestartet.")
        while not rospy.is_shutdown():
            cmd = Twist()

            if not self.detected or self.center_x is None:
                # nichts erkannt -> stehen bleiben
                self.stop_robot()
                self.rate.sleep()
                continue

            error_x = self.center_x - IMAGE_CENTER_X

            # Erst nur ausrichten
            if abs(error_x) > CENTER_TOLERANCE:
                if error_x < 0:
                    cmd.angular.z = ANGULAR_SPEED
                else:
                    cmd.angular.z = -ANGULAR_SPEED
                cmd.linear.x = 0.0
            else:
                # mittig -> langsam vorfahren
                cmd.angular.z = 0.0
                cmd.linear.x = LINEAR_SPEED

            self.cmd_pub.publish(cmd)
            self.rate.sleep()

if __name__ == "__main__":
    follower = BausteinFollower()
    follower.run()
```

## Erklärung Zeile für Zeile

| Zeile | Code | Erklärung |
| --- | --- | --- |
| 1 | `#!/usr/bin/env python3` | Diese Zeile sagt dem System, dass die Datei mit Python 3 ausgeführt werden soll. |
| 2 | `import rospy` | Importiert `rospy`, die Python-Bibliothek für ROS1. Damit kann der Code mit ROS kommunizieren. |
| 3 | `from geometry_msgs.msg import Twist, Point` | Importiert zwei Nachrichtentypen. `Twist` wird für Fahrbefehle benutzt, `Point` für die Position der Bausteinmitte. |
| 4 | `from std_msgs.msg import Bool` | Importiert den Nachrichtentyp `Bool`. Damit wird empfangen, ob ein Baustein erkannt wurde. |
| 5 | Leerzeile | Macht den Code übersichtlicher. |
| 6 | `IMAGE_WIDTH = 640.0` | Speichert die Breite des Kamerabildes. Hier wird angenommen, dass das Bild 640 Pixel breit ist. |
| 7 | `IMAGE_CENTER_X = IMAGE_WIDTH / 2.0` | Berechnet die x-Koordinate der Bildmitte. Bei 640 Pixeln Breite ist die Mitte bei `320`. |
| 8 | Leerzeile | Trennt die Bildmitte vom nächsten Einstellwert. |
| 9 | `# Toleranzbereich um die Bildmitte` | Kommentar: Der nächste Wert beschreibt, wie genau der Baustein in der Mitte sein muss. |
| 10 | `CENTER_TOLERANCE = 40.0` | Legt den Toleranzbereich fest. Wenn der Baustein höchstens 40 Pixel links oder rechts von der Mitte liegt, gilt er als mittig. |
| 11 | Leerzeile | Trennt den Toleranzwert von der Drehgeschwindigkeit. |
| 12 | `# Drehgeschwindigkeit` | Kommentar: Der nächste Wert bestimmt, wie schnell sich der Roboter dreht. |
| 13 | `ANGULAR_SPEED = 0.25` | Speichert die Drehgeschwindigkeit. Diese wird später in `cmd.angular.z` eingetragen. |
| 14 | Leerzeile | Trennt die Drehgeschwindigkeit von der Vorwärtsgeschwindigkeit. |
| 15 | `# Vorwärtsgeschwindigkeit` | Kommentar: Der nächste Wert bestimmt, wie schnell der Roboter nach vorne fährt. |
| 16 | `LINEAR_SPEED = 0.05` | Speichert die Vorwärtsgeschwindigkeit. Der Wert ist klein, damit der Roboter langsam auf den Baustein zufährt. |
| 17 | Leerzeile | Trennt die Einstellungen von der Klasse. |
| 18 | `class BausteinFollower:` | Definiert die Klasse `BausteinFollower`. In dieser Klasse steckt die komplette Logik für das Folgen des Bausteins. |
| 19 | `def __init__(self):` | Definiert den Konstruktor. Diese Methode wird automatisch ausgeführt, wenn ein `BausteinFollower` erstellt wird. |
| 20 | `rospy.init_node("baustein_follower", anonymous=True)` | Startet den ROS-Knoten mit dem Namen `baustein_follower`. `anonymous=True` erlaubt ROS, bei Bedarf eine eindeutige Nummer an den Namen anzuhängen. |
| 21 | Leerzeile | Trennt die Knotenerstellung von den internen Variablen. |
| 22 | `self.detected = False` | Speichert, ob aktuell ein Baustein erkannt wurde. Am Anfang steht der Wert auf `False`. |
| 23 | `self.center_x = None` | Speichert später die x-Position der Bausteinmitte. `None` bedeutet: Es wurde noch keine Position empfangen. |
| 24 | Leerzeile | Trennt die internen Variablen vom Publisher. |
| 25 | `self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)` | Erstellt einen Publisher für `/cmd_vel`. Über dieses Topic werden Fahrbefehle an den Roboter gesendet. |
| 26 | Leerzeile | Trennt den Publisher von den Subscribern. |
| 27 | `rospy.Subscriber("/baustein_detected", Bool, self.detected_callback)` | Erstellt einen Subscriber für `/baustein_detected`. Wenn eine Nachricht ankommt, wird `detected_callback` aufgerufen. |
| 28 | `rospy.Subscriber("/baustein_center", Point, self.center_callback)` | Erstellt einen Subscriber für `/baustein_center`. Wenn eine neue Bausteinmitte ankommt, wird `center_callback` aufgerufen. |
| 29 | Leerzeile | Trennt die Subscriber von der Schleifenrate. |
| 30 | `self.rate = rospy.Rate(10)` | Legt fest, dass die Hauptschleife ungefähr 10-mal pro Sekunde laufen soll. |
| 31 | Leerzeile | Trennt den Konstruktor von der ersten Callback-Methode. |
| 32 | `def detected_callback(self, msg):` | Definiert die Callback-Methode für `/baustein_detected`. |
| 33 | `self.detected = msg.data` | Speichert den empfangenen Wert. `True` bedeutet: Baustein erkannt. `False` bedeutet: kein Baustein erkannt. |
| 34 | Leerzeile | Trennt die erste Callback-Methode von der zweiten. |
| 35 | `def center_callback(self, msg):` | Definiert die Callback-Methode für `/baustein_center`. |
| 36 | `self.center_x = msg.x` | Speichert nur die x-Koordinate der Bausteinmitte. Für Links-Rechts-Ausrichtung reicht dieser Wert aus. |
| 37 | Leerzeile | Trennt die Callback-Methode von der Stopp-Methode. |
| 38 | `def stop_robot(self):` | Definiert eine Methode, die den Roboter stoppt. |
| 39 | `cmd = Twist()` | Erstellt eine neue leere `Twist`-Nachricht. Alle Geschwindigkeiten sind dadurch automatisch `0.0`. |
| 40 | `self.cmd_pub.publish(cmd)` | Sendet die leere `Twist`-Nachricht auf `/cmd_vel`. Dadurch soll der Roboter stehen bleiben. |
| 41 | Leerzeile | Trennt die Stopp-Methode von der Hauptschleife. |
| 42 | `def run(self):` | Definiert die Hauptmethode. Sie enthält die Schleife, die den Roboter immer wieder steuert. |
| 43 | `rospy.loginfo("Baustein-Follower gestartet.")` | Gibt im Terminal aus, dass der Baustein-Follower gestartet wurde. |
| 44 | `while not rospy.is_shutdown():` | Startet eine Schleife, die so lange läuft, bis ROS beendet wird. |
| 45 | `cmd = Twist()` | Erstellt für diesen Schleifendurchlauf eine neue Bewegungsnachricht. |
| 46 | Leerzeile | Trennt die neue Bewegungsnachricht von der Prüfung der Erkennung. |
| 47 | `if not self.detected or self.center_x is None:` | Prüft, ob kein Baustein erkannt wurde oder noch keine x-Position vorhanden ist. |
| 48 | `# nichts erkannt -> stehen bleiben` | Kommentar: Wenn keine gültige Erkennung vorhanden ist, soll der Roboter nicht fahren. |
| 49 | `self.stop_robot()` | Ruft die Stopp-Methode auf und sendet eine Geschwindigkeit von `0.0`. |
| 50 | `self.rate.sleep()` | Wartet kurz, damit die Schleife ungefähr bei 10 Durchläufen pro Sekunde bleibt. |
| 51 | `continue` | Springt direkt zum nächsten Schleifendurchlauf. Der restliche Code wird in diesem Durchlauf nicht ausgeführt. |
| 52 | Leerzeile | Trennt den Sicherheitsstopp von der Berechnung der Abweichung. |
| 53 | `error_x = self.center_x - IMAGE_CENTER_X` | Berechnet, wie weit der Baustein von der Bildmitte entfernt ist. Ein negativer Wert bedeutet links, ein positiver Wert bedeutet rechts. |
| 54 | Leerzeile | Trennt die Abweichung von der Entscheidung. |
| 55 | `# Erst nur ausrichten` | Kommentar: Der Roboter soll sich zuerst zum Baustein drehen, bevor er vorwärts fährt. |
| 56 | `if abs(error_x) > CENTER_TOLERANCE:` | Prüft, ob der Baustein zu weit links oder rechts von der Bildmitte liegt. `abs` macht aus der Abweichung einen positiven Abstand. |
| 57 | `if error_x < 0:` | Prüft, ob der Baustein links von der Bildmitte liegt. |
| 58 | `cmd.angular.z = ANGULAR_SPEED` | Setzt eine positive Drehgeschwindigkeit. Der Roboter dreht sich in eine Richtung, um den Baustein in die Mitte zu bringen. |
| 59 | `else:` | Wird ausgeführt, wenn der Baustein nicht links liegt, sondern rechts von der Bildmitte. |
| 60 | `cmd.angular.z = -ANGULAR_SPEED` | Setzt eine negative Drehgeschwindigkeit. Der Roboter dreht sich in die andere Richtung. |
| 61 | `cmd.linear.x = 0.0` | Setzt die Vorwärtsgeschwindigkeit auf `0.0`. Während der Ausrichtung fährt der Roboter nicht vorwärts. |
| 62 | `else:` | Wird ausgeführt, wenn der Baustein innerhalb des Toleranzbereichs liegt. |
| 63 | `# mittig -> langsam vorfahren` | Kommentar: Wenn der Baustein mittig genug ist, darf der Roboter langsam vorwärts fahren. |
| 64 | `cmd.angular.z = 0.0` | Setzt die Drehgeschwindigkeit auf `0.0`. Der Roboter dreht sich jetzt nicht. |
| 65 | `cmd.linear.x = LINEAR_SPEED` | Setzt die Vorwärtsgeschwindigkeit. Der Roboter fährt langsam geradeaus. |
| 66 | Leerzeile | Trennt die Entscheidung vom Senden des Fahrbefehls. |
| 67 | `self.cmd_pub.publish(cmd)` | Veröffentlicht den berechneten Fahrbefehl auf `/cmd_vel`. |
| 68 | `self.rate.sleep()` | Wartet kurz, damit die Schleife mit der eingestellten Rate weiterläuft. |
| 69 | Leerzeile | Trennt die Klasse vom Startblock. |
| 70 | `if __name__ == "__main__":` | Prüft, ob diese Datei direkt gestartet wurde. Nur dann wird der folgende Code ausgeführt. |
| 71 | `follower = BausteinFollower()` | Erstellt ein Objekt der Klasse `BausteinFollower`. Dadurch werden ROS-Knoten, Publisher und Subscriber eingerichtet. |
| 72 | `follower.run()` | Startet die Hauptschleife. Ab jetzt reagiert der Roboter auf die Baustein-Position. |

## Ablauf des Programms

```text
Programm starten
        ↓
ROS-Knoten baustein_follower erstellen
        ↓
Publisher für /cmd_vel erstellen
        ↓
Auf /baustein_detected hören
        ↓
Auf /baustein_center hören
        ↓
Prüfen: wurde ein Baustein erkannt?
        ↓
Nein → Roboter stoppen
        ↓
Ja → Abstand zur Bildmitte berechnen
        ↓
Baustein links oder rechts?
        ↓
Roboter dreht sich zur Mitte
        ↓
Baustein mittig genug?
        ↓
Roboter fährt langsam vorwärts
```

## Welche Topics werden benutzt?

| Topic | Richtung | Nachrichtentyp | Bedeutung |
| --- | --- | --- | --- |
| `/baustein_detected` | Eingang | `std_msgs/Bool` | Sagt, ob aktuell ein Baustein erkannt wurde. |
| `/baustein_center` | Eingang | `geometry_msgs/Point` | Enthält die Bildposition der Bausteinmitte. Hier wird nur `x` verwendet. |
| `/cmd_vel` | Ausgang | `geometry_msgs/Twist` | Sendet Fahrbefehle an den Roboter. |

## Wie entscheidet der Roboter?

Der Roboter vergleicht die x-Position des Bausteins mit der Bildmitte:

```python
error_x = self.center_x - IMAGE_CENTER_X
```

| Fall | Bedeutung | Reaktion |
| --- | --- | --- |
| `error_x < 0` | Der Baustein ist links im Bild. | Der Roboter dreht sich in Richtung Baustein. |
| `error_x > 0` | Der Baustein ist rechts im Bild. | Der Roboter dreht sich in die andere Richtung. |
| `abs(error_x) <= CENTER_TOLERANCE` | Der Baustein ist ungefähr mittig. | Der Roboter fährt langsam vorwärts. |
| Kein Baustein erkannt | Es gibt keine sichere Zielposition. | Der Roboter bleibt stehen. |

## Wo werden die wichtigsten Einstellungen geändert?

Die wichtigsten Einstellungen stehen oben in der Datei:

```python
IMAGE_WIDTH = 640.0
CENTER_TOLERANCE = 40.0
ANGULAR_SPEED = 0.25
LINEAR_SPEED = 0.05
```

| Einstellung | Bedeutung |
| --- | --- |
| `IMAGE_WIDTH` | Breite des Kamerabildes in Pixeln. Muss zur Kameraauflösung passen. |
| `CENTER_TOLERANCE` | Bereich um die Bildmitte. Größerer Wert bedeutet: Der Roboter akzeptiert mehr Abweichung. |
| `ANGULAR_SPEED` | Drehgeschwindigkeit. Größerer Wert bedeutet: Der Roboter dreht schneller. |
| `LINEAR_SPEED` | Vorwärtsgeschwindigkeit. Größerer Wert bedeutet: Der Roboter fährt schneller auf den Baustein zu. |

## Wichtig zu wissen

- Dieser Code benutzt `rospy` und ist damit im ROS1-Stil geschrieben.
- `yolo_baustein_publisher.py` muss laufen, damit `/baustein_detected` und `/baustein_center` Daten liefern.
- Der Roboter fährt nur vorwärts, wenn der Baustein ungefähr in der Bildmitte liegt.
- Wenn kein Baustein erkannt wird, wird immer ein Stopp-Befehl gesendet.
- Der Code nutzt keine Tiefeninformation. Er weiß also nicht, wie weit der Baustein entfernt ist.
- Ohne Abstandskontrolle fährt der Roboter weiter vorwärts, solange der Baustein mittig erkannt wird.
- Die Richtung der Drehung kann je nach Roboter-Setup anders wirken. Wenn sich der Roboter falsch herum dreht, müssen die Vorzeichen bei `cmd.angular.z` getauscht werden.
