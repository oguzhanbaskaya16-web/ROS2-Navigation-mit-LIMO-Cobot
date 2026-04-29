# Erklärung zu `mycobot_gripper_node.py`

Diese Datei startet einen ROS-Knoten, der den MyCobot-Greifer steuert.

Der Knoten wartet auf ein Signal auf `/greif_start`. Wenn dort `True` ankommt, führt der Roboterarm eine feste Greifsequenz aus.

## Kurz gesagt

1. Der ROS-Knoten startet.
2. Der MyCobot wird verbunden und initialisiert.
3. Der Greifer wird geöffnet.
4. Der Arm fährt in eine Home-Position.
5. Der Knoten wartet auf `/greif_start`.
6. Bei `True` fährt der Arm zur Greifposition.
7. Der Greifer schließt.
8. Der Arm hebt den Baustein an.

## Wichtige Begriffe

| Begriff | Einfache Erklärung |
| --- | --- |
| ROS-Knoten | Ein einzelnes Programm in ROS. Hier steuert es den MyCobot-Greifer. |
| `/greif_start` | Topic, das den Greifvorgang startet. |
| `Bool` | Nachrichtentyp für `True` oder `False`. |
| Home-Position | Sichere Startposition des Arms. |
| Pre-Grasp | Position kurz vor dem eigentlichen Greifen. |
| Grasp | Position, an der der Greifer schließen soll. |
| Lift | Position, zu der der Arm nach dem Greifen anhebt. |

## Wichtige Einstellungen

| Einstellung | Bedeutung |
| --- | --- |
| `PORT = "/dev/ttyACM0"` | Anschluss des MyCobot. |
| `BAUD = 115200` | Verbindungsgeschwindigkeit. |
| `MOVE_SPEED = 25` | Geschwindigkeit für Armbewegungen. |
| `GRIPPER_SPEED = 50` | Geschwindigkeit des Greifers. |
| `HOME_ANGLES` | Startposition des Arms. |
| `PRE_GRASP_ANGLES` | Position vor dem Greifen. |
| `GRASP_ANGLES` | Eigentliche Greifposition. |
| `LIFT_ANGLES` | Position nach dem Greifen zum Anheben. |

## Erklärung Zeile für Zeile

