# Erklärung zu `keyboard_control.py`

Diese Datei ist ein Tastaturprogramm zum manuellen Bewegen des MyCobot.

Du kannst damit einzelne Gelenke Schritt für Schritt bewegen, die aktuelle Pose anzeigen lassen und den Arm in eine Home-Position fahren.

## Kurz gesagt

1. Das Programm verbindet sich mit dem MyCobot.
2. Der Arm wird initialisiert.
3. Der Arm fährt in eine Startposition.
4. Im Terminal werden Steuerbefehle angezeigt.
5. Du gibst eine Taste ein.
6. Das passende Gelenk bewegt sich um einen kleinen Winkel.

## Wichtige Begriffe

| Begriff | Einfache Erklärung |
| --- | --- |
| Gelenk | Ein beweglicher Teil des Roboterarms. |
| Winkel | Position eines Gelenks in Grad. |
| Pose | Aktuelle Stellung des Arms, also Winkel und Koordinaten. |
| Home | Eine einfache Grundstellung des Arms. |
| `clamp` | Begrenzung eines Wertes, damit er nicht zu groß oder zu klein wird. |

## Wichtige Einstellungen

| Einstellung | Bedeutung |
| --- | --- |
| `PORT = "/dev/ttyACM0"` | Anschluss des MyCobot. |
| `BAUD = 115200` | Verbindungsgeschwindigkeit. |
| `STEP = 5` | Jedes Tastensignal bewegt ein Gelenk um 5 Grad. |
| `SPEED = 20` | Bewegungsgeschwindigkeit des Arms. |

## Erklärung Zeile für Zeile

