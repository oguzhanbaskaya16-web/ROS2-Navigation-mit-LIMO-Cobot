
# 🤖 YOLO Modell auf dem LIMO verwenden (Live Detection)

---

## 1. Modell auf den LIMO übertragen

```bash
scp PFAD/ZU/best.pt agilex@ROBOT_IP:~
````

👉 Beispiel:

```bash
scp best.pt agilex@192.168.0.192:~
```

---

## 2. Python-Skript ausführbar machen

```bash
chmod +x ~/yolo_limo_view.py
```
[Link](https://github.com/oguzhanbaskaya16-web/ROS2-Navigation-mit-LIMO-Cobot/blob/main/limo_waypoints/limo_object_detection/yolo_limo_view.py) zum Code

---

## 3. ROS Master starten

* Terminal 1:

```bash
roscore
```

---

## 4. Kamera starten

* Terminal 2:

```bash
source ~/agilex_ws/devel_isolated/astra_camera/setup.bash
roslaunch astra_camera dabai_u3.launch
```

---

## 5. YOLO Detection starten

* Terminal 3:

```bash
python3 ~/yolo_limo_view.py
```

👉 Ergebnis:

* Kamera öffnet sich
* Objekt vor die Kamera halten

---

## 6. Detection Publisher

👉 Skript:

```text
yolo_baustein_publisher.py
```
[Link](https://github.com/oguzhanbaskaya16-web/ROS2-Navigation-mit-LIMO-Cobot/blob/main/limo_waypoints/limo_object_detection/yolo_baustein_publisher.py) zum Code

👉 Funktion:

* Sendet Erkennungsergebnisse als ROS Topic

---

## 7. Detection Ergebnis

👉 Topic:

```text
/baustein_detected
```

👉 Werte:

* `true` → Objekt erkannt
* `false` → Objekt nicht erkannt

---

## ✅ Ergebnis

* Live Objekterkennung läuft auf dem LIMO
* Ergebnisse können in ROS weiterverarbeitet werden

## 8. Topic überwachen (Debugging)

👉 Mit folgendem Befehl kannst du das Topic live auslesen:

```
rostopic echo /baustein_detected
```

👉 Ergebnis:

Anzeige der aktuellen Detection-Werte in Echtzeit


