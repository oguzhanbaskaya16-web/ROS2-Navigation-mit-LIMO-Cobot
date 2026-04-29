# Erklärung zu `pickplace_navigator.py`

Diese Datei startet einen ROS2-Knoten, der den LIMO-Roboter zu einem Zielpunkt fahren lässt und danach wieder zur ursprünglichen Startposition zurückschickt.

Der Name "PickPlace" bedeutet hier: Der Roboter fährt zu einem Ort, an dem später etwas aufgenommen oder abgelegt werden könnte. Die eigentliche Pick/Place-Aktion ist in diesem Code noch nicht eingebaut, sondern wird nur mit einer Log-Meldung simuliert.

Kurz gesagt:

1. ROS2 wird gestartet.
2. Der Roboter wartet auf seine aktuelle Position aus `/amcl_pose`.
3. Diese Startposition wird gespeichert.
4. Der Roboter fährt zu einem festen Zielpunkt.
5. Dort wird eine Pick/Place-Aktion simuliert.
6. Der Roboter fährt zurück zur gespeicherten Startposition.
7. Am Ende wird ROS2 sauber beendet.

## Wichtige Begriffe

| Begriff | Bedeutung |
| --- | --- |
| ROS2-Knoten | Ein einzelnes ROS2-Programm. Hier übernimmt der Knoten die Pick/Place-Navigation. |
| Nav2 | Das Navigationssystem von ROS2. Es plant den Weg und steuert den Roboter zum Ziel. |
| ActionClient | Ein ROS2-Werkzeug, um eine längere Aufgabe zu starten, zum Beispiel "fahre zu dieser Position". |
| `/amcl_pose` | Ein ROS2-Topic, auf dem die geschätzte Position des Roboters auf der Karte veröffentlicht wird. |
| AMCL | Die Lokalisierung von Nav2. Sie schätzt, wo der Roboter auf der Karte steht. |
| Pose | Eine Position mit Ausrichtung. Sie enthält also `x`, `y` und eine Richtung. |
| Quaternion | Eine mathematische Form, mit der ROS2 Drehungen speichert. |
| yaw | Die Blickrichtung des Roboters als einfacher Winkel. |

## Vollständiger Code

