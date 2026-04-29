# Erklärung zu `move_arm.py`

Diese Datei ist ein Testskript, um zu prüfen, ob der MyCobot verbunden ist, eingeschaltet werden kann und eine einfache Bewegung ausführt.

## Vollständiger Code

```python
from pymycobot.mycobot import MyCobot
import time

mc = MyCobot('/dev/ttyACM0', 115200)
time.sleep(2)

print("Start angles:", mc.get_angles())
print("Power:", mc.is_power_on())

# Reset durchführen
print("Release servos...")
mc.release_all_servos()
time.sleep(2)

print("Power on...")
mc.power_on()
time.sleep(2)

print("Set fresh mode...")
mc.set_fresh_mode(1)
time.sleep(1)

print("Angles nach Reset:", mc.get_angles())

# Bewegung testen
print("Sende Bewegung...")
mc.send_angles([0, -30, 30, 0, 0, 0], 40)

for i in range(10):
    time.sleep(1)
    print(f"t={i+1}s moving:", mc.is_moving(), " angles:", mc.get_angles())
```

## Erklärung Zeile für Zeile

| Zeile | Code | Anfängerfreundliche Erklärung |
| --- | --- | --- |
| 1 | `from pymycobot.mycobot import MyCobot` | Importiert die MyCobot-Klasse, damit Python mit dem Roboterarm kommunizieren kann. |
| 2 | `import time` | Importiert Zeitfunktionen für Pausen. |
| 3 | Leerzeile | Macht den Code übersichtlicher. |
| 4 | `mc = MyCobot('/dev/ttyACM0', 115200)` | Verbindet sich mit dem MyCobot über den Port `/dev/ttyACM0`. |
| 5 | `time.sleep(2)` | Wartet 2 Sekunden, damit die Verbindung Zeit zum Starten hat. |
| 6 | Leerzeile | Trennt die Verbindung von den ersten Ausgaben. |
| 7 | `print("Start angles:", mc.get_angles())` | Gibt die aktuellen Gelenkwinkel aus. |
| 8 | `print("Power:", mc.is_power_on())` | Gibt aus, ob der Arm eingeschaltet ist. |
| 9 | Leerzeile | Trennt die Startausgaben vom Reset-Ablauf. |
| 10 | `# WICHTIG: Reset durchführen` | Kommentar: Der nächste Block setzt den Arm in einen vorbereiteten Zustand. |
| 11 | `print("Release servos...")` | Gibt aus, dass die Servos gelöst werden. |
| 12 | `mc.release_all_servos()` | Löst die Servos. Das ist Teil des Reset-Ablaufs. |
| 13 | `time.sleep(2)` | Wartet 2 Sekunden. |
| 14 | Leerzeile | Trennt das Lösen der Servos vom Einschalten. |
| 15 | `print("Power on...")` | Gibt aus, dass der Arm eingeschaltet wird. |
| 16 | `mc.power_on()` | Schaltet den MyCobot ein. |
| 17 | `time.sleep(2)` | Wartet, bis der Arm bereit ist. |
| 18 | Leerzeile | Trennt das Einschalten vom Fresh Mode. |
| 19 | `print("Set fresh mode...")` | Gibt aus, dass der Fresh Mode gesetzt wird. |
| 20 | `mc.set_fresh_mode(1)` | Aktiviert den Fresh Mode. Dadurch werden neue Bewegungsbefehle sauber verarbeitet. |
| 21 | `time.sleep(1)` | Kurze Wartezeit nach dem Moduswechsel. |
| 22 | Leerzeile | Trennt den Reset von der nächsten Ausgabe. |
| 23 | `print("Angles nach Reset:", mc.get_angles())` | Gibt die Winkel nach dem Reset aus. |
| 24 | Leerzeile | Trennt die Reset-Ausgabe vom Bewegungstest. |
| 25 | `# Bewegung testen` | Kommentar: Der nächste Block testet eine echte Armbewegung. |
| 26 | `print("Sende Bewegung...")` | Gibt aus, dass eine Bewegung gesendet wird. |
| 27 | `mc.send_angles([0, -30, 30, 0, 0, 0], 40)` | Sendet eine Testbewegung an den Arm. Die Liste enthält 6 Gelenkwinkel, `40` ist die Geschwindigkeit. |
| 28 | Leerzeile | Trennt den Bewegungsbefehl von der Beobachtungsschleife. |
| 29 | `for i in range(10):` | Wiederholt die folgende Ausgabe 10-mal. |
| 30 | `time.sleep(1)` | Wartet jeweils 1 Sekunde. |
| 31 | `print(f"t={i+1}s moving:", mc.is_moving(), " angles:", mc.get_angles())` | Gibt aus, ob der Arm sich noch bewegt und welche Winkel aktuell gemeldet werden. |

## Wofür ist das nützlich?

Dieses Skript ist gut zum Testen:

- Ist der MyCobot erreichbar?
- Lässt er sich einschalten?
- Kann er Winkel lesen?
- Führt er eine einfache Bewegung aus?

## Wichtig zu wissen

- Dieses Skript bewegt den Arm wirklich.
- Vor dem Start sollte genug Platz um den Arm sein.
- Wenn der Port falsch ist, kann keine Verbindung aufgebaut werden.
