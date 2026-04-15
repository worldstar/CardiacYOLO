# CardiacYOLO Models Directory

Place your trained YOLO model files in this directory.

## Default Model: YOLOv26

The default and recommended model is **YOLOv26**, which provides the best general performance for valvular regurgitation detection.

Place your trained YOLOv26 model file here as:

```
models/yolov26_cardiac.pt
```

## Supported Model Files

| Model | Filename | Required |
|-------|----------|----------|
| **YOLOv26** ⭐ | `yolov26_cardiac.pt` | **Yes (default)** |
| YOLOv22 | `yolov22_cardiac.pt` | Optional |
| YOLOv16 | `yolov16_cardiac.pt` | Optional |
| YOLOv9 | `yolov9_cardiac.pt` | Optional |

The application will automatically detect which models are available and show them in the model selection dropdown.

## File Format

Models should be in PyTorch format (`.pt`) compatible with the [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) framework. These are produced when training a model using:

```python
from ultralytics import YOLO
model = YOLO("yolov26.yaml")  # or yolov26.pt
results = model.train(data="cardiac.yaml", epochs=100)
# Trained model saved at: runs/detect/train/weights/best.pt
```

Copy the `best.pt` file here and rename it to match the expected filename (e.g., `yolov26_cardiac.pt`).

## Model Training Notes

For best results, train your model on:
- **Color Doppler echocardiographic images**
- **Annotated bounding boxes** for valvular regurgitation regions
- Class labels for different regurgitation types (e.g., mitral, aortic, tricuspid, pulmonary)
- A balanced dataset with sufficient examples of each class

## Privacy Notice

Model files stored here may contain learned representations of training data. Do not commit confidential or patient-derived models to public repositories.

This directory is included in `.gitignore` (except for this README).