```python
import math

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus


class PickPlaceNavigator(Node):
    def __init__(self):
        super().__init__('pick_place_navigator')

        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        self.start_pose = None

        self.pose_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.amcl_callback,
            10
        )

        # Zielpunkt für "Pick" oder "Place"
        self.target_x = -0.49
        self.target_y = 0.00
        self.target_yaw = 0.0

    def amcl_callback(self, msg):
        if self.start_pose is None:
            self.start_pose = (
                msg.pose.pose.position.x,
                msg.pose.pose.position.y,
                self.get_yaw_from_quaternion(msg.pose.pose.orientation)
            )
            self.get_logger().info(
                f'Startposition gespeichert: '
                f'x={self.start_pose[0]:.2f}, '
                f'y={self.start_pose[1]:.2f}, '
                f'yaw={self.start_pose[2]:.2f}'
            )

    def get_yaw_from_quaternion(self, q):
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        return math.atan2(siny_cosp, cosy_cosp)

    def create_pose(self, x, y, yaw):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0

        pose.pose.orientation.x = 0.0
        pose.pose.orientation.y = 0.0
        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)

        return pose

    def send_goal(self, x, y, yaw):
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = self.create_pose(x, y, yaw)

        self.get_logger().info(f'Fahre zu: x={x:.2f}, y={y:.2f}, yaw={yaw:.2f}')

        self.client.wait_for_server()

        future = self.client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Ziel wurde abgelehnt!')
            return False

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        result = result_future.result()

        if result is None:
            self.get_logger().error('Kein Ergebnis erhalten.')
            return False

        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Ziel erreicht!')
            return True
        else:
            self.get_logger().error(f'Navigation fehlgeschlagen, Status: {result.status}')
            return False

    def run(self):
        self.get_logger().info('Warte auf Startposition aus /amcl_pose ...')

        while rclpy.ok() and self.start_pose is None:
            rclpy.spin_once(self, timeout_sec=0.5)

        if self.start_pose is None:
            self.get_logger().error('Startposition konnte nicht gelesen werden.')
            return

        # 1. Zum Ziel fahren
        success = self.send_goal(self.target_x, self.target_y, self.target_yaw)
        if not success:
            return

        # Hier könnte später Pick/Place-Aktion kommen
        self.get_logger().info('Am Ziel angekommen. Simuliere Pick/Place ...')

        # 2. Zurück zur Startposition
        sx, sy, syaw = self.start_pose
        self.get_logger().info('Fahre zurück zur Startposition ...')
        self.send_goal(sx, sy, syaw)


def main(args=None):
    rclpy.init(args=args)
    node = PickPlaceNavigator()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Erklärung Zeile für Zeile

| Zeile | Code | Erklärung |
| --- | --- | --- |
| 1 | `import math` | Importiert die Python-Bibliothek `math`. Sie wird für Winkelberechnungen gebraucht. |
| 2 | Leerzeile | Macht den Code übersichtlicher. |
| 3 | `import rclpy` | Importiert die wichtigste Python-Bibliothek für ROS2. Damit kann Python mit ROS2 arbeiten. |
| 4 | `from rclpy.node import Node` | Importiert die Klasse `Node`. Jeder ROS2-Knoten basiert auf dieser Klasse. |
| 5 | `from rclpy.action import ActionClient` | Importiert den `ActionClient`. Damit kann das Programm eine längere Aufgabe an ROS2 senden, zum Beispiel eine Navigation. |
| 6 | Leerzeile | Trennt die ROS2-Importe von den Nachrichten-Importen. |
| 7 | `from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped` | Importiert zwei Nachrichtentypen. `PoseStamped` wird für Zielpositionen genutzt. `PoseWithCovarianceStamped` wird für die geschätzte AMCL-Position genutzt. |
| 8 | `from nav2_msgs.action import NavigateToPose` | Importiert die Nav2-Action `NavigateToPose`. Diese Action sagt Nav2: "Fahre zu dieser Pose." |
| 9 | `from action_msgs.msg import GoalStatus` | Importiert Statuswerte für Actions. Damit kann geprüft werden, ob die Navigation erfolgreich war. |
| 10 | Leerzeile | Sorgt für bessere Lesbarkeit. |
| 11 | Leerzeile | Trennt die Importe von der Klasse. |
| 12 | `class PickPlaceNavigator(Node):` | Definiert die Klasse `PickPlaceNavigator`. Sie ist ein ROS2-Knoten, weil sie von `Node` erbt. |
| 13 | `def __init__(self):` | Definiert den Konstruktor. Er wird automatisch ausgeführt, wenn ein Objekt der Klasse erstellt wird. |
| 14 | `super().__init__('pick_place_navigator')` | Startet den ROS2-Knoten mit dem Namen `pick_place_navigator`. |
| 15 | Leerzeile | Trennt die Knotenerstellung vom ActionClient. |
| 16 | `self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')` | Erstellt einen ActionClient für Nav2. Er verbindet sich mit der Action `navigate_to_pose`. |
| 17 | Leerzeile | Trennt den ActionClient von der Startposition. |
| 18 | `self.start_pose = None` | Erstellt eine Variable für die Startposition. `None` bedeutet: Es wurde noch keine Startposition gespeichert. |
| 19 | Leerzeile | Trennt die Startposition vom Subscriber. |
| 20 | `self.pose_sub = self.create_subscription(` | Erstellt einen Subscriber. Ein Subscriber hört auf ein ROS2-Topic und reagiert auf neue Nachrichten. |
| 21 | `PoseWithCovarianceStamped,` | Gibt an, welchen Nachrichtentyp das Topic liefert. `/amcl_pose` verwendet diesen Typ. |
| 22 | `'/amcl_pose',` | Gibt den Namen des Topics an. Auf `/amcl_pose` veröffentlicht AMCL die geschätzte Roboterposition. |
| 23 | `self.amcl_callback,` | Gibt an, welche Methode aufgerufen wird, wenn eine neue AMCL-Position ankommt. |
| 24 | `10` | Legt die Warteschlangengröße fest. Bis zu 10 Nachrichten können zwischengespeichert werden. |
| 25 | `)` | Beendet den Aufruf von `create_subscription`. |
| 26 | Leerzeile | Trennt den Subscriber vom Zielpunkt. |
| 27 | `# Zielpunkt für "Pick" oder "Place"` | Kommentar: Die folgenden Werte beschreiben den Zielpunkt für die Pick/Place-Aufgabe. |
| 28 | `self.target_x = -0.49` | Speichert die x-Koordinate des Zielpunkts. |
| 29 | `self.target_y = 0.00` | Speichert die y-Koordinate des Zielpunkts. |
| 30 | `self.target_yaw = 0.0` | Speichert die gewünschte Blickrichtung am Zielpunkt. |
| 31 | Leerzeile | Trennt den Konstruktor von der nächsten Methode. |
| 32 | `def amcl_callback(self, msg):` | Definiert die Callback-Methode für `/amcl_pose`. Sie wird automatisch aufgerufen, wenn eine neue Positionsnachricht empfangen wird. |
| 33 | `if self.start_pose is None:` | Prüft, ob noch keine Startposition gespeichert wurde. Dadurch wird die Startposition nur einmal gespeichert. |
| 34 | `self.start_pose = (` | Beginnt das Speichern der Startposition als Tupel. Ein Tupel ist eine feste Sammlung von Werten. |
| 35 | `msg.pose.pose.position.x,` | Liest die aktuelle x-Position aus der AMCL-Nachricht. |
| 36 | `msg.pose.pose.position.y,` | Liest die aktuelle y-Position aus der AMCL-Nachricht. |
| 37 | `self.get_yaw_from_quaternion(msg.pose.pose.orientation)` | Wandelt die Orientierung aus der AMCL-Nachricht in den einfacheren Winkel `yaw` um. |
| 38 | `)` | Beendet das Tupel der Startposition. Es enthält jetzt `x`, `y` und `yaw`. |
| 39 | `self.get_logger().info(` | Startet eine Info-Ausgabe im Terminal. |
| 40 | `f'Startposition gespeichert: '` | Erster Teil der Meldung: Die Startposition wurde gespeichert. |
| 41 | `f'x={self.start_pose[0]:.2f}, '` | Gibt die x-Koordinate mit zwei Nachkommastellen aus. |
| 42 | `f'y={self.start_pose[1]:.2f}, '` | Gibt die y-Koordinate mit zwei Nachkommastellen aus. |
| 43 | `f'yaw={self.start_pose[2]:.2f}'` | Gibt die Blickrichtung mit zwei Nachkommastellen aus. |
| 44 | `)` | Beendet die Log-Ausgabe. |
| 45 | Leerzeile | Trennt die AMCL-Methode von der Winkel-Methode. |
| 46 | `def get_yaw_from_quaternion(self, q):` | Definiert eine Methode, die aus einem Quaternion den Winkel `yaw` berechnet. |
| 47 | `siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)` | Berechnet einen Zwischenschritt für die Umrechnung von Quaternion zu yaw. |
| 48 | `cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)` | Berechnet einen zweiten Zwischenschritt für die Umrechnung. |
| 49 | `return math.atan2(siny_cosp, cosy_cosp)` | Berechnet mit `atan2` den yaw-Winkel und gibt ihn zurück. |
| 50 | Leerzeile | Trennt die Winkel-Methode von der Pose-Methode. |
| 51 | `def create_pose(self, x, y, yaw):` | Definiert eine Methode, die aus `x`, `y` und `yaw` eine ROS2-Zielnachricht erstellt. |
| 52 | `pose = PoseStamped()` | Erstellt eine neue `PoseStamped`-Nachricht. |
| 53 | `pose.header.frame_id = 'map'` | Legt fest, dass die Koordinaten im Karten-Koordinatensystem `map` liegen. |
| 54 | `pose.header.stamp = self.get_clock().now().to_msg()` | Fügt die aktuelle ROS2-Zeit in die Nachricht ein. |
| 55 | Leerzeile | Trennt den Nachrichtenkopf von der Position. |
| 56 | `pose.pose.position.x = x` | Setzt die x-Koordinate der Zielposition. |
| 57 | `pose.pose.position.y = y` | Setzt die y-Koordinate der Zielposition. |
| 58 | `pose.pose.position.z = 0.0` | Setzt die z-Koordinate auf `0.0`, weil der Roboter auf dem Boden fährt. |
| 59 | Leerzeile | Trennt die Position von der Orientierung. |
| 60 | `pose.pose.orientation.x = 0.0` | Setzt den x-Anteil der Orientierung auf `0.0`. Für normale Boden-Navigation wird dieser Anteil nicht gebraucht. |
| 61 | `pose.pose.orientation.y = 0.0` | Setzt den y-Anteil der Orientierung auf `0.0`. |
| 62 | `pose.pose.orientation.z = math.sin(yaw / 2.0)` | Berechnet den z-Anteil der Quaternion-Orientierung aus dem yaw-Winkel. |
| 63 | `pose.pose.orientation.w = math.cos(yaw / 2.0)` | Berechnet den w-Anteil der Quaternion-Orientierung aus dem yaw-Winkel. |
| 64 | Leerzeile | Trennt die Orientierung von der Rückgabe. |
| 65 | `return pose` | Gibt die fertige Zielposition zurück. |
| 66 | Leerzeile | Trennt `create_pose` von `send_goal`. |
| 67 | `def send_goal(self, x, y, yaw):` | Definiert eine Methode, die ein Ziel an Nav2 sendet. |
| 68 | `goal_msg = NavigateToPose.Goal()` | Erstellt eine neue Zielnachricht für die Nav2-Action. |
| 69 | `goal_msg.pose = self.create_pose(x, y, yaw)` | Erstellt die passende Ziel-Pose und speichert sie in der Zielnachricht. |
| 70 | Leerzeile | Trennt die Zielnachricht von der Log-Ausgabe. |
| 71 | `self.get_logger().info(f'Fahre zu: x={x:.2f}, y={y:.2f}, yaw={yaw:.2f}')` | Gibt im Terminal aus, zu welcher Position der Roboter fährt. Die Werte werden mit zwei Nachkommastellen angezeigt. |
| 72 | Leerzeile | Trennt die Ausgabe vom Warten auf Nav2. |
| 73 | `self.client.wait_for_server()` | Wartet, bis der Nav2-Action-Server verfügbar ist. |
| 74 | Leerzeile | Trennt das Warten vom Senden des Ziels. |
| 75 | `future = self.client.send_goal_async(goal_msg)` | Sendet das Ziel asynchron an Nav2. Das Programm bekommt die Antwort später über `future`. |
| 76 | `rclpy.spin_until_future_complete(self, future)` | Lässt ROS2 so lange arbeiten, bis Nav2 die Zielanfrage beantwortet hat. |
| 77 | `goal_handle = future.result()` | Holt die Antwort von Nav2. Daraus sieht man, ob das Ziel angenommen wurde. |
| 78 | Leerzeile | Trennt die Antwort von der Prüfung. |
| 79 | `if not goal_handle.accepted:` | Prüft, ob Nav2 das Ziel abgelehnt hat. |
| 80 | `self.get_logger().error('Ziel wurde abgelehnt!')` | Gibt eine Fehlermeldung aus, wenn Nav2 das Ziel nicht annimmt. |
| 81 | `return False` | Gibt `False` zurück. Das bedeutet: Die Fahrt wurde nicht erfolgreich gestartet. |
| 82 | Leerzeile | Trennt die Fehlerbehandlung vom normalen Ablauf. |
| 83 | `result_future = goal_handle.get_result_async()` | Fordert das Endergebnis der Navigation an. Dieses Ergebnis kommt erst, wenn die Fahrt abgeschlossen ist. |
| 84 | `rclpy.spin_until_future_complete(self, result_future)` | Wartet, bis die Navigation fertig ist. |
| 85 | `result = result_future.result()` | Holt das Ergebnis der Navigation. |
| 86 | Leerzeile | Trennt das Ergebnis von der nächsten Prüfung. |
| 87 | `if result is None:` | Prüft, ob kein Ergebnis angekommen ist. |
| 88 | `self.get_logger().error('Kein Ergebnis erhalten.')` | Gibt eine Fehlermeldung aus, wenn kein Ergebnis vorhanden ist. |
| 89 | `return False` | Gibt `False` zurück, weil die Navigation nicht sicher erfolgreich war. |
| 90 | Leerzeile | Trennt diese Fehlerprüfung von der Erfolgsprüfung. |
| 91 | `if result.status == GoalStatus.STATUS_SUCCEEDED:` | Prüft, ob Nav2 meldet, dass das Ziel erfolgreich erreicht wurde. |
| 92 | `self.get_logger().info('Ziel erreicht!')` | Gibt eine Erfolgsmeldung aus. |
| 93 | `return True` | Gibt `True` zurück. Das bedeutet: Die Navigation war erfolgreich. |
| 94 | `else:` | Wird ausgeführt, wenn der Status nicht erfolgreich war. |
| 95 | `self.get_logger().error(f'Navigation fehlgeschlagen, Status: {result.status}')` | Gibt eine Fehlermeldung mit dem konkreten Status aus. Das hilft beim Fehlersuchen. |
| 96 | `return False` | Gibt `False` zurück, weil die Navigation nicht erfolgreich war. |
| 97 | Leerzeile | Trennt `send_goal` von der Hauptlogik `run`. |
| 98 | `def run(self):` | Definiert die Methode, die den ganzen Pick/Place-Ablauf startet. |
| 99 | `self.get_logger().info('Warte auf Startposition aus /amcl_pose ...')` | Gibt aus, dass der Roboter auf seine aktuelle AMCL-Position wartet. |
| 100 | Leerzeile | Trennt die Ausgabe von der Warteschleife. |
| 101 | `while rclpy.ok() and self.start_pose is None:` | Wartet so lange, bis ROS2 läuft und eine Startposition gespeichert wurde. |
| 102 | `rclpy.spin_once(self, timeout_sec=0.5)` | Lässt ROS2 kurz arbeiten, damit neue Nachrichten von `/amcl_pose` verarbeitet werden können. |
| 103 | Leerzeile | Trennt die Warteschleife von der Sicherheitsprüfung. |
| 104 | `if self.start_pose is None:` | Prüft nach dem Warten, ob trotzdem keine Startposition vorhanden ist. |
| 105 | `self.get_logger().error('Startposition konnte nicht gelesen werden.')` | Gibt eine Fehlermeldung aus, wenn keine Startposition gelesen werden konnte. |
| 106 | `return` | Beendet den Ablauf, weil ohne Startposition keine sichere Rückfahrt möglich ist. |
| 107 | Leerzeile | Trennt die Startpositionsprüfung von der Hinfahrt. |
| 108 | `# 1. Zum Ziel fahren` | Kommentar: Jetzt beginnt der erste Schritt, die Fahrt zum Zielpunkt. |
| 109 | `success = self.send_goal(self.target_x, self.target_y, self.target_yaw)` | Sendet den gespeicherten Zielpunkt an Nav2 und speichert, ob die Fahrt erfolgreich war. |
| 110 | `if not success:` | Prüft, ob die Hinfahrt fehlgeschlagen ist. |
| 111 | `return` | Beendet den Ablauf, wenn das Ziel nicht erreicht wurde. |
| 112 | Leerzeile | Trennt die Hinfahrt von der Pick/Place-Stelle. |
| 113 | `# Hier könnte später Pick/Place-Aktion kommen` | Kommentar: An dieser Stelle könnte später Code für Greifer, Servo oder Objektaufnahme eingefügt werden. |
| 114 | `self.get_logger().info('Am Ziel angekommen. Simuliere Pick/Place ...')` | Gibt aus, dass der Roboter am Ziel ist. Die Pick/Place-Aktion wird hier nur simuliert. |
| 115 | Leerzeile | Trennt die simulierte Aktion von der Rückfahrt. |
| 116 | `# 2. Zurück zur Startposition` | Kommentar: Jetzt beginnt die Rückfahrt zur gespeicherten Startposition. |
| 117 | `sx, sy, syaw = self.start_pose` | Zerlegt die gespeicherte Startposition in drei einzelne Variablen: `sx`, `sy` und `syaw`. |
| 118 | `self.get_logger().info('Fahre zurück zur Startposition ...')` | Gibt aus, dass der Roboter zurück zur Startposition fährt. |
| 119 | `self.send_goal(sx, sy, syaw)` | Sendet die gespeicherte Startposition als neues Ziel an Nav2. |
| 120 | Leerzeile | Trennt die Klasse vom Hauptprogramm. |
| 121 | Leerzeile | Zusätzlicher Abstand für bessere Lesbarkeit. |
| 122 | `def main(args=None):` | Definiert die Hauptfunktion. Sie ist der Startpunkt des Programms. |
| 123 | `rclpy.init(args=args)` | Startet ROS2 für dieses Python-Programm. |
| 124 | `node = PickPlaceNavigator()` | Erstellt den Pick/Place-Navigationsknoten. Dabei wird automatisch `__init__` ausgeführt. |
| 125 | `node.run()` | Startet den Ablauf: Startposition lesen, zum Ziel fahren, Pick/Place simulieren, zurückfahren. |
| 126 | `node.destroy_node()` | Zerstört den ROS2-Knoten sauber, wenn der Ablauf fertig ist. |
| 127 | `rclpy.shutdown()` | Beendet ROS2 für dieses Programm. |
| 128 | Leerzeile | Trennt die Hauptfunktion vom Startblock. |
| 129 | Leerzeile | Zusätzlicher Abstand für bessere Lesbarkeit. |
| 130 | `if __name__ == '__main__':` | Prüft, ob diese Datei direkt gestartet wurde. |
| 131 | `main()` | Ruft die Hauptfunktion auf und startet damit das Programm. |

