"""Image preprocessing and DICOM handling."""

import logging
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger("cardiacyolo")

SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".dcm", ".dicom"}


class ImageProcessor:
    """Handles loading and preprocessing of medical images."""

    @staticmethod
    def is_supported(file_path: str) -> bool:
        """Check if the file extension is supported."""
        return Path(file_path).suffix.lower() in SUPPORTED_FORMATS

    @staticmethod
    def is_dicom(file_path: str) -> bool:
        """Check if the file is a DICOM file."""
        return Path(file_path).suffix.lower() in {".dcm", ".dicom"}

    @staticmethod
    def load_image(file_path: str) -> Tuple[np.ndarray, dict]:
        """
        Load an image from disk. Returns (image_array, metadata_dict).

        Image is returned as a BGR uint8 numpy array (OpenCV format).
        Metadata may include DICOM tags if applicable.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {file_path}")

        if not ImageProcessor.is_supported(file_path):
            raise ValueError(f"Unsupported file format: {path.suffix}")

        if ImageProcessor.is_dicom(file_path):
            return ImageProcessor._load_dicom(file_path)
        return ImageProcessor._load_standard(file_path)

    @staticmethod
    def _load_standard(file_path: str) -> Tuple[np.ndarray, dict]:
        """Load a standard image (JPG/PNG/TIFF/BMP)."""
        try:
            import cv2
        except ImportError as exc:
            raise ImportError("opencv-python is required") from exc

        image = cv2.imread(file_path, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Failed to load image: {file_path}")

        metadata = {
            "filename": Path(file_path).name,
            "format": Path(file_path).suffix.lower(),
            "shape": image.shape,
            "is_dicom": False,
        }
        return image, metadata

    @staticmethod
    def _load_dicom(file_path: str) -> Tuple[np.ndarray, dict]:
        """Load a DICOM file and convert to BGR numpy array."""
        try:
            import pydicom
            import cv2
        except ImportError as exc:
            raise ImportError("pydicom and opencv-python are required for DICOM") from exc

        ds = pydicom.dcmread(file_path)
        pixel_array = ds.pixel_array

        # Normalize to 0-255 uint8
        if pixel_array.dtype != np.uint8:
            pixel_array = pixel_array.astype(np.float32)
            p_min, p_max = pixel_array.min(), pixel_array.max()
            if p_max > p_min:
                pixel_array = (pixel_array - p_min) / (p_max - p_min) * 255.0
            pixel_array = pixel_array.astype(np.uint8)

        # Convert to 3-channel BGR
        if pixel_array.ndim == 2:
            image = cv2.cvtColor(pixel_array, cv2.COLOR_GRAY2BGR)
        elif pixel_array.ndim == 3 and pixel_array.shape[-1] == 3:
            image = cv2.cvtColor(pixel_array, cv2.COLOR_RGB2BGR)
        else:
            image = pixel_array

        # Extract de-identified metadata
        metadata = {
            "filename": Path(file_path).name,
            "format": ".dcm",
            "shape": image.shape,
            "is_dicom": True,
            "modality": getattr(ds, "Modality", "Unknown"),
            "study_date": getattr(ds, "StudyDate", "Unknown"),
            "manufacturer": getattr(ds, "Manufacturer", "Unknown"),
        }
        return image, metadata

    @staticmethod
    def validate_image(image: np.ndarray) -> Optional[str]:
        """Validate image quality. Returns None if OK, error message otherwise."""
        if image is None or image.size == 0:
            return "Image is empty"
        if image.ndim < 2:
            return "Image has invalid dimensions"
        h, w = image.shape[:2]
        if h < 64 or w < 64:
            return f"Image too small ({w}x{h}). Minimum: 64x64"
        if h > 8192 or w > 8192:
            return f"Image too large ({w}x{h}). Maximum: 8192x8192"
        return None
