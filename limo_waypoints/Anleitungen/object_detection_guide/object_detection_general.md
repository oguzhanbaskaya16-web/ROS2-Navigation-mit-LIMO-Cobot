
# 📷 Object Detection (ROS1)

---

## 1. Kamera überprüfen

### a) ROS Master starten

- Terminal 1:

```bash
roscore
````

---

### b) Kamera starten

* Terminal 2:

```bash
source ~/agilex_ws/devel_isolated/astra_camera/setup.bash
roslaunch astra_camera dabai_u3.launch
```

---

### c) RViz starten

* Terminal 3:

```bash
rviz
```

---

### d) RViz konfigurieren

👉 Links in der Menüleiste:

* **Fixed Frame** auf:

```text
camera_link
```

---

👉 Kamera-Bild hinzufügen:

* Unten links auf **Add** klicken
* **Image** auswählen
* **By topic** → auswählen:

```text
/camera/color/image_raw
```

* Kamera auswählen → **OK**

---

👉 Ergebnis:

* Kamerabild sollte jetzt sichtbar sein

---

## 2. Fotos aufnehmen

* Mit dem Handy Fotos vom Objekt machen
* Verschiedene Perspektiven aufnehmen

👉 Ziel:

* Datensatz für Objekterkennung erstellen
* Unterschiedliche Winkel & Lichtverhältnisse abdecken

* ca. 100-300 Bilder. Je mehr desto besser. 

## 3. Bilder vorbereiten

👉 Alle Bilder im **.jpg-Format** speichern  
- Falls Bilder ein anderes Format haben (z. B. .png, .heic), in **.jpg umwandeln**

---

👉 Bilder auf dem PC in einem Ordner sammeln:

```text id="gk5h2l"
z.B.:
C:\Users\DeinName\ObjectDetection\images\
```

## 4. LabelImg installieren und starten

```bash
pip install labelImg
````

👉 Programm starten (Beispiel Windows):

```bash id="8n3u4c"
""d:\users\bku\benutzer\appdata(roaming)\python\python38\Scripts\labelImg.exe""
```

---

## 5. Dataset-Struktur erstellen

👉 Ordnerstruktur anlegen:

```text id="1bq4cf"
objekt_dataset/
├── images/
│   ├── train/
│   └── val/
└── labels/
    ├── train/
    └── val/
```

---

## 6. Bilder ablegen

👉 Die vorbereiteten `.jpg` Bilder in folgenden Ordner kopieren:

```text id="pj9n3g"
images/train/
```

---

## 7. Bilder in LabelImg labeln

### a) Bilder öffnen

* **Open Dir** klicken
* Ordner auswählen:

```text id="yb6z0u"
images/train/
```

---

### b) Speicherort festlegen

* **Change Save Dir** klicken
* Ordner auswählen:

```text id="p2j7lx"
labels/train/
```

---

### c) Format einstellen

* Unten links **YOLO Format** auswählen
  👉 (nicht PascalVOC)

---

### d) Bounding Box erstellen

* Erstes Bild öffnet sich automatisch
* Mit **W-Taste** Box um das Objekt ziehen

---

### e) Klasse vergeben

* Klassenname eingeben:

```text id="xk7o8h"
beliebig
```

---

### f) Speichern

* **STRG + S**

---

### g) Nächstes Bild

* Mit **D-Taste** zum nächsten Bild wechseln

---

### h) Wiederholen

* Schritte für alle Bilder durchführen

---

## ⚠️ Wichtige Hinweise beim Labeln

* Bounding Box möglichst **eng um das Objekt ziehen**
* **Nicht zu viel Hintergrund** einbeziehen
* **Objekt vollständig innerhalb der Box**

---

## ✅ Ergebnis

* Für jedes Bild wird automatisch eine `.txt` Datei in dem vorher festgelegten Speicherordner erzeugt
* Diese enthält die YOLO-Labels


## 8. Labels und Bilder überprüfen

👉 Prüfen, ob für jedes Bild eine passende Label-Datei existiert:

```text
images/train/ → .jpg Dateien  
labels/train/ → .txt Dateien  
````

👉 Wichtig:

* Für jedes Bild muss eine `.txt` Datei mit gleichem Namen existieren
* Beispiel:

```text
bild_01.jpg  →  bild_01.txt
```

👉 Falls Dateien fehlen:

* Bild erneut in LabelImg öffnen und labeln

---

## 9. Trainings- und Validierungsdaten aufteilen

👉 Ca. **20 % der Daten** in den Validation-Ordner verschieben

---

### a) Bilder verschieben

```text
images/train/ → images/val/
```

---

### b) Labels verschieben

👉 Die **zugehörigen Labels mit exakt gleichem Namen** ebenfalls verschieben:

```text
labels/train/ → labels/val/
```

---

### c) classes.txt entfernen

👉 Datei löschen:

```text
labels/train/classes.txt
```

👉 Hinweis:

* Wird für das Training nicht benötigt


## 10. dataset.yaml erstellen

👉 Im Ordner `objekt_dataset` eine neue Datei anlegen:

```text
objekt_dataset/dataset.yaml
````

