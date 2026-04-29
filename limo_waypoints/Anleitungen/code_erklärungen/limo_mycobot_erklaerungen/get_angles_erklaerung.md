# Erklärung zu `get_angles.py`

Diese Datei ist ein sehr kleines Testskript für den MyCobot.

Sie verbindet sich mit dem Roboterarm und gibt danach zwei Dinge aus:

1. die aktuellen Gelenkwinkel
2. die aktuellen Koordinaten des Arms

## Vollständiger Code

```python
from pymycobot.mycobot import MyCobot
mc = MyCobot('/dev/ttyACM0', 115200)
print(mc.get_angles())
print(mc.get_coords())
```

## Erklärung Zeile für Zeile

| Zeile | Code | Anfängerfreundliche Erklärung |
| --- | --- | --- |
| 1 | `from pymycobot.mycobot import MyCobot` | Importiert die Klasse `MyCobot`. Damit kann Python mit dem Roboterarm sprechen. |
| 2 | `mc = MyCobot('/dev/ttyACM0', 115200)` | Baut die Verbindung zum MyCobot auf. `/dev/ttyACM0` ist der Anschluss, `115200` ist die Baudrate. |
| 3 | `print(mc.get_angles())` | Liest die aktuellen Winkel der Gelenke aus und gibt sie im Terminal aus. |
| 4 | `print(mc.get_coords())` | Liest die aktuelle Position des Arms als Koordinaten aus und gibt sie im Terminal aus. |

## Wofür ist das nützlich?

Dieses Skript ist praktisch, wenn du schnell prüfen möchtest:

- Ist der MyCobot erreichbar?
- Welche Gelenkwinkel hat der Arm gerade?
- Welche Koordinaten meldet der Arm gerade?

## Wichtig zu wissen

- Der MyCobot muss am richtigen Port angeschlossen sein.
- Wenn der Port nicht stimmt, funktioniert die Verbindung nicht.
- Dieses Skript bewegt den Arm nicht. Es liest nur Werte aus.
