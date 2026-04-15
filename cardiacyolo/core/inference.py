"""YOLO inference engine for cardiac image analysis."""

import logging
import time
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

logger = logging.getLogger("cardiacyolo")


@dataclass
class Detection:
    """A single detection result."""
    class_name: str
    class_id: int
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]


@dataclass
class InferenceResult:
    """Container for inference results."""
    detections: List[Detection] = field(default_factory=list)
    inference_time_ms: float = 0.0
    model_name: str = ""
    image_shape: tuple = (0, 0, 0)
    annotated_image: Optional[np.ndarray] = None

    def num_detections(self) -> int:
        return len(self.detections)

    def to_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "inference_time_ms": self.inference_time_ms,
            "image_shape": list(self.image_shape),
            "num_detections": self.num_detections(),
            "detections": [
                {
                    "class_name": d.class_name,
                    "class_id": d.class_id,
                    "confidence": float(d.confidence),
                    "bbox": [float(x) for x in d.bbox],
                }
                for d in self.detections
            ],
        }


class InferenceEngine:
    """Runs YOLO inference on input images."""

    def __init__(self, model_manager):
        self.model_manager = model_manager

    def predict(
        self,
        image: np.ndarray,
        model_name: Optional[str] = None,
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.45,
    ) -> InferenceResult:
        """Run prediction on a single image."""
        if model_name:
            self.model_manager.load_model(model_name)
        model = self.model_manager.get_current_model()
        current_model_name = self.model_manager.current_model_name

        logger.info(
            f"Running inference: model={current_model_name}, "
            f"conf={confidence_threshold}, iou={iou_threshold}"
        )

        start_time = time.perf_counter()
        results = model.predict(
            source=image,
            conf=confidence_threshold,
            iou=iou_threshold,
            verbose=False,
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        result_obj = InferenceResult(
            inference_time_ms=elapsed_ms,
            model_name=current_model_name,
            image_shape=image.shape,
        )

        if not results:
            return result_obj

        result = results[0]
        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes
            class_names = result.names

            for i in range(len(boxes)):
                xyxy = boxes.xyxy[i].cpu().numpy().tolist()
                conf = float(boxes.conf[i].cpu().numpy())
                cls_id = int(boxes.cls[i].cpu().numpy())
                cls_name = class_names.get(cls_id, f"class_{cls_id}")

                result_obj.detections.append(
                    Detection(
                        class_name=cls_name,
                        class_id=cls_id,
                        confidence=conf,
                        bbox=xyxy,
                    )
                )

        # Generate annotated image with bounding boxes
        try:
            result_obj.annotated_image = result.plot()
        except Exception as e:
            logger.warning(f"Failed to generate annotated image: {e}")

        logger.info(
            f"Inference complete: {result_obj.num_detections()} detections "
            f"in {elapsed_ms:.1f}ms"
        )
        return result_obj
