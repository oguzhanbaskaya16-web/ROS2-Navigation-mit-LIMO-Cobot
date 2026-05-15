# Plan: Autonomes Greif-Szenario mit LIMO Cobot

## System-Überblick (Ist-Zustand)

```
Vorhandene Bausteine:
✓ Nav2 + AMCL Navigation (ROS2)
✓ YOLOv8 Bausteinserkennung (ROS1)
✓ MyCobot Gripper-Sequenz (ROS1)
✓ baustein_auto_grabber.py (Koordinaten-Transformation, ROS1)
✗ Kein integrierter Ablauf-Controller
✗ Kein Rotations-Suchlauf mit YOLO-Feedback
✗ Kein autonomes Annähern an Baustein
```

---

## Ablauf in 5 Phasen

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1       Phase 2        Phase 3     Phase 4   Phase 5 │
│  Navigate  →   Search-Spin →  Center  →  Approach →  Grasp  │
│  to Point      (YOLO)         (YOLO)     (Depth)   (XYZ)    │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1 — Navigation zum Zielpunkt

**Datei:** `limo_navigation/pickplace_navigator.py` (erweitern)

- Nav2 `navigate_to_pose` Action Client
- Fährt zu einem konfigurierbaren Zielpunkt (x, y aus YAML)
- Wartet auf Erfolg → triggert Phase 2

**Relevante Topics:**
| Topic | Typ | Richtung |
|---|---|---|
| `/amcl_pose` | `PoseWithCovarianceStamped` | Subscribe |
| Nav2 Action | `NavigateToPose` | Action Client |

---

## Phase 2 — Rotations-Suchlauf (Search Spin)

**Neue Datei:** `limo_navigation/search_spin_node.py`

```
Logik:
  WHILE kein Baustein erkannt:
    → Drehe LIMO um N Grad (cmd_vel / angular.z)
    → Abonniere /baustein_detected (Bool) von YOLO
    → Kurze Pause → prüfe Erkennung
    → Falls 360° ohne Fund → Fehler / Stopp
  WENN erkannt → Phase 3
```

**Relevante Topics:**
| Topic | Typ | Richtung |
|---|---|---|
| `/cmd_vel` | `Twist` | Publish |
| `/baustein_detected` | `Bool` | Subscribe |
| `/odom` | `Odometry` | Subscribe (Winkel-Tracking) |

**Parameter:**
- `angular_speed`: Rotationsgeschwindigkeit (rad/s)
- `detection_pause`: Wartezeit pro Schritt (s)
- `max_rotation_deg`: Abbruch nach N Grad (Standard: 360°)

---

## Phase 3 — Zentrierung des Bausteins

**Neue Datei:** `limo_navigation/center_baustein_node.py`

```
Logik:
  WHILE Baustein nicht zentriert:
    → Lese /baustein_center (Pixel x, y)
    → Berechne Fehler: offset = center_x - image_width / 2
    → Korrigiere angular.z proportional (P-Regler)
    → Stopp wenn |offset| < THRESHOLD (z.B. 20 Pixel)
  → Phase 4
```

**Relevante Topics:**
| Topic | Typ | Richtung |
|---|---|---|
| `/baustein_center` | `Point` | Subscribe |
| `/cmd_vel` | `Twist` | Publish |

**Parameter:**
- `center_threshold_px`: Erlaubter Pixelabstand zur Bildmitte
- `kp_angular`: P-Regler Verstärkung für Rotation

---

## Phase 4 — Autonomes Annähern

**In `center_baustein_node.py` integriert**

```
Logik:
  WHILE Distanz > ZIEL_DISTANZ (z.B. 0.35 m):
    → Lese Tiefe aus /camera/depth/image_raw
    → Fahre vorwärts (linear.x)
    → Gleichzeitig: Halte Zentrierung (P-Regler aktiv)
    → Stopp wenn Zieldistanz erreicht
  → Phase 5
```

**Relevante Topics:**
| Topic | Typ | Richtung |
|---|---|---|
| `/camera/depth/image_raw` | `Image` | Subscribe |
| `/baustein_center` | `Point` | Subscribe |
| `/cmd_vel` | `Twist` | Publish |

**Parameter:**
- `target_distance_m`: Zieldistanz zum Baustein (m)
- `approach_speed`: Vorwärtsgeschwindigkeit (m/s)
- `min_safe_distance_m`: Sicherheits-Stopp-Distanz (m)

---

## Phase 5 — Autonomes Greifen (XYZ-Koordinaten)

**Datei:** `limo_mycobot/baustein_auto_grabber.py` (bereits vorhanden, anpassen)

```
Ablauf:
  1. Lese Baustein-Position aus Tiefenbild + YOLO-Center
  2. Transformiere Kamera-Koordinaten → Arm-Koordinaten
     (Kalibrierungsmatrix: camera_to_arm x/y/z Offsets)
  3. Berechne XYZ-Greifpunkt
  4. Führe Greif-Sequenz aus:
       Home → Pre-Grasp → Grasp-Position → Greifer schließen → Lift
  5. Publiziere Erfolg-Signal
```