| Zeile | Code | Anfängerfreundliche Erklärung |
| --- | --- | --- |
| 1 | `#!/usr/bin/env python3` | Sagt dem System, dass diese Datei mit Python 3 gestartet werden soll. |
| 2 | `import time` | Importiert Zeitfunktionen für Wartezeiten. |
| 3 | Leerzeile | Macht den Code übersichtlicher. |
| 4 | `import rospy` | Importiert die ROS1-Python-Bibliothek. |
| 5 | `from pymycobot.mycobot import MyCobot` | Importiert die MyCobot-Klasse für die Kommunikation mit dem Roboterarm. |
| 6 | `from std_msgs.msg import Bool` | Importiert den ROS-Nachrichtentyp `Bool` für `True` oder `False`. |
| 7 | Leerzeile | Trennt die Imports von den Einstellungen. |
| 8 | Leerzeile | Zusätzliche optische Trennung. |
| 9 | `PORT = "/dev/ttyACM0"` | Speichert den Anschluss des MyCobot. |
| 10 | `BAUD = 115200` | Speichert die Verbindungsgeschwindigkeit. |
| 11 | `MOVE_SPEED = 25` | Legt die Bewegungsgeschwindigkeit des Arms fest. |
| 12 | `GRIPPER_SPEED = 50` | Legt die Geschwindigkeit des Greifers fest. |
| 13 | Leerzeile | Trennt Verbindungswerte von den Armpositionen. |
| 14 | `HOME_ANGLES = [0, -20, 20, 0, 0, 0]` | Speichert die Startposition des Arms als 6 Gelenkwinkel. |
| 15 | Leerzeile | Trennt die Home-Position von den Greifpositionen. |
| 16 | `# Greifposition links unten.` | Kommentar: Die folgenden Winkel beschreiben eine Greifposition links unten. |
| 17 | `# Wenn der Arm zu weit links greift: ersten Wert naeher an 0 setzen.` | Kommentar mit Kalibrierhinweis für die seitliche Position. |
| 18 | `# Wenn der Arm zu hoch greift: zweiten Wert negativer und dritten Wert groesser setzen.` | Kommentar mit Kalibrierhinweis für die Höhe. |
| 19 | `PRE_GRASP_ANGLES = [-35, -35, 45, 0, 0, 0]` | Position kurz vor dem Greifen. Der Arm fährt zuerst dorthin. |
| 20 | `GRASP_ANGLES = [-35, -52, 62, 0, 0, 0]` | Eigentliche Greifposition. Dort schließt der Greifer. |
| 21 | `LIFT_ANGLES = [-35, -20, 35, 0, 0, 0]` | Hebeposition nach dem Greifen. |
| 22 | Leerzeile | Trennt die Einstellungen von der Klasse. |
| 23 | Leerzeile | Macht den Klassenbeginn sichtbarer. |
| 24 | `class MyCobotGripperNode:` | Definiert die Klasse für den ROS-Greifknoten. |
| 25 | `def __init__(self):` | Definiert den Konstruktor. Er läuft automatisch beim Erstellen des Objekts. |
| 26 | `rospy.init_node("mycobot_gripper_node", anonymous=True)` | Startet den ROS-Knoten mit dem Namen `mycobot_gripper_node`. |
| 27 | Leerzeile | Trennt den ROS-Start von den Variablen. |
| 28 | `self.busy = False` | Speichert, ob gerade eine Greifsequenz läuft. Am Anfang ist der Arm frei. |
| 29 | `self.mc = MyCobot(PORT, BAUD)` | Baut die Verbindung zum MyCobot auf. |
| 30 | `time.sleep(2)` | Wartet 2 Sekunden auf die Verbindung. |
| 31 | Leerzeile | Trennt die Verbindung von der Initialisierung. |
| 32 | `rospy.loginfo("Initialisiere MyCobot.")` | Gibt eine ROS-Info-Meldung aus. |
| 33 | `self.mc.release_all_servos()` | Löst die Servos als Teil der Vorbereitung. |
| 34 | `time.sleep(2)` | Wartet 2 Sekunden. |
| 35 | `self.mc.power_on()` | Schaltet den Arm ein. |
| 36 | `time.sleep(2)` | Wartet 2 Sekunden. |
| 37 | `self.mc.set_fresh_mode(1)` | Aktiviert den Fresh Mode. |
| 38 | `time.sleep(1)` | Wartet 1 Sekunde. |
| 39 | Leerzeile | Trennt die Initialisierung von der Startposition. |
| 40 | `self.open_gripper()` | Öffnet den Greifer. |
| 41 | `self.move_to(HOME_ANGLES, 4.0)` | Fährt den Arm in die Home-Position und wartet 4 Sekunden. |
| 42 | Leerzeile | Trennt die Startposition vom Subscriber. |
| 43 | `rospy.Subscriber("/greif_start", Bool, self.grasp_callback)` | Abonniert `/greif_start`. Bei neuen Nachrichten wird `grasp_callback` aufgerufen. |
| 44 | `rospy.loginfo("MyCobot-Greifnode wartet auf /greif_start.")` | Meldet, dass der Knoten jetzt auf das Greifsignal wartet. |
| 45 | Leerzeile | Trennt den Konstruktor von der Bewegungsfunktion. |
| 46 | `def move_to(self, angles, wait_s):` | Definiert eine Funktion, die den Arm zu bestimmten Gelenkwinkeln fährt. |
| 47 | `rospy.loginfo("Arm bewege zu: %s", angles)` | Gibt aus, zu welchen Winkeln der Arm fahren soll. |
| 48 | `self.mc.send_angles(angles, MOVE_SPEED)` | Sendet die Zielwinkel an den MyCobot. |
| 49 | `time.sleep(wait_s)` | Wartet eine festgelegte Zeit, damit die Bewegung fertig werden kann. |
| 50 | Leerzeile | Trennt die Bewegungsfunktion von der Greifer-Öffnen-Funktion. |
| 51 | `def open_gripper(self):` | Definiert eine Funktion zum Öffnen des Greifers. |
| 52 | `rospy.loginfo("Greifer oeffnen.")` | Gibt aus, dass der Greifer geöffnet wird. |
| 53 | `self.mc.set_gripper_state(0, GRIPPER_SPEED, 1)` | Öffnet den Greifer. `0` steht hier für öffnen. |
| 54 | `time.sleep(2)` | Wartet 2 Sekunden. |
| 55 | Leerzeile | Trennt Öffnen und Schließen. |
| 56 | `def close_gripper(self):` | Definiert eine Funktion zum Schließen des Greifers. |
| 57 | `rospy.loginfo("Greifer schliessen.")` | Gibt aus, dass der Greifer geschlossen wird. |
| 58 | `self.mc.set_gripper_state(1, GRIPPER_SPEED, 1)` | Schließt den Greifer. `1` steht hier für schließen. |
| 59 | `time.sleep(2)` | Wartet 2 Sekunden. |
| 60 | Leerzeile | Trennt die Greiferfunktion von der Callback-Funktion. |
| 61 | `def grasp_callback(self, msg):` | Definiert die Funktion, die bei einem `/greif_start`-Signal ausgeführt wird. |
| 62 | `if not msg.data or self.busy:` | Prüft, ob kein echtes Startsignal kam oder der Arm schon beschäftigt ist. |
| 63 | `return` | Bricht ab, wenn nicht gegriffen werden soll. |
| 64 | Leerzeile | Trennt die Sicherheitsprüfung vom Start der Sequenz. |
| 65 | `self.busy = True` | Markiert den Arm als beschäftigt. |
| 66 | `rospy.loginfo("Greifsignal empfangen. Starte Greifsequenz.")` | Gibt aus, dass die Greifsequenz startet. |
| 67 | Leerzeile | Trennt die Startmeldung vom geschützten Ausführungsblock. |
| 68 | `try:` | Startet einen geschützten Bereich. Fehler werden abgefangen. |
| 69 | `self.open_gripper()` | Öffnet den Greifer vor dem Greifen. |
| 70 | `self.move_to(PRE_GRASP_ANGLES, 4.0)` | Fährt zur Position kurz vor dem Baustein. |
| 71 | `self.move_to(GRASP_ANGLES, 4.0)` | Fährt zur eigentlichen Greifposition. |
| 72 | `self.close_gripper()` | Schließt den Greifer. |
| 73 | `self.move_to(LIFT_ANGLES, 4.0)` | Hebt den Baustein an. |
| 74 | `rospy.loginfo("Greifsequenz beendet.")` | Gibt aus, dass die Greifsequenz fertig ist. |
| 75 | `except Exception as exc:` | Fängt Fehler während der Greifsequenz ab. |
| 76 | `rospy.logerr("Fehler in Greifsequenz: %s", exc)` | Gibt den Fehler als ROS-Fehlermeldung aus. |
| 77 | Leerzeile | Trennt die Klasse vom Startblock. |
| 78 | Leerzeile | Macht den Startblock optisch klarer. |
| 79 | `if __name__ == "__main__":` | Prüft, ob diese Datei direkt gestartet wurde. |
| 80 | `try:` | Startet einen geschützten Bereich für den Programmstart. |
| 81 | `MyCobotGripperNode()` | Erstellt den Greifknoten und initialisiert den Arm. |
| 82 | `rospy.spin()` | Hält das Programm am Laufen, damit es weiter auf `/greif_start` hören kann. |
| 83 | `except rospy.ROSInterruptException:` | Fängt eine normale ROS-Unterbrechung ab. |
| 84 | `pass` | Macht beim normalen Beenden nichts weiter. |

## Greifsequenz

```text
/greif_start = True
        ↓
Greifer öffnen
        ↓
zur Vor-Greifposition fahren
        ↓
zur Greifposition fahren
        ↓
Greifer schließen
        ↓
zur Hebeposition fahren
```

## Warum gibt es `self.busy`?

Wenn während einer Greifbewegung nochmal ein Signal ankommt, soll der Arm nicht gleichzeitig eine zweite Sequenz starten.

Darum prüft der Code:

```python
if not msg.data or self.busy:
    return
```

Das bedeutet: Wenn kein echtes Startsignal kommt oder der Arm gerade beschäftigt ist, passiert nichts.

## Wichtig zu wissen

- Dieser Code greift immer an festen Winkelpositionen.
- Er berechnet keine Zielposition aus Kamera- oder Tiefendaten.
- Für automatische flexible Greifpunkte ist `baustein_auto_grabber.py` zuständig.
- Die Winkelwerte müssen zum echten Aufbau passen.
