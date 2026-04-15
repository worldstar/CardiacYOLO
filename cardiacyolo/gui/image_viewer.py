"""Image viewer widget with drag-and-drop support."""

import logging
from typing import Optional

import numpy as np

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QLabel, QSizePolicy

logger = logging.getLogger("cardiacyolo")


class ImageViewer(QLabel):
    """Widget to display an image with drag-and-drop file loading."""

    image_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(640, 480)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.setStyleSheet(
            """
            QLabel {
                background-color: #f5f5f5;
                border: 2px dashed #c0c0c0;
                border-radius: 8px;
                color: #888888;
                font-size: 16px;
            }
            """
        )
        self._show_placeholder()
        self._current_image: Optional[np.ndarray] = None

    def _show_placeholder(self):
        self.setText(
            "📁 Drag and drop a medical image here\n\n"
            "or click 'Open Image' to browse\n\n"
            "Supported: DICOM (.dcm), JPG, PNG, TIFF, BMP"
        )

    def set_image(self, image: np.ndarray):
        """Display a numpy image array (BGR format from OpenCV)."""
        if image is None:
            self._show_placeholder()
            return

        self._current_image = image
        try:
            import cv2
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        except Exception:
            rgb_image = image

        h, w = rgb_image.shape[:2]
        if rgb_image.ndim == 3:
            ch = rgb_image.shape[2]
            bytes_per_line = ch * w
            qimage = QImage(
                rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
            )
        else:
            qimage = QImage(
                rgb_image.data, w, h, w, QImage.Format.Format_Grayscale8
            )

        pixmap = QPixmap.fromImage(qimage)
        scaled = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(scaled)
        self.setStyleSheet(
            """
            QLabel {
                background-color: #1a1a1a;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            """
        )

    def clear_image(self):
        self._current_image = None
        self.clear()
        self.setStyleSheet(
            """
            QLabel {
                background-color: #f5f5f5;
                border: 2px dashed #c0c0c0;
                border-radius: 8px;
                color: #888888;
                font-size: 16px;
            }
            """
        )
        self._show_placeholder()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._current_image is not None:
            self.set_image(self._current_image)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].isLocalFile():
                event.acceptProposedAction()
                return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            logger.info(f"Image dropped: {file_path}")
            self.image_dropped.emit(file_path)
            event.acceptProposedAction()