| Zeile | Code | Anfängerfreundliche Erklärung |
| --- | --- | --- |
| 1 | `from pymycobot.mycobot import MyCobot` | Importiert die MyCobot-Klasse. Damit kann Python mit dem Roboterarm kommunizieren. |
| 2 | `import time` | Importiert Zeitfunktionen, damit das Programm Pausen einbauen kann. |
| 3 | Leerzeile | Macht den Code übersichtlicher. |
| 4 | `PORT = "/dev/ttyACM0"` | Speichert den Anschluss, über den der MyCobot verbunden wird. |
| 5 | `BAUD = 115200` | Speichert die Verbindungsgeschwindigkeit. |
| 6 | `STEP = 5      # Grad pro Tastendruck` | Legt fest, dass sich ein Gelenk pro Eingabe um 5 Grad bewegt. |
| 7 | `SPEED = 20    # eher langsam und sicher` | Legt eine langsame und sichere Bewegungsgeschwindigkeit fest. |
| 8 | Leerzeile | Trennt die Einstellungen von den Funktionen. |
| 9 | `def clamp(value, low, high):` | Definiert eine Hilfsfunktion, die einen Wert begrenzt. |
| 10 | `return max(low, min(high, value))` | Gibt den Wert zurück, aber nie kleiner als `low` und nie größer als `high`. |
| 11 | Leerzeile | Trennt die Hilfsfunktion von der Initialisierung. |
| 12 | `def init_arm(mc):` | Definiert eine Funktion zum Vorbereiten des Arms. |
| 13 | `print("Initialisiere Arm...")` | Gibt im Terminal aus, dass der Arm vorbereitet wird. |
| 14 | `mc.release_all_servos()` | Löst die Servos des Arms als Teil der Vorbereitung. |
| 15 | `time.sleep(2)` | Wartet 2 Sekunden. |
| 16 | `mc.power_on()` | Schaltet den MyCobot ein. |
| 17 | `time.sleep(2)` | Wartet wieder 2 Sekunden, damit der Arm bereit ist. |
| 18 | `mc.set_fresh_mode(1)` | Aktiviert den Fresh Mode, damit neue Bewegungsbefehle sauber verarbeitet werden. |
| 19 | `time.sleep(1)` | Wartet 1 Sekunde. |
| 20 | `print("Arm bereit.")` | Gibt aus, dass der Arm bereit ist. |
| 21 | Leerzeile | Trennt die Vorbereitung von der Startbewegung. |
| 22 | `mc.send_angles([0, -20, 20, 0, 0, 0], 20)` | Fährt den Arm in eine einfache Startposition. Die Liste enthält die Winkel der 6 Gelenke. |
| 23 | `time.sleep(5)` | Wartet 5 Sekunden, damit die Bewegung abgeschlossen werden kann. |
| 24 | Leerzeile | Trennt die Initialisierung von der Wartefunktion. |
| 25 | `def wait_until_done(mc, timeout=10):` | Definiert eine Funktion, die wartet, bis der Arm nicht mehr fährt. |
| 26 | `for _ in range(timeout * 10):` | Wiederholt die Prüfung bis zu `timeout * 10`-mal. Bei 10 Sekunden sind das 100 Prüfungen. |
| 27 | `time.sleep(0.1)` | Wartet zwischen den Prüfungen jeweils 0,1 Sekunden. |
| 28 | `if mc.is_moving() == 0:` | Prüft, ob der Arm nicht mehr in Bewegung ist. |
| 29 | `break` | Beendet die Warteschleife, wenn der Arm fertig ist. |
| 30 | Leerzeile | Trennt die Wartefunktion von der Ausgabefunktion. |
| 31 | `def print_pose(mc):` | Definiert eine Funktion, die aktuelle Armwerte ausgibt. |
| 32 | `angles = mc.get_angles()` | Liest die aktuellen Gelenkwinkel aus. |
| 33 | `coords = mc.get_coords()` | Liest die aktuellen Koordinaten des Arms aus. |
| 34 | `print("\nAktuelle Winkel:", angles)` | Gibt die Winkel im Terminal aus. |
| 35 | `print("Aktuelle Koordinaten:", coords)` | Gibt die Koordinaten im Terminal aus. |
| 36 | Leerzeile | Trennt die Ausgabe von der Bewegungsfunktion. |
| 37 | `def move_joint(mc, joint_index, delta):` | Definiert eine Funktion, die ein einzelnes Gelenk bewegt. |
| 38 | `angles = mc.get_angles()` | Liest zuerst alle aktuellen Gelenkwinkel. |
| 39 | `if not angles:` | Prüft, ob keine Winkel gelesen werden konnten. |
| 40 | `print("Konnte Winkel nicht lesen.")` | Gibt eine Fehlermeldung aus. |
| 41 | `return` | Bricht die Funktion ab, weil ohne Winkel keine sichere Bewegung möglich ist. |
| 42 | Leerzeile | Trennt die Fehlerprüfung von der Zielberechnung. |
| 43 | `target = angles[:]` | Erstellt eine Kopie der aktuellen Winkel. |
| 44 | `target[joint_index] = clamp(target[joint_index] + delta, -170, 170)` | Verändert nur ein Gelenk und begrenzt den Zielwinkel auf den Bereich `-170` bis `170`. |
| 45 | Leerzeile | Trennt die Zielberechnung vom Senden der Bewegung. |
| 46 | `print(f"Bewege Gelenk {joint_index + 1} auf {target[joint_index]:.2f}Â°")` | Gibt aus, welches Gelenk auf welchen Winkel bewegt wird. |
| 47 | `mc.send_angles(target, SPEED)` | Sendet die neue Winkelposition an den MyCobot. |
| 48 | `wait_until_done(mc)` | Wartet, bis die Bewegung fertig ist. |
| 49 | `print_pose(mc)` | Gibt danach die neue Pose aus. |
| 50 | Leerzeile | Trennt die Gelenkbewegung von der Home-Funktion. |
| 51 | `def home(mc):` | Definiert eine Funktion für die Home-Position. |
| 52 | `print("Fahre Home...")` | Gibt aus, dass der Arm zur Home-Position fährt. |
| 53 | `mc.send_angles([0, 0, 0, 0, 0, 0], SPEED)` | Sendet Zielwinkel von `0` Grad für alle 6 Gelenke. |
| 54 | `wait_until_done(mc)` | Wartet, bis diese Bewegung fertig ist. |
| 55 | `print_pose(mc)` | Gibt die neue Pose aus. |
| 56 | Leerzeile | Trennt die Home-Funktion von der Hauptfunktion. |
| 57 | `def main():` | Definiert die Hauptfunktion des Programms. |
| 58 | `mc = MyCobot(PORT, BAUD)` | Baut die Verbindung zum MyCobot auf. |
| 59 | `time.sleep(2)` | Wartet 2 Sekunden auf die Verbindung. |
| 60 | `init_arm(mc)` | Initialisiert den Arm. |
| 61 | `print_pose(mc)` | Gibt nach der Initialisierung die aktuelle Pose aus. |
| 62 | Leerzeile | Trennt die Vorbereitung von der Anzeige der Steuerung. |
| 63 | `print("""` | Beginnt eine mehrzeilige Ausgabe im Terminal. |
| 64 | `Steuerung:` | Überschrift der Steuerungsanleitung. |
| 65 | `1 / q  -> Gelenk 1 - / +` | Zeigt die Tasten für Gelenk 1 an. |
| 66 | `2 / w  -> Gelenk 2 - / +` | Zeigt die Tasten für Gelenk 2 an. |
| 67 | `3 / e  -> Gelenk 3 - / +` | Zeigt die Tasten für Gelenk 3 an. |
| 68 | `4 / r  -> Gelenk 4 - / +` | Zeigt die Tasten für Gelenk 4 an. |
| 69 | `5 / t  -> Gelenk 5 - / +` | Zeigt die Tasten für Gelenk 5 an. |
| 70 | `6 / z  -> Gelenk 6 - / +` | Zeigt die Tasten für Gelenk 6 an. |
| 71 | `p      -> Pose ausgeben` | Zeigt, dass `p` die aktuelle Pose ausgibt. |
| 72 | `h      -> Home` | Zeigt, dass `h` die Home-Position anfährt. |
| 73 | `x      -> Beenden` | Zeigt, dass `x` das Programm beendet. |
| 74 | `""")` | Beendet die mehrzeilige Ausgabe. |
| 75 | Leerzeile | Trennt die Anleitung von der Eingabeschleife. |
| 76 | `while True:` | Startet eine Endlosschleife für Tastatureingaben. |
| 77 | `cmd = input("Taste eingeben: ").strip().lower()` | Liest eine Eingabe ein, entfernt Leerzeichen und wandelt sie in Kleinbuchstaben um. |
| 78 | Leerzeile | Trennt die Eingabe von der Auswertung. |
| 79 | `if cmd == "1":` | Prüft, ob die Taste `1` eingegeben wurde. |
| 80 | `move_joint(mc, 0, -STEP)` | Bewegt Gelenk 1 um `STEP` Grad in negative Richtung. |
| 81 | `elif cmd == "q":` | Prüft, ob `q` eingegeben wurde. |
| 82 | `move_joint(mc, 0, STEP)` | Bewegt Gelenk 1 in positive Richtung. |
| 83 | `elif cmd == "2":` | Prüft, ob `2` eingegeben wurde. |
| 84 | `move_joint(mc, 1, -STEP)` | Bewegt Gelenk 2 in negative Richtung. |
| 85 | `elif cmd == "w":` | Prüft, ob `w` eingegeben wurde. |
| 86 | `move_joint(mc, 1, STEP)` | Bewegt Gelenk 2 in positive Richtung. |
| 87 | `elif cmd == "3":` | Prüft, ob `3` eingegeben wurde. |
| 88 | `move_joint(mc, 2, -STEP)` | Bewegt Gelenk 3 in negative Richtung. |
| 89 | `elif cmd == "e":` | Prüft, ob `e` eingegeben wurde. |
| 90 | `move_joint(mc, 2, STEP)` | Bewegt Gelenk 3 in positive Richtung. |
| 91 | `elif cmd == "4":` | Prüft, ob `4` eingegeben wurde. |
| 92 | `move_joint(mc, 3, -STEP)` | Bewegt Gelenk 4 in negative Richtung. |
| 93 | `elif cmd == "r":` | Prüft, ob `r` eingegeben wurde. |
| 94 | `move_joint(mc, 3, STEP)` | Bewegt Gelenk 4 in positive Richtung. |
| 95 | `elif cmd == "5":` | Prüft, ob `5` eingegeben wurde. |
| 96 | `move_joint(mc, 4, -STEP)` | Bewegt Gelenk 5 in negative Richtung. |
| 97 | `elif cmd == "t":` | Prüft, ob `t` eingegeben wurde. |
| 98 | `move_joint(mc, 4, STEP)` | Bewegt Gelenk 5 in positive Richtung. |
| 99 | `elif cmd == "6":` | Prüft, ob `6` eingegeben wurde. |
| 100 | `move_joint(mc, 5, -STEP)` | Bewegt Gelenk 6 in negative Richtung. |
| 101 | `elif cmd == "z":` | Prüft, ob `z` eingegeben wurde. |
| 102 | `move_joint(mc, 5, STEP)` | Bewegt Gelenk 6 in positive Richtung. |
| 103 | `elif cmd == "p":` | Prüft, ob `p` eingegeben wurde. |
| 104 | `print_pose(mc)` | Gibt die aktuelle Pose aus. |
| 105 | `elif cmd == "h":` | Prüft, ob `h` eingegeben wurde. |
| 106 | `home(mc)` | Fährt den Arm in die Home-Position. |
| 107 | `elif cmd == "x":` | Prüft, ob `x` eingegeben wurde. |
| 108 | `print("Beende Programm.")` | Gibt aus, dass das Programm beendet wird. |
| 109 | `break` | Beendet die Endlosschleife. |
| 110 | `else:` | Dieser Fall läuft, wenn keine bekannte Taste eingegeben wurde. |
| 111 | `print("Unbekannte Eingabe.")` | Gibt eine Meldung für unbekannte Eingaben aus. |
| 112 | Leerzeile | Trennt die Hauptfunktion vom Startblock. |
| 113 | `if __name__ == "__main__":` | Prüft, ob diese Datei direkt gestartet wurde. |
| 114 | `main()` | Startet die Hauptfunktion. |

