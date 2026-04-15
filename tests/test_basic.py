"""Basic smoke tests for CardiacYOLO."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest


def test_imports():
    """Verify all main modules can be imported."""
    from cardiacyolo.core.model_manager import ModelManager, SUPPORTED_MODELS, DEFAULT_MODEL
    from cardiacyolo.core.image_processor import ImageProcessor
    from cardiacyolo.core.inference import InferenceEngine, Detection, InferenceResult
    from cardiacyolo.core.report_generator import ReportGenerator
    from cardiacyolo.data.database import Database
    from cardiacyolo.data.settings import Settings, DEFAULT_SETTINGS

    assert DEFAULT_MODEL == "YOLOv26"
    assert "YOLOv26" in SUPPORTED_MODELS


def test_default_model_is_yolov26():
    """The default model must be YOLOv26 (best general performance)."""
    from cardiacyolo.core.model_manager import DEFAULT_MODEL
    assert DEFAULT_MODEL == "YOLOv26"


def test_image_processor_format_check():
    """Test image format validation."""
    from cardiacyolo.core.image_processor import ImageProcessor

    assert ImageProcessor.is_supported("test.jpg")
    assert ImageProcessor.is_supported("test.png")
    assert ImageProcessor.is_supported("test.dcm")
    assert ImageProcessor.is_supported("test.dicom")
    assert not ImageProcessor.is_supported("test.txt")
    assert not ImageProcessor.is_supported("test.pdf")

    assert ImageProcessor.is_dicom("test.dcm")
    assert ImageProcessor.is_dicom("test.dicom")
    assert not ImageProcessor.is_dicom("test.jpg")


def test_settings_defaults():
    """Test settings load with sensible defaults."""
    import tempfile
    from cardiacyolo.data.settings import Settings

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        settings = Settings(settings_path=tmp.name)

    assert settings.get("default_model") == "YOLOv26"
    assert 0.0 <= settings.get("confidence_threshold") <= 1.0
    assert 0.0 <= settings.get("iou_threshold") <= 1.0


def test_database_creation():
    """Test that the database initializes correctly."""
    import tempfile
    from cardiacyolo.data.database import Database

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(db_path=db_path)
        assert db_path.exists()

        db.log_action("test_action", {"key": "value"})
        history = db.get_prediction_history(limit=10)
        assert isinstance(history, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
