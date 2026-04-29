# Erklärung zu `test_port.py`

Diese Datei testet, über welchen Port und mit welcher Baudrate der MyCobot erreichbar ist.

Das ist nützlich, wenn du nicht sicher bist, ob der Roboterarm unter `/dev/ttyUSB0` oder `/dev/ttyACM0` angeschlossen ist oder welche Baudrate funktioniert.

## Vollständiger Code

```python
from pymycobot.mycobot import MyCobot
import time

tests = [
    ("/dev/ttyUSB0", 115200),
    ("/dev/ttyACM0", 115200),
    ("/dev/ttyUSB0", 1000000),
    ("/dev/ttyACM0", 1000000),
]

for port, baud in tests:
    try:
        print(f"\nTeste {port} @ {baud}")
        mc = MyCobot(port, baud)
        time.sleep(2)
        print("angles:", mc.get_angles())
        print("coords:", mc.get_coords())
        print("is_power_on:", mc.is_power_on())
    except Exception as e:
        print("Fehler:", e)
```

## Erklärung Zeile für Zeile

| Zeile | Code | Anfängerfreundliche Erklärung |
| --- | --- | --- |
| 1 | `from pymycobot.mycobot import MyCobot` | Importiert die MyCobot-Klasse. |
| 2 | `import time` | Importiert Zeitfunktionen für kurze Pausen. |
| 3 | Leerzeile | Trennt die Imports von der Testliste. |
| 4 | `tests = [` | Startet eine Liste mit Verbindungsvarianten. |
| 5 | `("/dev/ttyUSB0", 115200),` | Testet Port `/dev/ttyUSB0` mit Baudrate `115200`. |
| 6 | `("/dev/ttyACM0", 115200),` | Testet Port `/dev/ttyACM0` mit Baudrate `115200`. |
| 7 | `("/dev/ttyUSB0", 1000000),` | Testet Port `/dev/ttyUSB0` mit Baudrate `1000000`. |
| 8 | `("/dev/ttyACM0", 1000000),` | Testet Port `/dev/ttyACM0` mit Baudrate `1000000`. |
| 9 | `]` | Beendet die Liste. |
| 10 | Leerzeile | Trennt die Testliste von der Schleife. |
| 11 | `for port, baud in tests:` | Geht alle Testkombinationen nacheinander durch. |
| 12 | `try:` | Startet einen geschützten Bereich. Fehler werden abgefangen. |
| 13 | `print(f"\nTeste {port} @ {baud}")` | Gibt aus, welche Kombination gerade getestet wird. |
| 14 | `mc = MyCobot(port, baud)` | Versucht, mit diesen Werten eine Verbindung aufzubauen. |
| 15 | `time.sleep(2)` | Wartet 2 Sekunden auf die Verbindung. |
| 16 | `print("angles:", mc.get_angles())` | Gibt Gelenkwinkel aus, wenn die Verbindung funktioniert. |
| 17 | `print("coords:", mc.get_coords())` | Gibt Koordinaten aus, wenn die Verbindung funktioniert. |
| 18 | `print("is_power_on:", mc.is_power_on())` | Gibt aus, ob der Arm eingeschaltet ist. |
| 19 | `except Exception as e:` | Fängt Fehler ab, wenn eine Kombination nicht funktioniert. |
| 20 | `print("Fehler:", e)` | Gibt den Fehler im Terminal aus. |

## Wofür ist das nützlich?

Wenn du nicht weißt, welchen Anschluss du in anderen Skripten eintragen musst, kannst du dieses Skript starten. Die Kombination, bei der sinnvolle Werte für Winkel und Koordinaten erscheinen, ist wahrscheinlich die richtige.

## Wichtig zu wissen

- Dieses Skript bewegt den Arm nicht.
- Es testet nur die Verbindung.
- Danach kannst du den funktionierenden Port in den anderen MyCobot-Dateien verwenden.
