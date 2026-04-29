# Erklärung zu `yolo_baustein_follow.py`

Diese Datei steuert den LIMO-Roboter so, dass er einem erkannten Baustein folgt.

Wichtig: Diese Datei erkennt den Baustein nicht selbst. Sie bekommt die Erkennungsdaten von einem anderen ROS-Knoten, zum Beispiel von `yolo_baustein_publisher.py`.

Der Ablauf ist:

1. Der Knoten startet in ROS.
2. Er hört auf zwei Topics:
   - `/baustein_detected`: Wurde ein Baustein erkannt?
   - `/baustein_center`: Wo liegt die Mitte des Bausteins im Kamerabild?
3. Wenn kein Baustein erkannt wird, bleibt der Roboter stehen.
4. Wenn der Baustein links oder rechts im Bild ist, dreht sich der Roboter.
5. Wenn der Baustein ungefähr in der Bildmitte ist, fährt der Roboter langsam vorwärts.

## Wichtige Begriffe

| Begriff | Einfache Erklärung |
| --- | --- |
| ROS-Knoten | Ein einzelnes Programm in ROS. Hier ist es das Programm, das den Roboter zum Baustein ausrichtet. |
| Topic | Ein Kommunikationskanal in ROS. Programme senden und empfangen darüber Nachrichten. |
| Publisher | Sendet Nachrichten auf ein Topic. |
| Subscriber | Empfängt Nachrichten von einem Topic. |
| Callback | Eine Funktion, die automatisch ausgeführt wird, wenn eine neue Nachricht ankommt. |
| `Twist` | ROS-Nachricht für Bewegungsbefehle. Sie enthält Vorwärtsgeschwindigkeit und Drehgeschwindigkeit. |
| `Point` | ROS-Nachricht mit `x`, `y` und `z`. Hier wird nur `x` für die horizontale Position im Bild benutzt. |
| `Bool` | ROS-Nachricht für `True` oder `False`. |
| `/cmd_vel` | Topic, über das der Roboter Fahrbefehle bekommt. |

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

