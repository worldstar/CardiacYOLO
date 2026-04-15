# CardiacYOLO

**AI-Powered Valvular Regurgitation Detection in Echocardiography**

CardiacYOLO is a user-friendly, standalone desktop application designed to assist cardiologists and sonographers in detecting valvular regurgitation from color Doppler echocardiographic images. Powered by state-of-the-art YOLO (v9-v26) object detection models, with **YOLOv26** as the default for best general performance.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Mac%20%7C%20Linux-lightgrey.svg)]()

---

## Features

- **Drag-and-Drop Interface**: Simply drag medical images into the application
- **Multi-Model Support**: Choose between YOLOv9 and YOLOv26 (default)
- **Real-Time Inference**: Process images in 5-30 seconds (depending on hardware)
- **DICOM Support**: Native support for DICOM medical image format
- **Visual Results**: Bounding boxes with confidence scores and class labels
- **Report Generation**: Export results as PDF or CSV
- **Local Database**: SQLite-based history of all predictions
- **GPU Acceleration**: Automatic CUDA detection (NVIDIA GPUs)
- **Privacy First**: All data stays on your computer—no cloud required

---

## Installation

### From Source (Developers)

Requirements:
- Python 3.10 or higher
- pip

```bash
# Clone the repository
git clone https://github.com/yourusername/CardiacYOLO.git
cd CardiacYOLO

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

---

## Quick Start Guide

### 1. Place Your Trained Model

Place your trained **YOLOv26** model file in the `models/` directory:

```
CardiacYOLO/
└── models/
    └── yolov26_cardiac.pt   ← Your trained model here
```

The application will automatically load this model on startup.

### 2. Launch the Application

- **Windows**: Start Menu → CardiacYOLO
- **Mac**: Applications → CardiacYOLO
- **Linux**: Run the AppImage
- **From source**: `python main.py`

### 3. Analyze an Image

1. **Upload Image**: Drag-and-drop a DICOM/JPG/PNG image, or click "Open Image"
2. **Select Model**: Choose YOLOv26 (default) or another version from the dropdown
3. **Adjust Settings** (optional): Change confidence threshold or NMS IoU
4. **Run Prediction**: Click "Analyze" button
5. **View Results**: Bounding boxes and confidence scores appear on the image
6. **Export Report**: Click "Export PDF" or "Export CSV" to save results

---

## Project Structure

```
CardiacYOLO/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── LICENSE                    # MIT license
├── .gitignore
├── cardiacyolo/               # Main package
│   ├── app.py                 # QApplication setup
│   ├── gui/                   # GUI components
│   │   ├── main_window.py     # Main window
│   │   ├── image_viewer.py    # Image display widget
│   │   ├── results_panel.py   # Results display panel
│   │   └── settings_dialog.py # Settings dialog
│   ├── core/                  # Business logic
│   │   ├── inference.py       # YOLO inference engine
│   │   ├── model_manager.py   # Model loading & management
│   │   ├── image_processor.py # Image preprocessing
│   │   └── report_generator.py # PDF/CSV reports
│   ├── data/                  # Data layer
│   │   ├── database.py        # SQLite operations
│   │   └── settings.py        # Settings management
│   └── utils/                 # Utilities
│       └── logger.py          # Logging
├── models/                    # Trained YOLO models (place .pt files here)
│   └── README.md              # Model placement instructions
├── assets/                    # Icons and images
├── tests/                     # Unit tests
└── docs/                      # Documentation
    └── SPECIFICATION_AND_DEVELOPMENT_PLAN.md
```

---

## System Requirements

### Minimum
- **OS**: Windows 7+, macOS 10.14+, Ubuntu 18.04+
- **RAM**: 4 GB
- **Storage**: 500 MB + 2 GB for models
- **Python**: 3.10+ (if running from source)

### Recommended
- **OS**: Windows 10+, macOS 11+, Ubuntu 20.04+
- **RAM**: 8 GB
- **Storage**: SSD with 5 GB free
- **GPU**: NVIDIA GPU with CUDA support (3-5x faster inference)

---

## Supported Models

| Model | Speed | Accuracy | Best For |
|-------|-------|----------|----------|
| YOLOv9 | Fast | Good | Real-time inference, lower-end hardware |
| **YOLOv26** ⭐ | Medium | **Highest** | **Default — best general performance** |

---

## Supported Image Formats

- **DICOM**: `.dcm`, `.dicom` (with full metadata support)
- **Standard**: `.jpg`, `.jpeg`, `.png`, `.tiff`, `.tif`, `.bmp`

---

## Disclaimer

⚠️ **CardiacYOLO is a research and clinical decision support tool. It is NOT a substitute for professional medical judgment.** All results should be verified by qualified medical professionals. This software has not been approved by the FDA for clinical diagnosis.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

---

## Authors

- **Shih-Hsin Chen** — Tamkang University, Taiwan
- **Ting-Yi Kao** — Chang Gung University, Taiwan / NEOMA Business School, France
- **Ken-Pen Weng** — Kaohsiung Veterans General Hospital, Taiwan

---

## Acknowledgments

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) for the YOLO framework
- The open-source medical imaging community
- All the cardiologists and sonographers who provided feedback during development

---

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/CardiacYOLO/issues)
- **Documentation**: See the [docs/](docs/) folder
- **Email**: your.email@example.com