---

👉 Ordnerstruktur sollte jetzt so aussehen:

```text
objekt_dataset/
├── dataset.yaml
├── images/
│   ├── train/
│   └── val/
└── labels/
    ├── train/
    └── val/
```

---

👉 Inhalt der `dataset.yaml`:

```yaml
path: D:/Users/BKU/OguzhanBaskaya/OneDrive - Deutsche Bahn/Pictures/ObjectDetection/baustein_dataset

train: images/train
val: images/val

names:
  0: name_der_klasse
```

---

👉 Hinweise:

* `path` = absoluter Pfad zu deinem Dataset-Ordner
* `train` und `val` = relative Pfade innerhalb des Datasets
* `name_der_klasse` z. B. ersetzen durch:

```yaml
0: baustein
```


## 11. In den Dataset-Ordner wechseln

```bash
cd "PFAD/ZUM/objekt_dataset"
````

👉 Beispiel:

```bash
cd "C:/Users/Username/Pictures/ObjectDetection/objekt_dataset"
```

---

## 12. YOLO Training starten

```bash
& "d:\users\bku\bentuzer\appdata(roaming)\python\python38\Scripts\yolo.exe" detect train data=dataset.yaml model=yolov8s.pt epochs=100 imgsz=640
```

---

👉 Erklärung:

* `data=dataset.yaml` → beschreibt dein Dataset
* `model=yolov8n.pt` → vortrainiertes YOLOv8 Modell
* `epochs=50` → Anzahl Trainingsdurchläufe
* `imgsz=640` → Bildgröße

---

👉 Ergebnis:

* Trainingsordner wird automatisch erstellt (`runs/detect/...`)
* Bestes Modell wird gespeichert (`best.pt`)


## 13. Trainingsergebnisse auswerten

👉 Dein bestes Modell wurde automatisch gespeichert unter:

```text
runs/detect/train/weights/best.pt
````

---

## 📊 Wichtige Kennzahlen erklärt

* **Precision**
  → Gibt an, wie viele der erkannten Objekte tatsächlich korrekt sind
  → Hohe Precision = wenige Fehl-Erkennungen

* **Recall**
  → Gibt an, wie viele der vorhandenen Objekte erkannt wurden
  → Hoher Recall = kaum Objekte werden übersehen

* **mAP@50**
  → Bewertet die Genauigkeit der Erkennung bei einer bestimmten Überlappung zwischen Vorhersage und Realität
  → Wird oft als Hauptkennzahl für Objekterkennung genutzt

* **mAP@50-95**
  → Strengere Bewertung über mehrere Überlappungsschwellen hinweg
  → Zeigt, wie stabil und präzise das Modell wirklich ist

---

## 🧠 Fazit

👉 Diese Kennzahlen helfen dir zu verstehen:

* wie zuverlässig dein Modell Objekte erkennt
* wie genau die Positionen der Objekte bestimmt werden
* wie gut dein Modell für reale Anwendungen geeignet ist

---

## 💡 Verbesserungsmöglichkeiten

* Mehr Trainingsdaten hinzufügen
* Unterschiedliche Perspektiven und Lichtverhältnisse
* Bounding Boxes genauer setzen
* Mehr Trainingsdurchläufe (Epochs) verwenden


## 14. Modell auf Bildern testen

```bash
yolo detect predict model="runs/detect/train/weights/best.pt" source="images/val"
````

👉 Erklärung:

* `model` = Pfad zum trainierten Modell
* `source` = Ordner mit Testbildern
* Ergebnisse werden automatisch unter `runs/detect/predict/` gespeichert

---

## 15. Modell mit Webcam testen

```bash
yolo detect predict model="runs/detect/train/weights/best.pt" source=0 conf=0.7 show=True
```

👉 Erklärung:

* `source=0` = Webcam verwenden
* `conf=0.7` = Mindest-Sicherheit für Erkennung
* `show=True` = Live-Fenster anzeigen

---

## Hinweis zu `conf`

* Niedriger Wert → Modell erkennt mehr Objekte, aber eventuell mehr Fehlerkennungen
* Höherer Wert → Modell erkennt nur sichere Objekte, aber eventuell weniger Objekte


## 19. Ergebnisse anzeigen

👉 Die Ergebnisse der Objekterkennung werden automatisch gespeichert unter:

```text
runs/detect/predict/
````

👉 Dort findest du:

