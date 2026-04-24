# 📍 Waypoints erstellen (ROS2)

---

## 1. In den Workspace wechseln

```bash
cd ~/limo_ros2_ws/src
```

## 2. Neues ROS2-Paket erstellen

```bash
ros2 pkg create --build-type ament_python limo_waypoints
```

👉 Erstellt ein neues Python-Paket für Waypoints

## 3. In das Paket wechseln

```bash
cd ~/limo_ros2_ws/src/limo_waypoints
```

👉 Ordnerstruktur sollte ungefähr so aussehen:

```text
~/limo_ros2_ws/src/limo_waypoints/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/
│   └── limo_waypoints
├── limo_waypoints/
│   └── __init__.py
└── test/
```
## 4. Python-Skript auf den LIMO übertragen

Auf deinem Windows-PC (im Ordner mit der Datei):

**Anmerkung:** Die Datei befindet sich auf GitHub im Ordner  
[limo_navigation/waypoints_navigator.py](https://github.com/oguzhanbaskaya16-web/ROS2-Navigation-mit-LIMO-Cobot/blob/main/limo_waypoints/limo_navigation/waypoint_navigator.py)

```bash
scp .\waypoints_navigator.py agilex@192.168.0.192:~/limo_ros2_ws/src/limo_waypoints/limo_waypoints/
```


## 5. Paketstruktur prüfen

```bash
cd ~/limo_ros2_ws/src/limo_waypoints/limo_waypoints
ls
```

👉 Überprüfen, ob die Datei vorhanden ist:

* `waypoints_navigator.py`

👉 Hinweis:

*  Falls die Datei nicht angezeigt wird → Übertragung (scp) überprüfen

## 6. Zurück in den Paket-Ordner wechseln

```bash
cd ~/limo_ros2_ws/src/limo_waypoints
```


## 7. setup.py bearbeiten

```bash
nano setup.py
````

👉 Inhalt anpassen bzw. einfügen

👉 Speichern und Beenden:

* `STRG + O` → speichern
* `Enter`
* `STRG + X` → beenden

👉 **Empfehlung:**
Es ist oft einfacher, die Datei lokal auf deinem PC zu bearbeiten und anschließend wieder per `scp` auf den LIMO zu übertragen:

```bash
scp .\setup.py agilex@192.168.0.192:~/limo_ros2_ws/src/limo_waypoints/
```
**Anmerkung:** Die Datei befindet sich auf GitHub im Ordner  
[limo_waypoints/setup.py](https://github.com/oguzhanbaskaya16-web/ROS2-Navigation-mit-LIMO-Cobot/blob/main/limo_waypoints/setup.py)


## 8. package.xml bearbeiten

```bash
nano package.xml
````

👉 Inhalt anpassen bzw. Abhängigkeiten ergänzen

👉 Speichern und Beenden:

* `STRG + O` → speichern
* `Enter`
* `STRG + X` → beenden

---

👉 **Empfehlung:**
Es ist oft einfacher, die Datei lokal auf deinem PC zu bearbeiten und anschließend wieder per `scp` auf den LIMO zu übertragen:

```bash
scp .\package.xml agilex@192.168.0.192:~/limo_ros2_ws/src/limo_waypoints/
```

---

👉 **GitHub-Link zur Datei:**
[package.xml](https://github.com/oguzhanbaskaya16-web/ROS2-Navigation-mit-LIMO-Cobot/blob/main/limo_waypoints/package.xml)

## 9. Workspace builden

```bash
cd ~/limo_ros2_ws
colcon build --packages-select limo_waypoints 
source ~/limo_ros2_ws/install/setup.bash
```

## 10. Prüfen ob ROS den Node erkennt

```bash
ros2 run limo_waypoints waypoint_navigator
```
* Mit `STRG + C` beenden

## 11. LIMO starten (Basis + TF)

- Terminal 1 (foxy) auf dem LIMO:

```bash
ros2 launch limo_bringup limo_start.launch.py pub_odom_tf:=true
```

## 12. Navigation starten (Nav2)

- Terminal 2 (foxy) auf dem LIMO:

```bash
ros2 launch limo_bringup limo_nav2.launch.py
```

## 13. Ungefähre Position in RViz2 setzen (Pose Estimate)

- In RViz auf **"2D Pose Estimate"** klicken  
- Auf die ungefähre Position des Roboters in der Map klicken  
- Richtung durch Ziehen der Maus festlegen  

👉 Ergebnis:
- Die Lokalisierung (AMCL) wird initialisiert  
- Die Position des Roboters wird korrekt geschätzt  

👉 Sichtbares Feedback:
- Anpassung der Map-Darstellung  
- bessere Übereinstimmung zwischen LiDAR und Karte  

## 14. Waypoint-Navigation starten

- Terminal 3 (foxy) auf dem LIMO:

```bash
source ~/limo_ros2_ws/install/setup.bash
ros2 run limo_waypoints waypoint_navigator
```

👉 Ergebnis:

Der Roboter fährt automatisch die definierten Waypoints ab
Die Navigation erfolgt über Nav2






