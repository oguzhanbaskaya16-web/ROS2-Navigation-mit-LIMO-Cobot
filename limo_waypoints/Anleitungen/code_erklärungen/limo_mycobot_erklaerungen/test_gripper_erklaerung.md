# Erklärung zu `test_gripper.py`

Diese Datei testet den Greifer des MyCobot.

Der Arm wird verbunden und vorbereitet. Danach wird der Greifer geöffnet, geschlossen und halb geschlossen.

## Kurz gesagt

1. Verbindung zum MyCobot herstellen.
2. Arm zurücksetzen und einschalten.
3. Arm in eine einfache Startposition fahren.
4. Greifer öffnen.
5. Greifer schließen.
6. Greifer halb schließen.

## Erklärung Zeile für Zeile

| Zeile | Code | Anfängerfreundliche Erklärung |
| --- | --- | --- |
| 1 | `from pymycobot.mycobot import MyCobot` | Importiert die MyCobot-Klasse, damit Python mit dem Roboterarm sprechen kann. |
| 2 | `import time` | Importiert Zeitfunktionen für Pausen. |
| 3 | Leerzeile | Macht den Code übersichtlicher. |
| 4 | `mc = MyCobot('/dev/ttyACM0', 115200)` | Baut die Verbindung zum MyCobot über `/dev/ttyACM0` auf. |
| 5 | `time.sleep(2)` | Wartet 2 Sekunden, damit die Verbindung bereit ist. |
| 6 | Leerzeile | Trennt die Verbindung vom Reset-Ablauf. |
| 7 | `# Reset (wie immer!)` | Kommentar: Der folgende Block setzt den Arm in einen vorbereiteten Zustand. |
| 8 | `mc.release_all_servos()` | Löst die Servos als Teil der Vorbereitung. |
| 9 | `time.sleep(2)` | Wartet 2 Sekunden. |
| 10 | `mc.power_on()` | Schaltet den Arm ein. |
| 11 | `time.sleep(2)` | Wartet wieder 2 Sekunden. |
| 12 | `mc.set_fresh_mode(1)` | Aktiviert den Fresh Mode, damit neue Befehle sauber verarbeitet werden. |
| 13 | `time.sleep(1)` | Wartet 1 Sekunde. |
| 14 | Leerzeile | Trennt den Reset von der Startbewegung. |
| 15 | `mc.send_angles([0, -20, 20, 0, 0, 0], 20)` | Fährt den Arm in eine einfache Startstellung. Die Liste enthält 6 Gelenkwinkel. |
| 16 | `time.sleep(5)` | Wartet 5 Sekunden, damit die Bewegung abgeschlossen werden kann. |
| 17 | Leerzeile | Trennt die Armbewegung vom Greifertest. |
| 18 | `print("Ã–ffne Greifer")` | Gibt im Terminal aus, dass der Greifer geöffnet wird. |
| 19 | `mc.set_gripper_state(0, 50, 1)` | Öffnet den Greifer. `0` steht hier für öffnen. |
| 20 | `time.sleep(3)` | Wartet 3 Sekunden. |
| 21 | Leerzeile | Trennt Öffnen und Schließen. |
| 22 | `print("SchlieÃŸe Greifer")` | Gibt im Terminal aus, dass der Greifer geschlossen wird. |
| 23 | `mc.set_gripper_state(1, 50, 1)` | Schließt den Greifer. `1` steht hier für schließen. |
| 24 | `time.sleep(3)` | Wartet 3 Sekunden. |
| 25 | Leerzeile | Trennt Schließen und halbes Schließen. |
| 26 | `print("Halb schlieÃŸen")` | Gibt aus, dass der Greifer halb geschlossen wird. |
| 27 | `mc.set_gripper_value(50, 50)` | Setzt den Greifer auf einen mittleren Wert. Der erste Wert ist die Öffnung, der zweite die Geschwindigkeit. |
| 28 | `time.sleep(3)` | Wartet 3 Sekunden. |

## Was bedeuten die Greiferbefehle?

| Befehl | Bedeutung |
| --- | --- |
| `set_gripper_state(0, 50, 1)` | Greifer öffnen. |
| `set_gripper_state(1, 50, 1)` | Greifer schließen. |
| `set_gripper_value(50, 50)` | Greifer auf einen bestimmten Wert setzen. |

## Wichtig zu wissen

- Dieses Skript bewegt den Greifer wirklich.
- Der Arm fährt vorher in eine Startposition.
- Es ist ein Testskript und kein ROS-Knoten.
- Wenn der Greifer nicht reagiert, zuerst Port, Stromversorgung und Verbindung prüfen.
