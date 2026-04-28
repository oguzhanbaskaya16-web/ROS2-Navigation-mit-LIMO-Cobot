---

# 🧱 LIMO – Baustein Follow (Mit Depth-Kamera)

## 🔧 Voraussetzungen

* ROS1 (Noetic) installiert
* `limo_base` erfolgreich gebaut
* YOLO-Modell (`best.pt`) vorhanden
* Kamera (Astra) funktioniert

---

## 🚀 1. LIMO Base starten

Terminal 1:

```bash
cd ~/agilex_ws
source devel/setup.bash
roslaunch limo_base limo_base.launch
```

➡️ **Wichtig:** Dieses Terminal offen lassen!

---

## 📷 2. Kamera starten

Terminal 2:

```bash
source ~/agilex_ws/devel_isolated/astra_camera/setup.bash
roslaunch astra_camera dabai_u3.launch
```

---

## 🤖 3. Baustein Publisher starten

```bash
source ~/agilex_ws/devel/setup.bash
python3 ~/yolo_baustein_publisher.py
```

[Link](https://github.com/oguzhanbaskaya16-web/ROS2-Navigation-mit-LIMO-Cobot/blob/main/limo_waypoints/limo_object_detection/yolo_baustein_publisher.py) zum Skript

---

---

## 🤖 4. Baustein Follow (mit Depth-Kamera) starten

```bash
source ~/agilex_ws/devel/setup.bash
python3 ~/yolo_baustein_follow_depth.py
```


---

## 🎮 Verhalten

* LIMO dreht sich zum Baustein
* LIMO fährt nach vorne, bis zum angegebenen Abstand (TARGET_DISTANCE_M = 0.80), kann beliebig geändert werden
* Stoppt, wenn kein Objekt erkannt wird


---

## 🧪 Test (manuell)

```bash
rostopic pub -r 10 /cmd_vel geometry_msgs/Twist "linear:
  x: 0.05
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0"
```

➡️ Prüft, ob LIMO fahren kann

---

## 🛑 Stoppen

* `Ctrl + C` in allen Terminals