* Bilder mit eingezeichneten Bounding Boxes
* erkannte Objekte inkl. Labels

---

👉 Hinweis:

* Bei mehreren Durchläufen entstehen Ordner wie:

```text
predict/
predict2/
predict3/
```

👉 Der neueste Ordner enthält die aktuellsten Ergebnisse



---

💡 Vorteil:
- keine festen (persönlichen) Pfade mehr  
- direkt GitHub-tauglich  
- für jeden Nutzer verständlich




## 🤖 YOLO Modelle

Für das Training der Objekterkennung können verschiedene YOLO-Modelle verwendet werden. Diese unterscheiden sich hauptsächlich in **Geschwindigkeit** und **Genauigkeit**.

### 📊 Modellübersicht

| Modell       | Beschreibung                                              |
| ------------ | --------------------------------------------------------- |
| `yolov8n.pt` | Sehr schnell, aber geringere Genauigkeit                  |
| `yolov8s.pt` | Guter Kompromiss zwischen Geschwindigkeit und Genauigkeit |
| `yolov8m.pt` | Höhere Genauigkeit, aber langsamer                        |
| `yolov8l.pt` | Sehr genau, benötigt viel Rechenleistung                  |
| `yolov8x.pt` | Maximale Genauigkeit, sehr hohe Rechenanforderungen       |

---

### ⚖️ Auswahl des Modells

Die Wahl des Modells hängt vom Anwendungsfall ab:

* Für **schnelle Ausführung auf dem Roboter (LIMO)** → `yolov8n.pt`
* Für **gute Balance im Training** → `yolov8s.pt`
* Für **maximale Genauigkeit (z. B. Auswertung)** → `yolov8m` oder größer

---

### 💡 Hinweis

Größere Modelle liefern in der Regel bessere Ergebnisse, benötigen jedoch mehr **Rechenleistung** und **Trainingszeit**.

---

### 🧠 Fazit

Für die meisten Anwendungen empfiehlt sich `yolov8s.pt`, da es eine gute Balance zwischen **Leistung** und **Effizienz** bietet.

---

### Effizientere Trainingszeit

Für eine effiziente Trainingszeit wird eine NVIDIA-Grafikkarte mit CUDA-Unterstützung verwendet. Durch die Nutzung der GPU kann die Trainingsdauer im Vergleich zur CPU erheblich reduziert werden.

Hier ist ein sauberer Markdown-Abschnitt für deine Doku 👇

---

## ⚡ Umstellung von CPU auf GPU (YOLO Training)

Für eine deutlich schnellere Trainingszeit wurde das Training von der **CPU** auf die **GPU (NVIDIA CUDA)** umgestellt.

---

### 🔍 1. GPU überprüfen

Zuerst wurde geprüft, ob eine kompatible NVIDIA-Grafikkarte vorhanden ist:

```bash
nvidia-smi
```

👉 Ergebnis:
Die GPU wurde erfolgreich erkannt (z. B. *NVIDIA RTX 2000 Ada*).

---

### ⚠️ 2. Ausgangszustand

Das Training lief zunächst nur über die CPU:

```text
torch-2.x.x+cpu
GPU_mem 0G
```

👉 Nachteil: Sehr lange Trainingszeiten

---

### 🔧 3. CPU-Version von PyTorch entfernen

```bash
python -m pip uninstall torch torchvision torchaudio -y
```

---

### 🔧 4. GPU-Version von PyTorch installieren

```bash
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

👉 Diese Version unterstützt **CUDA (GPU-Beschleunigung)**

---

### 🔍 5. GPU-Nutzung überprüfen

```bash
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

👉 Ergebnis:

```text
True
NVIDIA RTX 2000 Ada Generation Laptop GPU
```

---

### 🚀 6. Training mit GPU starten

```bash
& "d:\users\bku\benutzer\appdata(roaming)\python\python38\Scripts\yolo.exe" detect train data=dataset.yaml model=yolov8s.pt epochs=100 imgsz=640 device=0
```

👉 `device=0` erzwingt die Nutzung der GPU

---

### 📊 7. GPU-Nutzung erkennen

Während des Trainings:

```text
GPU_mem 2G
```

👉 bedeutet: GPU wird aktiv genutzt
❌ `GPU_mem 0G` → CPU wird verwendet

---

### ⚡ Vorteile der GPU-Nutzung

* Deutlich schnellere Trainingszeit
* Effizientere Verarbeitung großer Datensätze
* Bessere Nutzung moderner Hardware

---

### 🧠 Fazit

Durch die Umstellung auf GPU konnte die Trainingsdauer erheblich reduziert werden. Voraussetzung ist eine kompatible **NVIDIA-Grafikkarte mit CUDA-Unterstützung** sowie eine passende PyTorch-Version.

---






















