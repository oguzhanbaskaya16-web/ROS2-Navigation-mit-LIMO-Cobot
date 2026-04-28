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

## 🦾 5. MyCobot Greifer-Node starten

Der Greifer wird nicht direkt im Fahr-Skript gesteuert.  
Stattdessen wartet ein separater Node auf das ROS-Signal:

```bash
/greif_start
```

Wenn LIMO den Zielabstand erreicht hat, sendet `yolo_baustein_follow_depth.py` automatisch:

```bash
std_msgs/Bool "data: true"
```

Terminal 5:

```bash
source ~/agilex_ws/devel/setup.bash
python3 ~/mycobot_gripper_node.py
```

➡️ **Wichtig:** Dieses Terminal offen lassen!

Der Greifer-Node führt dann automatisch aus:

* Greifer öffnen
* Arm in Vor-Greifposition fahren
* Arm in Greifposition fahren
* Greifer schließen
* Arm anheben

---

## 🧪 Greifer manuell testen

Ohne LIMO-Fahrt kann der Greifer so getestet werden:

```bash
rostopic pub /greif_start std_msgs/Bool "data: true" -1
```

Wenn alles funktioniert, sollte der MyCobot die Greifsequenz starten.

---

## ⚙️ Greifposition anpassen

Die Armpositionen werden in `mycobot_gripper_node.py` eingestellt:

```python
HOME_ANGLES = [0, -20, 20, 0, 0, 0]
PRE_GRASP_ANGLES = [0, -35, 45, 0, 0, 0]
GRASP_ANGLES = [0, -45, 55, 0, 0, 0]
LIFT_ANGLES = [0, -20, 35, 0, 0, 0]
```

Diese Werte müssen praktisch kalibriert werden, damit der Greifer genau vor dem Baustein steht.

---

## 🔁 Gesamtablauf

```text
YOLO erkennt Baustein
→ LIMO richtet sich aus
→ Depth-Kamera misst Abstand
→ LIMO fährt bis TARGET_DISTANCE_M
→ LIMO stoppt
→ /greif_start wird gesendet
→ MyCobot greift
→ MyCobot hebt Baustein an
```
```

Und bei deiner Start-Reihenfolge wäre es dann komplett:

```bash
# Terminal 1
cd ~/agilex_ws
source devel/setup.bash
roslaunch limo_base limo_base.launch

# Terminal 2
source ~/agilex_ws/devel_isolated/astra_camera/setup.bash
roslaunch astra_camera dabai_u3.launch

# Terminal 3
source ~/agilex_ws/devel/setup.bash
python3 ~/yolo_baustein_publisher.py

# Terminal 4
source ~/agilex_ws/devel/setup.bash
python3 ~/mycobot_gripper_node.py

# Terminal 5
source ~/agilex_ws/devel/setup.bash
python3 ~/yolo_baustein_follow_depth.py
```

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