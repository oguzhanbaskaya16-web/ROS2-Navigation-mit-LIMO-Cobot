# Erklärung zu `waypoint_navigator.py`

Diese Datei startet einen ROS2-Knoten, der dem LIMO-Roboter automatisch mehrere Zielpunkte schickt. Der Roboter fährt dadurch zuerst zu einem Zielpunkt und danach zum nächsten Zielpunkt.

Kurz gesagt:

1. ROS2 wird gestartet.
2. Ein Navigations-Knoten wird erstellt.
3. Zielpunkte werden als Liste gespeichert.
4. Jeder Zielpunkt wird in eine ROS2-Nachricht umgewandelt.
5. Die Ziele werden nacheinander an Nav2 gesendet.
6. Am Ende wird der Knoten sauber beendet.

## Wichtige Begriffe

| Begriff | Bedeutung |
| --- | --- |
| ROS2-Knoten | Ein einzelnes Programm in ROS2. Dieser Knoten kümmert sich um die Navigation zu Wegpunkten. |
| ActionClient | Ein ROS2-Werkzeug, um eine längere Aufgabe zu starten, zum Beispiel "fahre zu diesem Ziel". |
| Nav2 | Das Navigationssystem von ROS2. Es plant den Weg und steuert den Roboter zum Ziel. |
| Pose | Eine Position mit Ausrichtung. Sie enthält also `x`, `y` und eine Richtung. |
| Waypoint | Ein Zielpunkt, zu dem der Roboter fahren soll. |
| yaw | Die Drehung des Roboters um die senkrechte Achse. Einfach gesagt: die Blickrichtung des Roboters. |

## Vollständiger Code