## Ablauf des Programms

```text
Programm starten
        ↓
ROS2 initialisieren
        ↓
PickPlaceNavigator-Knoten erstellen
        ↓
Auf /amcl_pose warten
        ↓
Aktuelle Startposition speichern
        ↓
Zum Pick/Place-Ziel fahren
        ↓
Prüfen, ob Ziel erreicht wurde
        ↓
Pick/Place-Aktion simulieren
        ↓
Zur gespeicherten Startposition zurückfahren
        ↓
Knoten beenden
        ↓
ROS2 herunterfahren
```

## Wo wird das Ziel geändert?

Der Pick/Place-Zielpunkt steht hier:

```python
self.target_x = -0.49
self.target_y = 0.00
self.target_yaw = 0.0
```

| Wert | Bedeutung |
| --- | --- |
| `target_x` | x-Koordinate des Zielpunkts auf der Karte. |
| `target_y` | y-Koordinate des Zielpunkts auf der Karte. |
| `target_yaw` | Blickrichtung des Roboters am Zielpunkt. |

Wenn der Roboter zu einem anderen Ort fahren soll, änderst du diese drei Werte.

## Warum wird `/amcl_pose` benutzt?

`/amcl_pose` liefert die aktuelle geschätzte Position des Roboters auf der Karte. Der Code speichert die erste empfangene Position als Startposition.

Dadurch muss die Rückfahrt nicht fest im Code eingetragen werden. Der Roboter merkt sich selbst, wo er gestartet ist.

## Wo könnte später Pick/Place-Code eingefügt werden?

Diese Stelle ist dafür gedacht:

```python
# Hier könnte später Pick/Place-Aktion kommen
self.get_logger().info('Am Ziel angekommen. Simuliere Pick/Place ...')
```

Hier könnte später zum Beispiel Code stehen, der einen Greifer öffnet, schließt oder einen Gegenstand aufnimmt.

## Wichtig zu wissen

- Nav2 muss laufen, sonst findet `wait_for_server()` keinen Action-Server.
- Die Lokalisierung muss funktionieren, sonst kommt keine sinnvolle Position über `/amcl_pose`.
- In RViz sollte vorher die Startposition mit `2D Pose Estimate` gesetzt werden.
- Die Koordinaten beziehen sich auf die Karte, also auf das Koordinatensystem `map`.
- Der Roboter fährt nur zurück, wenn die Hinfahrt erfolgreich war.
- Die Pick/Place-Aktion ist aktuell nur eine Simulation und bewegt noch keinen Greifer.
