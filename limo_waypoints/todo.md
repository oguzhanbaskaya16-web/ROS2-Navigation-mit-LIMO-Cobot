# TODO: Nav2-Start- und Zielpose kalibrieren

## Aktueller Stand

- Der Roboter faehrt mit direktem `/cmd_vel` geradeaus.
- Hardware, Motoren und Reifen sind deshalb wahrscheinlich nicht das Hauptproblem.
- Das Abweichen passiert eher bei Nav2, also durch Startpose, Zielpose, Map, Costmap oder Zielausrichtung.

Geprueft wurde bereits:

- `/scan` laeuft sauber mit ca. 10 Hz.
- `base_link -> laser_link` funktioniert.
- `odom -> base_link` funktioniert.
- `/map` hat einen Publisher.
- `map -> odom` funktioniert.
- `map -> base_link` funktioniert.
- AMCL ist `active [3]`.
- `/amcl_pose` hat einen Publisher, liefert aber bei `ros2 topic hz /amcl_pose` keine laufenden Daten.
- Die Lokalisierung kann trotzdem ueber TF genutzt werden.

Zuletzt gemessene Startpose:

```text
x = 0.471
y = 0.117
orientation z = -0.030
orientation w = 1.000
```

## Naechster Schritt

Nicht mehr raten, wo "geradeaus" in der Karte ist. Stattdessen eine echte Geradeausfahrt messen und daraus Start- und Endpose ableiten.

### 1. Startpose auslesen

Roboter an die feste Startposition stellen und dann ausfuehren:

```bash
ros2 run tf2_ros tf2_echo map base_link
```

Diese Werte notieren:

```text
START_X =
START_Y =
START_Z =
START_W =
```

Danach mit `STRG + C` abbrechen.

### 2. Roboter geradeaus fahren lassen

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{
linear: {x: 0.15, y: 0.0, z: 0.0},
angular: {x: 0.0, y: 0.0, z: 0.0}
}"
```

Nach der gewuenschten Strecke mit `STRG + C` stoppen.

### 3. Endpose auslesen

```bash
ros2 run tf2_ros tf2_echo map base_link
```

Diese Werte notieren:

```text
END_X =
END_Y =
END_Z =
END_W =
```

Danach mit `STRG + C` abbrechen.

### 4. Gemessene Werte fuer Nav2 verwenden

Die gemessene Startpose wird als `/initialpose` gesetzt:

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "{
header: {frame_id: 'map'},
pose: {
  pose: {
    position: {x: START_X, y: START_Y, z: 0.0},
    orientation: {x: 0.0, y: 0.0, z: START_Z, w: START_W}
  },
  covariance: [0.25, 0, 0, 0, 0, 0,
               0, 0.25, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0.0685]
}
}"
```

Die gemessene Endpose wird als Nav2-Ziel gesetzt:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{
pose: {
  header: {frame_id: 'map'},
  pose: {
    position: {x: END_X, y: END_Y, z: 0.0},
    orientation: {x: 0.0, y: 0.0, z: END_Z, w: END_W}
  }
}
}" --feedback
```

## Ziel des Tests

- Wenn Nav2 danach gerade faehrt, waren die vorherigen Zielwerte oder die manuelle RViz-Eingabe das Problem.
- Wenn Nav2 trotzdem abweicht, dann als Naechstes den lila Pfad in RViz und die Nav2-Controller-/Costmap-Parameter pruefen.
