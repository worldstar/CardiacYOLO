"""Model manager for loading and managing YOLO models."""

import logging
from pathlib import Path
from typing import Optional, Dict, List

logger = logging.getLogger("cardiacyolo")

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "models"

# Available model versions and their default filenames
SUPPORTED_MODELS = {
    "YOLOv26": "yolov26s_dataset5_ME-T_mAP50.pt",  # Default - best general performance
    "YOLOv9": "yolov9_cardiac.pt",
}

DEFAULT_MODEL = "YOLOv26"


class ModelManager:
    """Manages YOLO model loading and switching."""

    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = Path(models_dir) if models_dir else MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.current_model = None
        self.current_model_name = None
        self._loaded_models: Dict[str, object] = {}

    def list_available_models(self) -> List[str]:
        """List models that are physically available in the models directory."""
        available = []
        for model_name, filename in SUPPORTED_MODELS.items():
            if (self.models_dir / filename).exists():
                available.append(model_name)
        return available

    def get_model_path(self, model_name: str) -> Path:
        """Get the file path for a given model."""
        if model_name not in SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model: {model_name}")
        return self.models_dir / SUPPORTED_MODELS[model_name]

    def load_model(self, model_name: str = DEFAULT_MODEL):
        """Load a YOLO model by name. Caches loaded models."""
        if model_name in self._loaded_models:
            self.current_model = self._loaded_models[model_name]
            self.current_model_name = model_name
            logger.info(f"Switched to cached model: {model_name}")
            return self.current_model

        model_path = self.get_model_path(model_name)
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                f"Please place your trained {model_name} model at this location."
            )

        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise ImportError(
                "ultralytics package is not installed. "
                "Install with: pip install ultralytics"
            ) from exc

        logger.info(f"Loading model: {model_name} from {model_path}")
        model = YOLO(str(model_path))

        self._loaded_models[model_name] = model
        self.current_model = model
        self.current_model_name = model_name
        logger.info(f"Successfully loaded {model_name}")
        return model

    def get_current_model(self):
        """Return the currently loaded model."""
        if self.current_model is None:
            self.load_model(DEFAULT_MODEL)
        return self.current_model

    def is_gpu_available(self) -> bool:
        """Check if CUDA GPU is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    def get_device_info(self) -> str:
        """Return a human-readable description of the inference device."""
        try:
            import torch
            if torch.cuda.is_available():
                return f"GPU: {torch.cuda.get_device_name(0)}"
            return "CPU (slower, but works on any hardware)"
        except ImportError:
            return "Unknown (PyTorch not installed)"
