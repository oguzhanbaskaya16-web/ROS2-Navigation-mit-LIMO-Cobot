
# 🔄 Modell weiter trainieren (Fine-Tuning)

Ein bestehendes YOLO-Modell kann jederzeit weiter verbessert werden, indem neue Trainingsdaten hinzugefügt und das Training fortgesetzt wird.

---

## 📷 1. Neue Bilder hinzufügen

Neue Bilder werden in den Trainingsordner eingefügt:

```

images/train/

```

👉 Wichtig:
- unterschiedliche **Perspektiven**
- verschiedene **Lichtverhältnisse**
- unterschiedliche **Hintergründe**

---

## 🏷️ 2. Bilder labeln

Die neuen Bilder müssen mit einem Annotationstool wie :contentReference[oaicite:0]{index=0} gelabelt werden.

👉 Hinweise:
- **gleiche Klassenbezeichnung** verwenden (z. B. `baustein`)
- Bounding Box möglichst **genau um das Objekt ziehen**
- nicht zu viel Hintergrund einbeziehen

---

## 🔀 3. Trainings- und Validierungsdaten aktualisieren

- ca. **20 % der neuen Daten** in den Validation-Ordner verschieben:
```

images/val/
labels/val/

````

- zugehörige Labels müssen **denselben Namen** haben

---

## 🚀 4. Training fortsetzen (Fine-Tuning)

Das bestehende Modell wird weiter trainiert, anstatt von vorne zu beginnen:

```bash
yolo detect train data=dataset.yaml model="runs/detect/baustein_gpu/weights/best.pt" epochs=50 imgsz=640 device=0 name=baustein_gpu_v2
````

---

## 🧠 Vorteile

* Modell kennt das Objekt bereits → schnelleres Lernen
* bessere **Generalization**
* weniger Fehl-Erkennungen
* Anpassung an reale Bedingungen (z. B. Kamerabild vom LIMO)

---

## ⚠️ Wichtige Hinweise

* Klassenname **nicht ändern**
* jedes Bild muss ein Label haben
* neue Daten sollten sich **von bisherigen unterscheiden**

---

## 💡 Tipp

Statt erneut komplett zu trainieren:

👉 lieber mehrere kurze Trainingsdurchläufe (z. B. +30 Epochs)

---

## ✅ Fazit

Durch das Hinzufügen neuer Bilder und erneutes Training kann das Modell kontinuierlich verbessert werden, ohne von Grund auf neu trainiert werden zu müssen.



