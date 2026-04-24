
# 🤖 Neue Node hinzufügen (Beispiel: pickplace.py)

---

## 1. Python-Datei erstellen (Windows)

- Auf deinem Windows-PC eine neue Datei erstellen:

```bash
pickplace_navigator.py
````

👉 Hier kommt dein Node-Code rein

---

## 2. Datei auf den LIMO übertragen

```bash
scp .\pickplace_navigator.py agilex@192.168.0.192:~/limo_ros2_ws/src/limo_waypoints/limo_waypoints/
```

👉 Kopiert die Datei in dein ROS2-Paket

---

## 3. Node in `setup.py` registrieren

Link zur Datei: [setup.py](https://github.com/oguzhanbaskaya16-web/ROS2-Navigation-mit-LIMO-Cobot/blob/main/limo_waypoints/setup.py)

Datei öffnen:

```bash
nano ~/limo_ros2_ws/src/limo_waypoints/setup.py
```

👉 Unter `entry_points` hinzufügen:

```python
entry_points={
    'console_scripts': [
        'waypoint_navigator = limo_waypoints.waypoint_navigator:main',
        'pickplace_navigator = limo_waypoints.pickplace_navigator:main',
    ],
},
```

👉 Speichern und Beenden:

* `STRG + O`
* `Enter`
* `STRG + X`

---

## 4. Workspace wechseln

```bash
cd ~/limo_ros2_ws
```

---

## 5. Paket neu builden

```bash
colcon build --packages-select limo_waypoints
```

---

## 6. Umgebung neu laden

```bash
source install/setup.bash
```

---

## ✅ Ergebnis

👉 Dein neuer Node ist jetzt verfügbar und kann gestartet werden mit:

```bash
ros2 run limo_waypoints pickplace_navigator
```

---

## ⚠️ Hinweise

* Dateiname = `pickplace_navigator.py`
* Funktionsname muss `main()` sein
* Name in `setup.py` muss exakt übereinstimmen

---

## 💡 Empfehlung

Es ist oft einfacher:

* Datei lokal auf dem PC bearbeiten
* dann per `scp` auf den LIMO kopieren

---

## 🔗 GitHub 


[pickplace_navigator.py](https://github.com/oguzhanbaskaya16-web/ROS2-Navigation-mit-LIMO-Cobot/blob/main/limo_waypoints/limo_navigation/pickplace_navigator.py)





