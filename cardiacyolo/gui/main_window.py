"""Main application window for CardiacYOLO."""

import logging
from pathlib import Path
from typing import Optional

import numpy as np

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QToolBar, QPushButton,
    QComboBox, QLabel, QFileDialog, QMessageBox, QStatusBar, QSplitter,
    QProgressBar
)

from cardiacyolo.gui.image_viewer import ImageViewer
from cardiacyolo.gui.results_panel import ResultsPanel
from cardiacyolo.gui.settings_dialog import SettingsDialog
from cardiacyolo.core.model_manager import ModelManager, SUPPORTED_MODELS, DEFAULT_MODEL
from cardiacyolo.core.image_processor import ImageProcessor
from cardiacyolo.core.inference import InferenceEngine, InferenceResult
from cardiacyolo.core.report_generator import ReportGenerator
from cardiacyolo.data.database import Database
from cardiacyolo.data.settings import Settings

logger = logging.getLogger("cardiacyolo")


class InferenceWorker(QThread):
    """Background worker for running YOLO inference without blocking the UI."""

    finished = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, engine, image, model_name, conf, iou):
        super().__init__()
        self.engine = engine
        self.image = image
        self.model_name = model_name
        self.conf = conf
        self.iou = iou

    def run(self):
        try:
            result = self.engine.predict(
                image=self.image,
                model_name=self.model_name,
                confidence_threshold=self.conf,
                iou_threshold=self.iou,
            )
            self.finished.emit(result)
        except Exception as e:
            logger.exception("Inference failed")
            self.failed.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CardiacYOLO - Valvular Regurgitation Detection")
        self.resize(1280, 800)

        self.settings = Settings()
        self.database = Database()
        self.model_manager = ModelManager()
        self.inference_engine = InferenceEngine(self.model_manager)

        self.current_image: Optional[np.ndarray] = None
        self.current_image_path: Optional[str] = None
        self.current_metadata: dict = {}
        self.current_result: Optional[InferenceResult] = None
        self.worker: Optional[InferenceWorker] = None

        self._init_ui()
        self._init_menu()
        self._update_status_bar()
        self.database.log_action("app_started")

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toolbar
        toolbar = self._create_toolbar()
        self.addToolBar(toolbar)

        # Main content area: image viewer + results panel
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.image_viewer = ImageViewer()
        self.image_viewer.image_dropped.connect(self.load_image)
        splitter.addWidget(self.image_viewer)

        self.results_panel = ResultsPanel()
        splitter.addWidget(self.results_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([900, 380])

        main_layout.addWidget(splitter, stretch=1)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # indeterminate
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _create_toolbar(self) -> QToolBar:
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)

        # Open image button
        open_btn = QPushButton("📂 Open Image")
        open_btn.clicked.connect(self.open_image_dialog)
        toolbar.addWidget(open_btn)

        toolbar.addSeparator()

        # Model selector
        toolbar.addWidget(QLabel("  Model: "))
        self.model_combo = QComboBox()
        for model in SUPPORTED_MODELS.keys():
            self.model_combo.addItem(model)
        # Set default to YOLOv26
        idx = self.model_combo.findText(DEFAULT_MODEL)
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)
        toolbar.addWidget(self.model_combo)

        toolbar.addSeparator()

        # Analyze button
        self.analyze_btn = QPushButton("🔍 Analyze")
        self.analyze_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #1f4e79;
                color: white;
                font-weight: bold;
                padding: 6px 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #2c5f8d; }
            QPushButton:disabled { background-color: #cccccc; color: #888888; }
            """
        )
        self.analyze_btn.clicked.connect(self.run_analysis)
        self.analyze_btn.setEnabled(False)
        toolbar.addWidget(self.analyze_btn)

        toolbar.addSeparator()

        # Export buttons
        self.export_pdf_btn = QPushButton("📄 Export PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        self.export_pdf_btn.setEnabled(False)
        toolbar.addWidget(self.export_pdf_btn)

        self.export_csv_btn = QPushButton("📊 Export CSV")
        self.export_csv_btn.clicked.connect(self.export_csv)
        self.export_csv_btn.setEnabled(False)
        toolbar.addWidget(self.export_csv_btn)

        return toolbar

    def _init_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open Image...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_image_dialog)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        export_pdf_action = QAction("Export &PDF Report...", self)
        export_pdf_action.triggered.connect(self.export_pdf)
        file_menu.addAction(export_pdf_action)

        export_csv_action = QAction("Export &CSV...", self)
        export_csv_action.triggered.connect(self.export_csv)
        file_menu.addAction(export_csv_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("&Edit")
        settings_action = QAction("&Settings...", self)
        settings_action.triggered.connect(self.open_settings)
        edit_menu.addAction(settings_action)

        help_menu = menubar.addMenu("&Help")
        about_action = QAction("&About CardiacYOLO", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _update_status_bar(self):
        device = self.model_manager.get_device_info()
        available = self.model_manager.list_available_models()
        if available:
            self.status_bar.showMessage(
                f"Ready | Device: {device} | Available models: {', '.join(available)}"
            )
        else:
            self.status_bar.showMessage(
                f"Ready | Device: {device} | ⚠ No model files found in models/ directory"
            )

    def open_image_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Medical Image",
            "",
            "Medical Images (*.dcm *.dicom *.jpg *.jpeg *.png *.tiff *.tif *.bmp);;All Files (*)",
        )
        if path:
            self.load_image(path)

    def load_image(self, file_path: str):
        """Load and display an image from disk."""
        try:
            if not ImageProcessor.is_supported(file_path):
                QMessageBox.warning(
                    self,
                    "Unsupported Format",
                    f"The selected file format is not supported.\n\n"
                    f"Supported formats: DICOM, JPG, PNG, TIFF, BMP"
                )
                return

            image, metadata = ImageProcessor.load_image(file_path)
            error = ImageProcessor.validate_image(image)
            if error:
                QMessageBox.warning(self, "Invalid Image", error)
                return

            self.current_image = image
            self.current_image_path = file_path
            self.current_metadata = metadata
            self.image_viewer.set_image(image)
            self.results_panel.clear()

            self.analyze_btn.setEnabled(True)
            self.export_pdf_btn.setEnabled(False)
            self.export_csv_btn.setEnabled(False)
            self.current_result = None

            self.status_bar.showMessage(
                f"Loaded: {Path(file_path).name} ({image.shape[1]}x{image.shape[0]})"
            )
            self.database.log_action(
                "image_loaded", {"path": file_path, "shape": list(image.shape)}
            )
        except Exception as e:
            logger.exception("Failed to load image")
            QMessageBox.critical(
                self, "Load Error", f"Failed to load image:\n\n{str(e)}"
            )

    def run_analysis(self):
        """Start inference in a background thread."""
        if self.current_image is None:
            return

        model_name = self.model_combo.currentText()

        # Check if model file exists
        try:
            model_path = self.model_manager.get_model_path(model_name)
            if not model_path.exists():
                QMessageBox.warning(
                    self,
                    "Model Not Found",
                    f"The model file for {model_name} was not found at:\n\n"
                    f"{model_path}\n\n"
                    f"Please place your trained model in the 'models/' directory."
                )
                return
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Model", str(e))
            return

        conf = self.settings.get("confidence_threshold", 0.5)
        iou = self.settings.get("iou_threshold", 0.45)

        self.analyze_btn.setEnabled(False)
        self.progress_bar.show()
        self.status_bar.showMessage(
            f"Running inference with {model_name}..."
        )

        self.worker = InferenceWorker(
            self.inference_engine,
            self.current_image,
            model_name,
            conf,
            iou,
        )
        self.worker.finished.connect(self._on_inference_finished)
        self.worker.failed.connect(self._on_inference_failed)
        self.worker.start()

    def _on_inference_finished(self, result: InferenceResult):
        """Handle successful inference results."""
        self.progress_bar.hide()
        self.analyze_btn.setEnabled(True)
        self.current_result = result

        # Show annotated image if available
        if result.annotated_image is not None:
            self.image_viewer.set_image(result.annotated_image)

        self.results_panel.display_results(result)
        self.export_pdf_btn.setEnabled(True)
        self.export_csv_btn.setEnabled(True)

        self.status_bar.showMessage(
            f"Done: {result.num_detections()} detection(s) "
            f"in {result.inference_time_ms:.1f}ms"
        )

        if self.settings.get("auto_save_results", True):
            try:
                self.database.save_prediction(
                    image_filename=Path(self.current_image_path).name,
                    image_path=self.current_image_path,
                    model_name=result.model_name,
                    confidence_threshold=self.settings.get("confidence_threshold", 0.5),
                    iou_threshold=self.settings.get("iou_threshold", 0.45),
                    num_detections=result.num_detections(),
                    inference_time_ms=result.inference_time_ms,
                    results_dict=result.to_dict(),
                )
            except Exception as e:
                logger.warning(f"Failed to save prediction to database: {e}")

    def _on_inference_failed(self, error_msg: str):
        """Handle inference errors."""
        self.progress_bar.hide()
        self.analyze_btn.setEnabled(True)
        self.status_bar.showMessage("Inference failed")
        QMessageBox.critical(
            self,
            "Inference Error",
            f"Failed to run inference:\n\n{error_msg}"
        )

    def export_pdf(self):
        """Export results as PDF report."""
        if self.current_result is None:
            return

        default_dir = self.settings.get(
            "output_directory", str(Path.home())
        )
        Path(default_dir).mkdir(parents=True, exist_ok=True)

        default_name = (
            f"CardiacYOLO_Report_{Path(self.current_image_path).stem}.pdf"
        )
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            str(Path(default_dir) / default_name),
            "PDF Files (*.pdf)",
        )
        if not path:
            return

        try:
            ReportGenerator.export_pdf(
                self.current_result,
                output_path=path,
                image_filename=Path(self.current_image_path).name,
                annotated_image=self.current_result.annotated_image,
                patient_info=(
                    {k: v for k, v in self.current_metadata.items()
                     if k in ("modality", "study_date", "manufacturer")}
                    if self.current_metadata.get("is_dicom") else None
                ),
            )
            QMessageBox.information(
                self, "Export Successful",
                f"PDF report saved to:\n\n{path}"
            )
            self.database.log_action("export_pdf", {"path": path})
        except Exception as e:
            logger.exception("PDF export failed")
            QMessageBox.critical(
                self, "Export Error", f"Failed to export PDF:\n\n{str(e)}"
            )

    def export_csv(self):
        """Export results as CSV."""
        if self.current_result is None:
            return

        default_dir = self.settings.get(
            "output_directory", str(Path.home())
        )
        Path(default_dir).mkdir(parents=True, exist_ok=True)

        default_name = (
            f"CardiacYOLO_Results_{Path(self.current_image_path).stem}.csv"
        )
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save CSV File",
            str(Path(default_dir) / default_name),
            "CSV Files (*.csv)",
        )
        if not path:
            return

        try:
            ReportGenerator.export_csv(
                self.current_result,
                output_path=path,
                image_filename=Path(self.current_image_path).name,
            )
            QMessageBox.information(
                self, "Export Successful",
                f"CSV file saved to:\n\n{path}"
            )
            self.database.log_action("export_csv", {"path": path})
        except Exception as e:
            logger.exception("CSV export failed")
            QMessageBox.critical(
                self, "Export Error", f"Failed to export CSV:\n\n{str(e)}"
            )

    def open_settings(self):
        dialog = SettingsDialog(self.settings, self)
        dialog.exec()

    def show_about(self):
        QMessageBox.about(
            self,
            "About CardiacYOLO",
            "<h2>CardiacYOLO v1.0</h2>"
            "<p><b>AI-Powered Valvular Regurgitation Detection</b></p>"
            "<p>A research and clinical decision support tool for "
            "detecting valvular regurgitation in color Doppler echocardiographic "
            "images using YOLO (v9-v26) deep learning models.</p>"
            "<p><b>Default model:</b> YOLOv26 (best general performance)</p>"
            "<p><b>Authors:</b> Chen, Kao, Weng</p>"
            "<p><b>License:</b> MIT</p>"
            "<hr>"
            "<p><i>⚠ This software is NOT a substitute for professional "
            "medical judgment. All results should be verified by qualified "
            "medical professionals.</i></p>"
        )

    def closeEvent(self, event):
        self.database.log_action("app_closed")
        event.accept()
