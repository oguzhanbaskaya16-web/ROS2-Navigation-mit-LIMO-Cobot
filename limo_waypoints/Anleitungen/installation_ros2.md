# ⚙️ Umgebung einrichten

## 1. Ubuntu 20.04 installieren
- In Powershell als Administrator:

```bash
wsl --install -d Ubuntu-20.04
```

---

## 2. Ubuntu aktualisieren
- In Ubuntu:

```bash
sudo apt update
sudo apt upgrade -y
```

---

## 3. ROS2-Repository einrichten

```bash
sudo apt install software-properties-common -y
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
```

```bash
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
```

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

```bash
sudo apt update
```

---

## 4. ROS2 Foxy installieren

```bash
sudo apt install ros-foxy-desktop python3-argcomplete -y
```

---

## 5. ROS2-Umgebung laden

```bash
echo "source /opt/ros/foxy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## 6. Build-Werkzeuge installieren

```bash
sudo apt install python3-colcon-common-extensions -y
```

---

## 7. rosdep initialisieren

```bash
sudo rosdep init
rosdep update
```

---

## 8. Ersten ROS2-Test machen

```bash
ros2 --help
```

---

## 9. Workspace anlegen

Ein ROS2-Workspace ist der Ort, in dem die Pakete liegen.

```bash
mkdir -p ~/krish_ws/src
cd ~/krish_ws
colcon build
source install/setup.bash
```

```bash
echo "source ~/krish_ws/install/setup.bash" >> ~/.bashrc
```

---

## 10. Erstes Python-Paket anlegen

In den `src`-Ordner wechseln:

```bash
cd ~/krish_ws/src
```

```bash
ros2 pkg create --build-type ament_python demo_pkg
```

Nach dem Erstellen des Python-Pakets ergibt sich folgende Struktur:

```bash
krish_ws/
└── src/
    └── demo_pkg/
        ├── demo_pkg/
        │   └── __init__.py
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource/
        └── test/
```

---

## 11. Node schreiben

### 📄 Beispiel-Datei anlegen

```bash
~/krish_ws/src/demo_pkg/demo_pkg/talker.py
```

---

### 🧠 Beispielcode

```python
import rclpy
from rclpy.node import Node

class Talker(Node):
    def __init__(self):
        super().__init__("talker")
        self.timer = self.create_timer(1.0, self.tick)
        self.count = 0

    def tick(self):
        self.get_logger().info(f"Hello {self.count}")
        self.count += 1

def main():
    rclpy.init()
    node = Talker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
```
---

## 12. `setup.py` konfigurieren

Damit `ros2 run` den Node findet, muss man ihn in `entry_points` registrieren.

### Beispiel für `setup.py`

```python
from setuptools import setup
from glob import glob
import os

package_name = 'demo_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        (os.path.join('share', 'ament_index', 'resource_index', 'packages'),
         [os.path.join('resource', package_name)]),
        (os.path.join('share', package_name), ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dein_name',
    maintainer_email='dein_mail',
    description='Demo package',
    license='TODO',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'talker = demo_pkg.talker:main',
        ],
    },
)
```
### 🔍 Wichtiger Eintrag

Entscheidend ist dieser Teil:

```python
entry_points={
    'console_scripts': [
        'talker = demo_pkg.talker:main',
    ],
},
```

Das bedeutet:
- `talker` = Name des Befehls bei `ros2 run`
- `demo_pkg.talker` = Python-Datei `talker.py` im Paket `demo_pkg`
- `main` = Funktion, die beim Start ausgeführt wird


---

## 13. `package.xml` konfigurieren

```xml
<?xml version="1.0"?>
<package format="3">
  <name>demo_pkg</name>
  <version>0.0.1</version>
  <description>Demo package with a talker node</description>

  <maintainer email="you@example.com">krish</maintainer>
  <license>MIT</license>

  <buildtool_depend>ament_python</buildtool_depend>

  <!-- runtime dependencies -->
  <exec_depend>rclpy</exec_depend>
  <exec_depend>std_msgs</exec_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

---

## 14. Paket builden

```bash
cd ~/krish_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

---

## 15. Node starten

```bash
ros2 run demo_pkg talker
```

---

## 16. Publisher und Subscriber nutzen

Wenn man echte ROS2-Kommunikation testen will, baut man einen **Publisher** und einen **Subscriber** mit einem gemeinsamen Topic, zum Beispiel `/chatter`.

Das entspricht dem ROS2-Grundprinzip:

👉 **Publisher → Topic → Subscriber**

Die Konzepte und Tutorials sind Teil der offiziellen ROS2-Dokumentation.