```python
import math

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose


class SimpleNavigator(Node):
    def __init__(self):
        super().__init__('simple_navigator')

        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # 👉 HIER DEINE PUNKTE (erst hin, dann zurück)
        self.goals = [
            (-0.49, 0.00, 0.0),   # Zielpunkt B
            (-0.78, -0.23, 0.0)   # zurück zu A
        ]

    def create_pose(self, x, y, yaw):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = x
        pose.pose.position.y = y

        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)

        return pose

    def send_goal(self, x, y, yaw):
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = self.create_pose(x, y, yaw)

        self.get_logger().info(f'Fahre zu: {x}, {y}')

        self.client.wait_for_server()

        future = self.client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Ziel abgelehnt!')
            return

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        self.get_logger().info('Ziel erreicht!')

    def run(self):
        for x, y, yaw in self.goals:
            self.send_goal(x, y, yaw)


def main(args=None):
    rclpy.init(args=args)
    node = SimpleNavigator()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Erklärung Zeile für Zeile

| Zeile | Code | Erklärung |
| --- | --- | --- |
| 1 | `import math` | Importiert die Python-Bibliothek `math`. Sie wird später gebraucht, um aus dem Winkel `yaw` die richtige Orientierung für ROS2 zu berechnen. |
| 2 | Leerzeile | Macht den Code übersichtlicher. |
| 3 | `import rclpy` | Importiert die wichtigste Python-Bibliothek für ROS2. Damit kann das Programm ROS2 starten, laufen lassen und wieder beenden. |
| 4 | `from rclpy.node import Node` | Importiert die Klasse `Node`. Ein `Node` ist ein ROS2-Knoten, also ein einzelnes ROS2-Programm. |
| 5 | `from rclpy.action import ActionClient` | Importiert den `ActionClient`. Damit kann dieser Knoten eine Aufgabe an einen Action-Server senden, zum Beispiel eine Navigationsaufgabe. |
| 6 | Leerzeile | Trennt die ROS2-Importe von den Nachrichten-Importen. |
| 7 | `from geometry_msgs.msg import PoseStamped` | Importiert den Nachrichtentyp `PoseStamped`. Er beschreibt eine Position und Ausrichtung in einem bestimmten Koordinatensystem. |
| 8 | `from nav2_msgs.action import NavigateToPose` | Importiert die Nav2-Action `NavigateToPose`. Diese Action bedeutet: "Fahre zu dieser Zielposition." |
| 9 | Leerzeile | Sorgt für bessere Lesbarkeit. |
| 10 | Leerzeile | Trennt die Importe von der Klassendefinition. |
| 11 | `class SimpleNavigator(Node):` | Definiert die Klasse `SimpleNavigator`. Sie ist ein ROS2-Knoten, weil sie von `Node` erbt. |
| 12 | `def __init__(self):` | Definiert den Konstruktor. Diese Methode wird automatisch ausgeführt, wenn ein `SimpleNavigator` erstellt wird. |
| 13 | `super().__init__('simple_navigator')` | Startet den ROS2-Knoten mit dem Namen `simple_navigator`. Dieser Name ist in ROS2 sichtbar. |
| 14 | Leerzeile | Trennt die Knotenerstellung von der ActionClient-Erstellung. |
| 15 | `self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')` | Erstellt einen ActionClient für die Navigation. Er verbindet sich mit der Nav2-Action `navigate_to_pose`. |
| 16 | Leerzeile | Trennt den ActionClient von der Zielpunkt-Liste. |
| 17 | `# 👉 HIER DEINE PUNKTE (erst hin, dann zurück)` | Kommentar für dich: Hier werden die Wegpunkte eingetragen. Der Roboter fährt sie in der angegebenen Reihenfolge ab. |
| 18 | `self.goals = [` | Startet eine Liste mit Zielpunkten. Jeder Zielpunkt besteht aus `x`, `y` und `yaw`. |
| 19 | `(-0.49, 0.00, 0.0),   # Zielpunkt B` | Erster Zielpunkt. Der Roboter soll zur Position `x = -0.49`, `y = 0.00` fahren und mit Richtung `0.0` ankommen. |
| 20 | `(-0.78, -0.23, 0.0)   # zurück zu A` | Zweiter Zielpunkt. Danach fährt der Roboter zur Position `x = -0.78`, `y = -0.23` zurück. |
| 21 | `]` | Beendet die Liste der Zielpunkte. |
| 22 | Leerzeile | Trennt den Konstruktor von der nächsten Methode. |
| 23 | `def create_pose(self, x, y, yaw):` | Definiert eine Methode, die aus `x`, `y` und `yaw` eine ROS2-Zielposition erstellt. |
| 24 | `pose = PoseStamped()` | Erstellt eine neue `PoseStamped`-Nachricht. In diese Nachricht werden Position und Richtung eingetragen. |
| 25 | `pose.header.frame_id = 'map'` | Legt fest, dass die Zielposition im Koordinatensystem `map` angegeben ist. Das ist bei Nav2 normalerweise die Karte. |
| 26 | `pose.header.stamp = self.get_clock().now().to_msg()` | Schreibt die aktuelle ROS2-Zeit in die Nachricht. Dadurch weiß Nav2, wann diese Zielposition erstellt wurde. |
| 27 | Leerzeile | Trennt den Nachrichtenkopf von der eigentlichen Position. |
| 28 | `pose.pose.position.x = x` | Speichert die x-Koordinate des Zielpunkts in der Nachricht. |
| 29 | `pose.pose.position.y = y` | Speichert die y-Koordinate des Zielpunkts in der Nachricht. |
| 30 | Leerzeile | Trennt die Position von der Orientierung. |
| 31 | `pose.pose.orientation.z = math.sin(yaw / 2.0)` | Berechnet einen Teil der Orientierung. ROS2 speichert Drehungen als Quaternion, nicht direkt als einfachen Winkel. |
| 32 | `pose.pose.orientation.w = math.cos(yaw / 2.0)` | Berechnet den zweiten wichtigen Teil der Orientierung für eine Drehung um die z-Achse. |
| 33 | Leerzeile | Trennt die Berechnung von der Rückgabe. |
| 34 | `return pose` | Gibt die fertige Zielposition zurück. Diese Nachricht kann jetzt an Nav2 gesendet werden. |
| 35 | Leerzeile | Trennt `create_pose` von der nächsten Methode. |
| 36 | `def send_goal(self, x, y, yaw):` | Definiert eine Methode, die ein einzelnes Ziel an Nav2 sendet. |
| 37 | `goal_msg = NavigateToPose.Goal()` | Erstellt eine neue Zielnachricht für die Nav2-Action `NavigateToPose`. |
| 38 | `goal_msg.pose = self.create_pose(x, y, yaw)` | Erstellt aus `x`, `y` und `yaw` eine `PoseStamped`-Nachricht und speichert sie im Ziel. |
| 39 | Leerzeile | Macht den Code übersichtlicher. |
| 40 | `self.get_logger().info(f'Fahre zu: {x}, {y}')` | Gibt eine Info-Meldung aus. So sieht man im Terminal, zu welchem Punkt der Roboter gerade fahren soll. |
| 41 | Leerzeile | Trennt die Meldung vom Warten auf den Action-Server. |
| 42 | `self.client.wait_for_server()` | Wartet, bis der Nav2-Action-Server verfügbar ist. Ohne diesen Server kann kein Navigationsziel gesendet werden. |
| 43 | Leerzeile | Trennt das Warten vom Senden des Ziels. |
| 44 | `future = self.client.send_goal_async(goal_msg)` | Sendet das Ziel asynchron an Nav2. "Asynchron" bedeutet: Der Auftrag wird gestartet und das Ergebnis kommt später zurück. |
| 45 | `rclpy.spin_until_future_complete(self, future)` | Lässt ROS2 so lange arbeiten, bis Nav2 auf die Zielanfrage geantwortet hat. |
| 46 | `goal_handle = future.result()` | Holt das Ergebnis der Zielanfrage. Daraus kann man erkennen, ob Nav2 das Ziel angenommen hat. |
| 47 | Leerzeile | Trennt das Ergebnis von der Prüfung. |
| 48 | `if not goal_handle.accepted:` | Prüft, ob Nav2 das Ziel abgelehnt hat. |
| 49 | `self.get_logger().error('Ziel abgelehnt!')` | Gibt eine Fehlermeldung aus, wenn Nav2 das Ziel nicht annimmt. |
| 50 | `return` | Beendet die Methode sofort. Der Roboter wartet dann nicht weiter auf dieses Ziel. |
| 51 | Leerzeile | Trennt die Fehlerbehandlung vom normalen Ablauf. |
| 52 | `result_future = goal_handle.get_result_async()` | Fragt asynchron das Endergebnis der Fahrt ab. Dieses Ergebnis kommt erst, wenn die Navigation fertig ist. |
| 53 | `rclpy.spin_until_future_complete(self, result_future)` | Wartet, bis die Fahrt zu diesem Ziel beendet ist. |
| 54 | Leerzeile | Trennt das Warten von der Erfolgsmeldung. |
| 55 | `self.get_logger().info('Ziel erreicht!')` | Gibt aus, dass das Ziel erreicht wurde. |
| 56 | Leerzeile | Trennt `send_goal` von der nächsten Methode. |
| 57 | `def run(self):` | Definiert die Methode, die alle gespeicherten Zielpunkte nacheinander abarbeitet. |
| 58 | `for x, y, yaw in self.goals:` | Geht jeden Zielpunkt aus der Liste `self.goals` durch. Dabei werden die drei Werte direkt in `x`, `y` und `yaw` aufgeteilt. |
| 59 | `self.send_goal(x, y, yaw)` | Sendet den aktuellen Zielpunkt an Nav2 und wartet, bis er erreicht wurde. Erst danach kommt der nächste Punkt. |
| 60 | Leerzeile | Trennt die Klasse vom Hauptprogramm. |
| 61 | Leerzeile | Zusätzlicher Abstand für bessere Lesbarkeit. |
| 62 | `def main(args=None):` | Definiert die Hauptfunktion. Sie ist der zentrale Startpunkt des Programms. |
| 63 | `rclpy.init(args=args)` | Startet ROS2 für dieses Python-Programm. Das muss passieren, bevor ein ROS2-Knoten erstellt wird. |
| 64 | `node = SimpleNavigator()` | Erstellt den Navigations-Knoten. Dabei wird automatisch der Konstruktor `__init__` ausgeführt. |
| 65 | `node.run()` | Startet die Fahrt zu allen gespeicherten Zielpunkten. |
| 66 | `node.destroy_node()` | Zerstört den ROS2-Knoten sauber, wenn alle Ziele abgearbeitet wurden. |
| 67 | `rclpy.shutdown()` | Beendet ROS2 für dieses Programm. |
| 68 | Leerzeile | Trennt die Hauptfunktion vom Startblock. |
| 69 | Leerzeile | Zusätzlicher Abstand für bessere Lesbarkeit. |
| 70 | `if __name__ == '__main__':` | Prüft, ob die Datei direkt gestartet wurde. Nur dann wird `main()` ausgeführt. |
| 71 | `main()` | Ruft die Hauptfunktion auf und startet damit das komplette Programm. |