| Zeile | Code | Anfängerfreundliche Erklärung |
| --- | --- | --- |
| 1 | `#!/usr/bin/env python3` | Diese Zeile sagt dem Betriebssystem: Starte diese Datei mit Python 3. Das ist nützlich, wenn die Datei direkt ausgeführt wird. |
| 2 | `import rospy` | Importiert `rospy`. Das ist die Python-Bibliothek, mit der Python-Programme mit ROS kommunizieren können. |
| 3 | `from geometry_msgs.msg import Twist, Point` | Importiert zwei ROS-Nachrichtentypen. `Twist` wird für Fahrbefehle verwendet. `Point` wird hier für die Position des Bausteins im Bild verwendet. |
| 4 | `from std_msgs.msg import Bool` | Importiert den Nachrichtentyp `Bool`. Damit kann ein Wert wie `True` oder `False` übertragen werden. |
| 5 | Leerzeile | Die Leerzeile macht den Code besser lesbar. |
| 6 | `IMAGE_WIDTH = 640.0` | Speichert die angenommene Breite des Kamerabildes. Hier wird angenommen: Das Bild ist 640 Pixel breit. |
| 7 | `IMAGE_CENTER_X = IMAGE_WIDTH / 2.0` | Berechnet die x-Position der Bildmitte. Bei 640 Pixeln Breite ist die Mitte bei 320 Pixeln. |
| 8 | Leerzeile | Trennt die Bildwerte vom nächsten Einstellwert. |
| 9 | `# Toleranzbereich um die Bildmitte` | Ein Kommentar. Er erklärt, dass der nächste Wert den erlaubten Bereich um die Bildmitte beschreibt. |
| 10 | `CENTER_TOLERANCE = 40.0` | Legt fest, wie weit der Baustein von der Bildmitte entfernt sein darf und trotzdem noch als "mittig genug" gilt. Hier sind es 40 Pixel. |
| 11 | Leerzeile | Trennt die Toleranz von der Drehgeschwindigkeit. |
| 12 | `# Drehgeschwindigkeit` | Kommentar: Der nächste Wert bestimmt, wie schnell sich der Roboter drehen soll. |
| 13 | `ANGULAR_SPEED = 0.25` | Speichert die Drehgeschwindigkeit. Dieser Wert wird später für `cmd.angular.z` benutzt. |
| 14 | Leerzeile | Trennt die Drehgeschwindigkeit von der Vorwärtsgeschwindigkeit. |
| 15 | `# Vorwärtsgeschwindigkeit` | Kommentar: Der nächste Wert bestimmt, wie schnell der Roboter nach vorne fährt. |
| 16 | `LINEAR_SPEED = 0.05` | Speichert die Vorwärtsgeschwindigkeit. Der Wert ist bewusst klein, damit der Roboter langsam auf den Baustein zufährt. |
| 17 | Leerzeile | Trennt die Einstellungen von der Klasse. |
| 18 | `class BausteinFollower:` | Erstellt eine Klasse mit dem Namen `BausteinFollower`. Eine Klasse bündelt Daten und Funktionen, die zusammengehören. |
| 19 | `def __init__(self):` | Definiert den Konstruktor. Diese Funktion wird automatisch ausgeführt, wenn ein neues `BausteinFollower`-Objekt erstellt wird. |
| 20 | `rospy.init_node("baustein_follower", anonymous=True)` | Startet den ROS-Knoten mit dem Namen `baustein_follower`. `anonymous=True` erlaubt ROS, bei Bedarf eine eindeutige Nummer an den Namen anzuhängen. |
| 21 | Leerzeile | Trennt den Start des ROS-Knotens von den internen Variablen. |
| 22 | `self.detected = False` | Speichert, ob gerade ein Baustein erkannt wurde. Am Anfang steht der Wert auf `False`, also "nein". |
| 23 | `self.center_x = None` | Speichert später die x-Position der Bausteinmitte. `None` bedeutet: Es ist noch keine Position bekannt. |
| 24 | Leerzeile | Trennt die internen Variablen vom Publisher. |
| 25 | `self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)` | Erstellt einen Publisher für das Topic `/cmd_vel`. Über dieses Topic werden Bewegungsbefehle an den Roboter gesendet. |
| 26 | Leerzeile | Trennt den Publisher von den Subscribern. |
| 27 | `rospy.Subscriber("/baustein_detected", Bool, self.detected_callback)` | Erstellt einen Subscriber für `/baustein_detected`. Wenn dort eine neue Nachricht ankommt, wird `self.detected_callback` aufgerufen. |
| 28 | `rospy.Subscriber("/baustein_center", Point, self.center_callback)` | Erstellt einen Subscriber für `/baustein_center`. Wenn dort eine neue Position ankommt, wird `self.center_callback` aufgerufen. |
| 29 | Leerzeile | Trennt die Subscriber von der Schleifengeschwindigkeit. |
| 30 | `self.rate = rospy.Rate(10)` | Legt fest, dass die Hauptschleife ungefähr 10-mal pro Sekunde laufen soll. |
| 31 | Leerzeile | Trennt den Konstruktor von der ersten Callback-Funktion. |
| 32 | `def detected_callback(self, msg):` | Definiert die Funktion, die bei neuen Nachrichten auf `/baustein_detected` ausgeführt wird. |
| 33 | `self.detected = msg.data` | Speichert den empfangenen Wahrheitswert. `True` bedeutet: Baustein erkannt. `False` bedeutet: kein Baustein erkannt. |
| 34 | Leerzeile | Trennt die erste Callback-Funktion von der zweiten. |
| 35 | `def center_callback(self, msg):` | Definiert die Funktion, die bei neuen Nachrichten auf `/baustein_center` ausgeführt wird. |
| 36 | `self.center_x = msg.x` | Speichert nur die x-Koordinate der Bausteinmitte. Für links/rechts reicht dieser Wert aus. |
| 37 | Leerzeile | Trennt die Callback-Funktion von der Stopp-Funktion. |
| 38 | `def stop_robot(self):` | Definiert eine eigene Funktion, um den Roboter anzuhalten. |
| 39 | `cmd = Twist()` | Erstellt eine neue leere Bewegungsnachricht. Bei einer leeren `Twist`-Nachricht sind die Geschwindigkeiten standardmäßig 0. |
| 40 | `self.cmd_pub.publish(cmd)` | Sendet diese leere Bewegungsnachricht an `/cmd_vel`. Dadurch bekommt der Roboter den Befehl, stehen zu bleiben. |
| 41 | Leerzeile | Trennt die Stopp-Funktion von der Hauptfunktion. |
| 42 | `def run(self):` | Definiert die Hauptfunktion des Programms. Hier wird der Roboter dauerhaft gesteuert. |
| 43 | `rospy.loginfo("Baustein-Follower gestartet.")` | Gibt eine ROS-Info-Meldung aus. So sieht man im Terminal, dass der Follower gestartet ist. |
| 44 | `while not rospy.is_shutdown():` | Startet eine Schleife, die so lange läuft, bis ROS beendet wird. |
| 45 | `cmd = Twist()` | Erstellt für diesen Schleifendurchlauf eine neue Bewegungsnachricht. |
| 46 | Leerzeile | Trennt das Erstellen der Nachricht von der Sicherheitsprüfung. |
| 47 | `if not self.detected or self.center_x is None:` | Prüft zwei Fälle: Entweder wurde kein Baustein erkannt oder es gibt noch keine x-Position. In beiden Fällen darf der Roboter nicht losfahren. |
| 48 | `# nichts erkannt -> stehen bleiben` | Kommentar: Wenn keine sichere Erkennung vorhanden ist, soll der Roboter stehen bleiben. |
| 49 | `self.stop_robot()` | Ruft die Stopp-Funktion auf. Dadurch wird ein Stopp-Befehl auf `/cmd_vel` gesendet. |
| 50 | `self.rate.sleep()` | Wartet kurz, damit die Schleife bei ungefähr 10 Durchläufen pro Sekunde bleibt. |
| 51 | `continue` | Springt direkt zum nächsten Schleifendurchlauf. Alles darunter wird in diesem Durchlauf übersprungen. |
| 52 | Leerzeile | Trennt den Sicherheitsstopp von der Berechnung der Bildabweichung. |
| 53 | `error_x = self.center_x - IMAGE_CENTER_X` | Berechnet, wie weit der Baustein von der Bildmitte entfernt ist. Negativ bedeutet links von der Mitte. Positiv bedeutet rechts von der Mitte. |
| 54 | Leerzeile | Trennt die Berechnung von der Entscheidung. |
| 55 | `# Erst nur ausrichten` | Kommentar: Der Roboter soll sich zuerst zum Baustein ausrichten, bevor er vorwärts fährt. |
| 56 | `if abs(error_x) > CENTER_TOLERANCE:` | Prüft, ob der Baustein weiter als 40 Pixel von der Mitte entfernt ist. `abs()` macht aus negativen und positiven Werten einen positiven Abstand. |
| 57 | `if error_x < 0:` | Prüft, ob der Baustein links von der Bildmitte liegt. |
| 58 | `cmd.angular.z = ANGULAR_SPEED` | Setzt eine positive Drehgeschwindigkeit. Der Roboter dreht sich in eine Richtung, um den Baustein zur Bildmitte zu bringen. |
| 59 | `else:` | Dieser Block läuft, wenn `error_x` nicht kleiner als 0 ist. Dann liegt der Baustein rechts von der Bildmitte. |
| 60 | `cmd.angular.z = -ANGULAR_SPEED` | Setzt eine negative Drehgeschwindigkeit. Der Roboter dreht sich in die andere Richtung. |
| 61 | `cmd.linear.x = 0.0` | Setzt die Vorwärtsgeschwindigkeit auf 0. Während der Ausrichtung fährt der Roboter nicht nach vorne. |
| 62 | `else:` | Dieser Block läuft, wenn der Baustein innerhalb des Toleranzbereichs liegt, also ungefähr mittig ist. |
| 63 | `# mittig -> langsam vorfahren` | Kommentar: Wenn der Baustein mittig genug ist, darf der Roboter langsam vorwärts fahren. |
| 64 | `cmd.angular.z = 0.0` | Setzt die Drehgeschwindigkeit auf 0. Der Roboter dreht sich jetzt nicht. |
| 65 | `cmd.linear.x = LINEAR_SPEED` | Setzt die Vorwärtsgeschwindigkeit. Der Roboter fährt langsam geradeaus auf den Baustein zu. |
| 66 | Leerzeile | Trennt die Entscheidung vom Senden des Befehls. |
| 67 | `self.cmd_pub.publish(cmd)` | Sendet den berechneten Bewegungsbefehl an `/cmd_vel`. Erst hier bekommt der Roboter den aktuellen Fahrbefehl. |
| 68 | `self.rate.sleep()` | Wartet kurz, damit die Schleife kontrolliert weiterläuft und nicht unnötig schnell wird. |
| 69 | Leerzeile | Trennt die Klasse vom Startbereich der Datei. |
| 70 | `if __name__ == "__main__":` | Prüft, ob diese Datei direkt gestartet wurde. Nur dann wird der folgende Code ausgeführt. |
| 71 | `follower = BausteinFollower()` | Erstellt ein Objekt der Klasse `BausteinFollower`. Dadurch werden ROS-Knoten, Publisher und Subscriber eingerichtet. |
| 72 | `follower.run()` | Startet die Hauptschleife. Ab jetzt reagiert der Roboter dauerhaft auf die Baustein-Position. |

