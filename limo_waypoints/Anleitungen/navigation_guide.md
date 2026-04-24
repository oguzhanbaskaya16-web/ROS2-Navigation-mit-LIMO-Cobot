## 1. LIMO starten (Basis + TF)

- Terminal 1 (foxy) auf dem LIMO:

```bash
ros2 launch limo_bringup limo_start.launch.py pub_odom_tf:=true
```

## 2. Navigation starten (Nav2)

- Terminal 2 (foxy) auf dem LIMO:

```bash
ros2 launch limo_bringup limo_nav2.launch.py
```

👉  Nach dem Start:

- RViz2 öffnet sich automatisch
- die gespeicherte Map wird angezeigt

## 3. Startposition setzen (Pose Estimate)

- In RViz auf **"2D Pose Estimate"** klicken  
- Auf die ungefähre Position des Roboters in der Map klicken  
- Richtung durch Ziehen der Maus festlegen  

👉 Wichtig:
- Position möglichst genau setzen  
- sonst kann die Navigation ungenau sein  

👉 Was passiert dabei:
- Die Lokalisierung (AMCL) wird initialisiert  
- Die Partikelverteilung wird angepasst  

👉 Sichtbares Ergebnis in RViz:
- Die Map bzw. Umgebung passt sich an  
- Bereiche färben sich **grün / stabil**  
- Vorher „unsichere“ oder „rote“ Bereiche werden korrekt ausgerichtet  

👉 Bedeutung:
- Grün = gute Übereinstimmung zwischen Sensor (LiDAR) und Map  
- Der Roboter weiß jetzt, **wo er sich befindet**

## 4. Ziel setzen (2D Nav Goal)

- In RViz auf **"2D Nav Goal"** klicken  
- Zielposition auf der Map auswählen  
- Richtung durch Ziehen der Maus festlegen  

👉 Ergebnis:
- Eine geplante Route wird angezeigt (**lila Linie**)  
- Der Roboter fährt automatisch zum Ziel  

👉 Bedeutung der Farben:
- **Lila Linie** = geplanter Pfad (Global Path)  
- Zeigt die optimale Route vom aktuellen Standort zum Ziel  

👉 Hinweis:
- Wenn keine Route erscheint:
  - Startposition (Pose Estimate) nicht korrekt gesetzt
  - oder Map / Lokalisierung stimmt nicht