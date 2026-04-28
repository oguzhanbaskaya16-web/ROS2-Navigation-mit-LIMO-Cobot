

---

# 🧱 LIMO – Baustein Follow (Startanleitung)

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

## 🧠 3. Objekterkennung starten (YOLO)

Terminal 3:

```bash
python3 yolo_limo_view.py
```

➡️ Öffnet die Kamera und makiert den Baustein, wenn er zu sehen ist.

---

## 🤖 4. Baustein Publisher starten

```bash
source ~/agilex_ws/devel/setup.bash
python3 ~/yolo_baustein_publisher.py
```

[Link](https://github.com/oguzhanbaskaya16-web/ROS2-Navigation-mit-LIMO-Cobot/blob/main/limo_waypoints/limo_object_detection/yolo_baustein_publisher.py) zum Skript

---

---

## 🤖 4. Baustein Follow starten

```bash
source ~/agilex_ws/devel/setup.bash
python3 ~/yolo_baustein_follow.py
```

[Link](https://github.com/oguzhanbaskaya16-web/ROS2-Navigation-mit-LIMO-Cobot/blob/main/limo_waypoints/limo_object_detection/yolo_baustein_follow.py) zum Skript

---

## 🎮 Verhalten

* LIMO dreht sich zum Baustein
* LIMO fährt nach vorne, wenn Baustein mittig ist
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

---

## ⚠️ Häufige Fehler

**LIMO fährt nicht:**

* `limo_base` läuft nicht
* `/cmd_vel` hat keinen Subscriber

```bash
rostopic info /cmd_vel
```

---

**Keine Objekterkennung:**

* Kamera Topic prüfen:

```bash
rostopic list | grep camera
```

---

**Falsche Richtung:**

* In `baustein_follow.py` Vorzeichen von `angular.z` ändern

---