## Tastatursteuerung

| Eingabe | Wirkung |
| --- | --- |
| `1` / `q` | Gelenk 1 negativ / positiv bewegen. |
| `2` / `w` | Gelenk 2 negativ / positiv bewegen. |
| `3` / `e` | Gelenk 3 negativ / positiv bewegen. |
| `4` / `r` | Gelenk 4 negativ / positiv bewegen. |
| `5` / `t` | Gelenk 5 negativ / positiv bewegen. |
| `6` / `z` | Gelenk 6 negativ / positiv bewegen. |
| `p` | Aktuelle Winkel und Koordinaten anzeigen. |
| `h` | Home-Position anfahren. |
| `x` | Programm beenden. |

## Wie funktioniert `move_joint`?

Die Funktion liest zuerst alle aktuellen Gelenkwinkel:

```python
angles = mc.get_angles()
```

Dann wird ein Gelenk verändert:

```python
target[joint_index] = clamp(target[joint_index] + delta, -170, 170)
```

Danach werden alle Zielwinkel an den Roboter gesendet:

```python
mc.send_angles(target, SPEED)
```

## Merksatz

```text
Dieses Skript ist eine einfache manuelle Fernsteuerung für den MyCobot über das Terminal.
```

## Wichtig zu wissen

- Das Programm ist interaktiv und wartet auf Tastatureingaben.
- Es bewegt immer nur ein Gelenk pro Eingabe.
- Die Winkel werden auf den Bereich von `-170` bis `170` Grad begrenzt.
- Wenn der Arm nicht reagiert, sollte zuerst der Port geprüft werden.
