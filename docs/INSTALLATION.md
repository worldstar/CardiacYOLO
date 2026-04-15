# CardiacYOLO Installation Guide

## For Doctors and Non-Technical Users

### Windows
1. Download `CardiacYOLO-Setup.exe` from the [Releases page](https://github.com/yourusername/CardiacYOLO/releases)
2. Double-click the installer and follow the wizard
3. Launch from Start Menu → CardiacYOLO
4. On first launch, place your trained model in the `models` folder

### Mac
1. Download `CardiacYOLO.dmg`
2. Open it and drag CardiacYOLO to the Applications folder
3. The first time you open it, right-click → Open (to bypass Gatekeeper)
4. Place your trained model in `~/Library/Application Support/CardiacYOLO/models/`

### Linux
1. Download `CardiacYOLO.AppImage`
2. Make it executable: `chmod +x CardiacYOLO.AppImage`
3. Double-click to run

---

## For Developers (From Source)

### Prerequisites
- Python 3.10 or higher
- pip
- (Optional) NVIDIA GPU with CUDA 11.8+ for GPU acceleration

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/CardiacYOLO.git
cd CardiacYOLO

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. (Optional) Install with CUDA support for GPU acceleration
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# 6. Place your trained model in models/
# e.g., copy your trained YOLOv26 model to:
# CardiacYOLO/models/yolov26_cardiac.pt

# 7. Run the application
python main.py
```

### Running Tests

```bash
pip install pytest pytest-qt
pytest tests/ -v
```

### Building a Standalone Executable

Use PyInstaller to create a standalone executable:

```bash
pip install pyinstaller

# Windows
pyinstaller --noconfirm --windowed --name "CardiacYOLO" \
    --icon assets/icon.ico \
    --add-data "models;models" \
    main.py

# Mac
pyinstaller --noconfirm --windowed --name "CardiacYOLO" \
    --icon assets/icon.icns \
    --add-data "models:models" \
    main.py

# Linux
pyinstaller --noconfirm --windowed --name "CardiacYOLO" \
    --add-data "models:models" \
    main.py
```

The executable will be in `dist/CardiacYOLO/`.

---

## Troubleshooting

### "Model file not found"
- Ensure your trained `.pt` model is placed in the `models/` directory
- File must be named correctly (e.g., `yolov26_cardiac.pt` for YOLOv26)
- Check file permissions

### "PyQt6 not found"
- Reinstall PyQt6: `pip install --upgrade PyQt6`
- On Linux, you may need: `sudo apt-get install python3-pyqt6`

### "CUDA not available" but you have a GPU
- Install the CUDA-enabled version of PyTorch
- Verify with: `python -c "import torch; print(torch.cuda.is_available())"`

### Application crashes on startup
- Check the logs at `~/.cardiacyolo/logs/`
- Run from terminal to see error messages: `python main.py`

### DICOM files won't open
- Ensure pydicom is installed: `pip install pydicom`
- Some DICOM variants (compressed) may need: `pip install pylibjpeg pylibjpeg-libjpeg`

---

## File Locations

CardiacYOLO stores user data in:

| Platform | Location |
|----------|----------|
| Windows | `C:\Users\<username>\.cardiacyolo\` |
| Mac | `~/.cardiacyolo/` |
| Linux | `~/.cardiacyolo/` |

Contents:
- `cardiacyolo.db` - SQLite database (prediction history, audit logs)
- `settings.json` - Application settings
- `logs/` - Application log files