**Greif-Sequenz (Arm-Winkel, aus mycobot_gripper_node.py):**
| Schritt | Bezeichnung | Winkel [°] |
|---|---|---|
| 1 | Home | [0, -20, 20, 0, 0, 0] |
| 2 | Pre-Grasp | [-35, -35, 45, 0, 0, 0] |
| 3 | Grasp | [-35, -52, 62, 0, 0, 0] |
| 4 | Greifer schließen | — |
| 5 | Lift | [-35, -20, 35, 0, 0, 0] |

**Koordinaten-Transformation:**
```
Kamera (u, v, depth)  →  3D-Kamerakoordinaten (X_cam, Y_cam, Z_cam)
                      →  Arm-Koordinaten (X_arm, Y_arm, Z_arm)
                         (+ Offset-Kalibrierung)
```

---

## Haupt-Orchestrator (Zustands-Maschine)

**Neue Datei:** `limo_navigation/autonomous_grasp_controller.py`

```
Zustände:
  IDLE
    ↓
  NAVIGATING_TO_POINT     (Phase 1: Nav2)
    ↓
  SEARCHING_FOR_BLOCK     (Phase 2: Rotation + YOLO)
    ↓
  CENTERING_BLOCK         (Phase 3: P-Regler Ausrichtung)
    ↓
  APPROACHING_BLOCK       (Phase 4: Vorfahren + Zentrierung)
    ↓
  GRASPING                (Phase 5: XYZ Greif-Sequenz)
    ↓
  SUCCESS  /  ERROR
```

**Übergangsbedingungen:**
| Von → Nach | Bedingung |
|---|---|
| IDLE → NAVIGATING | Start-Signal empfangen |
| NAVIGATING → SEARCHING | Nav2 meldet Erfolg |
| SEARCHING → CENTERING | `/baustein_detected` = True |
| CENTERING → APPROACHING | `\|offset\|` < Threshold |
| APPROACHING → GRASPING | Distanz < Zieldistanz |
| GRASPING → SUCCESS | Greif-Sequenz abgeschlossen |
| Beliebig → ERROR | Timeout / Fehler |

---

## Zu erstellende Dateien

| Datei | Beschreibung | Priorität |
|---|---|---|
| `config/grasp_scenario.yaml` | Alle Parameter zentral | 1 |
| `autonomous_grasp_controller.py` | Zustands-Maschine | 2 |
| `search_spin_node.py` | Rotations-Suchlauf | 3 |
| `center_baustein_node.py` | Zentrierung + Annähern | 4 |

**Zu erweitern:**
| Datei | Erweiterung |
|---|---|
| `baustein_auto_grabber.py` | ROS2-kompatibel machen oder Bridge nutzen |
| `pickplace_navigator.py` | Zielpunkt aus YAML laden |

---

## ROS1/ROS2 Bridge-Strategie

Da YOLO und MyCobot noch in ROS1 implementiert sind:

```
Option A — ros1_bridge (Empfohlen für schnellen Start):
  ROS2 Controller  ←→  ros1_bridge  ←→  ROS1 YOLO / MyCobot

Option B — Vollständiger ROS2-Port:
  Alle Nodes auf ROS2 migrieren
  Mehr Aufwand, langfristig sauberer
```

---

## Konfigurations-Datei (Vorschau)

**`config/grasp_scenario.yaml`:**
```yaml
navigation:
  target_x: -0.49
  target_y: 0.00
  target_yaw: 0.0

search_spin:
  angular_speed: 0.3        # rad/s
  detection_pause: 0.5      # s
  max_rotation_deg: 360

centering:
  center_threshold_px: 20
  kp_angular: 0.003
  image_width_px: 640

approach:
  target_distance_m: 0.35
  approach_speed: 0.1       # m/s
  min_safe_distance_m: 0.15

arm_calibration:
  camera_to_arm_x: 0.0     # Kalibrierung erforderlich
  camera_to_arm_y: 0.0
  camera_to_arm_z: 0.0
```

---

## Kalibrierungsschritte (vor dem Betrieb)

| Schritt | Aufgabe | Tool |
|---|---|---|
| 1 | Kamera → Arm Offsets messen | Manuell + `keyboard_control.py` |
| 2 | YOLO Greifdistanz testen | `yolo_baustein_publisher.py` |
| 3 | Arm-Winkel für Greif-Sequenz einfahren | `keyboard_control.py` |
| 4 | Rotationsgeschwindigkeit kalibrieren | `search_spin_node.py` (Test) |
| 5 | Zieldistanz Annähern feintunen | Phase 4 Einzeltest |

---

## Implementierungs-Reihenfolge

```
Schritt 1:  config/grasp_scenario.yaml erstellen
Schritt 2:  search_spin_node.py implementieren + testen
Schritt 3:  center_baustein_node.py implementieren + testen
Schritt 4:  baustein_auto_grabber.py anpassen/bridgen
Schritt 5:  autonomous_grasp_controller.py (Zustands-Maschine)
Schritt 6:  Einzelphasen testen
Schritt 7:  Gesamtablauf testen
```

---

*Erstellt: 2026-05-15*
