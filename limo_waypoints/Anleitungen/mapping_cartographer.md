# 🗺️ Mapping mit Cartographer (LIMO + ROS2 Foxy)

---

## 1. LIMO starten (Basis + TF)

- Terminal 1 (ROS2 Foxy) auf dem LIMO:

```bash
ros2 launch limo_bringup limo_start.launch.py pub_odom_tf:=true
```

## 2. Cartographer starten

- Terminal 2 (foxy) auf dem LIMO:

```bash
ros2 launch limo_bringup cartographer.launch.py
```

## 3. RViz starten (Visualisierung)

- Terminal 3 (foxy) auf dem LIMO:

```bash
rviz2
```

## 4. Roboter manuell bewegen

- Steuerung über **Bluetooth / App / Controller**
- Fahre den Raum vollständig ab

### ⚠️ Wichtig:
- langsam fahren  
- gleichmäßig bewegen  
- keine schnellen Drehungen  

👉 Ziel:
- komplette Umgebung erfassen
- keine Bereiche auslassen

## 5. In Map-Ordner wechseln

- Terminal 4 (foxy) auf dem LIMO:

```bash
cd /home/agilex/agilex_ws/src/limo_ros/limo_bringup/maps
```

## 6. Trajektorie beenden

```bash
ros2 service call /finish_trajectory cartographer_ros_msgs/srv/FinishTrajectory "{trajectory_id: 0}"
```

## 7. SLAM-Zustand speichern (.pbstream)

```bash
ros2 service call /write_state cartographer_ros_msgs/srv/WriteState "{filename: '/home/agilex/map.pbstream'}"
```
👉 Speichert die Rohdaten der Karte (Cartographer-Format)

## 8. Karte als Nav2-Map speichern

```bash
ros2 run nav2_map_server map_saver_cli -f /home/agilex/agilex_ws/src/limo_ros/limo_bringup/maps/labor_map
```
👉 Erstellt:

- labor_map.pgm
- labor_map.yaml

## 9. Map in Navigation einbinden

Datei öffnen:

```bash
~/limo_ros2_ws/src/limo_ros2/limo_bringup/launch/limo_nav2.launch.py
```

👉 Dort Map-Pfad anpassen:

map: /home/agilex/agilex_ws/src/limo_ros/limo_bringup/maps/labor_map.yaml