## Wie entscheidet der Roboter?

Der wichtigste Wert ist:

```python
error_x = self.center_x - IMAGE_CENTER_X
```

Beispiel mit `IMAGE_CENTER_X = 320`:

| `self.center_x` | Rechnung | Bedeutung | Reaktion |
| --- | --- | --- | --- |
| `200` | `200 - 320 = -120` | Baustein ist links im Bild. | Roboter dreht sich. |
| `450` | `450 - 320 = 130` | Baustein ist rechts im Bild. | Roboter dreht sich in die andere Richtung. |
| `330` | `330 - 320 = 10` | Baustein ist fast in der Mitte. | Roboter fährt langsam vorwärts. |

## Benutzte ROS-Topics

| Topic | Richtung | Nachrichtentyp | Bedeutung |
| --- | --- | --- | --- |
| `/baustein_detected` | Eingang | `std_msgs/Bool` | Sagt, ob ein Baustein erkannt wurde. |
| `/baustein_center` | Eingang | `geometry_msgs/Point` | Enthält die Position der Bausteinmitte im Kamerabild. Hier wird `x` verwendet. |
| `/cmd_vel` | Ausgang | `geometry_msgs/Twist` | Sendet Bewegungsbefehle an den Roboter. |

## Wichtige Einstellungen