## Ablauf des Programms

```text
Programm starten
        ↓
ROS2 initialisieren
        ↓
SimpleNavigator-Knoten erstellen
        ↓
ActionClient für navigate_to_pose erstellen
        ↓
Zielpunkte aus self.goals lesen
        ↓
Ziel 1 an Nav2 senden
        ↓
Warten, bis Ziel 1 erreicht ist
        ↓
Ziel 2 an Nav2 senden
        ↓
Warten, bis Ziel 2 erreicht ist
        ↓
Knoten beenden
        ↓
ROS2 herunterfahren
```

## Wie du eigene Zielpunkte einträgst

Die Zielpunkte stehen in dieser Liste:

```python
self.goals = [
    (-0.49, 0.00, 0.0),
    (-0.78, -0.23, 0.0)
]
```

Jeder Eintrag hat diese Form:

```python
(x, y, yaw)
```

| Wert | Bedeutung |
| --- | --- |
| `x` | Position auf der Karte in x-Richtung. |
| `y` | Position auf der Karte in y-Richtung. |
| `yaw` | Blickrichtung des Roboters am Zielpunkt. |

Beispiel mit drei Zielpunkten:

```python
self.goals = [
    (1.0, 0.0, 0.0),
    (1.0, 1.0, 1.57),
    (0.0, 0.0, 3.14)
]
```

Hier fährt der Roboter zuerst zu Punkt 1, danach zu Punkt 2 und danach zu Punkt 3.

## Wichtig zu wissen

- Vor dem Start muss Nav2 laufen, sonst findet `wait_for_server()` keinen Action-Server.
- Die Startposition des Roboters sollte in RViz mit `2D Pose Estimate` gesetzt sein.
- Screenshot: [2dposeestimate.png](../../Konsolenausgabe_Screenshots/2dposeestimate.png)
- Die Koordinaten beziehen sich auf die geladene Karte, also auf das Koordinatensystem `map`.
- `yaw = 0.0` bedeutet meistens: Der Roboter schaut in Richtung der positiven x-Achse der Karte.
- Der nächste Wegpunkt wird erst gesendet, wenn der vorherige Wegpunkt abgeschlossen ist.