Diese Werte stehen oben in der Datei und können angepasst werden:

```python
IMAGE_WIDTH = 640.0
CENTER_TOLERANCE = 40.0
ANGULAR_SPEED = 0.25
LINEAR_SPEED = 0.05
```

| Einstellung | Bedeutung |
| --- | --- |
| `IMAGE_WIDTH` | Breite des Kamerabildes in Pixeln. Muss zur Kameraauflösung passen. |
| `CENTER_TOLERANCE` | Erlaubter Bereich um die Bildmitte. Größerer Wert bedeutet: Der Roboter akzeptiert mehr Abweichung. |
| `ANGULAR_SPEED` | Drehgeschwindigkeit. Größerer Wert bedeutet: Der Roboter dreht schneller. |
| `LINEAR_SPEED` | Vorwärtsgeschwindigkeit. Größerer Wert bedeutet: Der Roboter fährt schneller nach vorne. |

## Merksatz

Der Code macht im Grunde immer nur diese Entscheidung:

```text
Kein Baustein erkannt?
-> stehen bleiben

Baustein links oder rechts?
-> drehen

Baustein ungefähr mittig?
-> langsam vorwärts fahren
```

## Wichtig zu wissen

- Der Code verwendet `rospy` und ist damit ROS1-Code.
- `yolo_baustein_publisher.py` oder ein ähnlicher Erkennungsknoten muss laufen, damit Daten auf `/baustein_detected` und `/baustein_center` ankommen.
- Der Roboter nutzt hier nur die horizontale Bildposition `x`.
- Der Code kennt keinen Abstand zum Baustein.
- Wenn der Baustein mittig erkannt wird, fährt der Roboter weiter vorwärts.
- Wenn der Roboter sich falsch herum dreht, müssen wahrscheinlich die Vorzeichen bei `cmd.angular.z` getauscht werden.
