"""Settings dialog."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QDoubleSpinBox, QCheckBox,
    QLineEdit, QPushButton, QHBoxLayout, QFileDialog, QDialogButtonBox,
    QLabel
)


class SettingsDialog(QDialog):
    """Application settings dialog."""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self._init_ui()
        self._load_values()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.0, 1.0)
        self.confidence_spin.setSingleStep(0.05)
        self.confidence_spin.setDecimals(2)
        form.addRow("Confidence Threshold:", self.confidence_spin)

        self.iou_spin = QDoubleSpinBox()
        self.iou_spin.setRange(0.0, 1.0)
        self.iou_spin.setSingleStep(0.05)
        self.iou_spin.setDecimals(2)
        form.addRow("NMS IoU Threshold:", self.iou_spin)

        self.gpu_check = QCheckBox("Use GPU acceleration (if available)")
        form.addRow("", self.gpu_check)

        self.auto_save_check = QCheckBox("Auto-save results to database")
        form.addRow("", self.auto_save_check)

        # Output directory
        output_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_output_dir)
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(browse_btn)
        form.addRow("Output Directory:", output_layout)

        layout.addLayout(form)

        info = QLabel(
            "Settings are saved to: ~/.cardiacyolo/settings.json"
        )
        info.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(info)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.RestoreDefaults
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(
            QDialogButtonBox.StandardButton.RestoreDefaults
        ).clicked.connect(self._restore_defaults)
        layout.addWidget(buttons)

    def _load_values(self):
        self.confidence_spin.setValue(self.settings.get("confidence_threshold", 0.5))
        self.iou_spin.setValue(self.settings.get("iou_threshold", 0.45))
        self.gpu_check.setChecked(self.settings.get("use_gpu", True))
        self.auto_save_check.setChecked(self.settings.get("auto_save_results", True))
        self.output_dir_edit.setText(self.settings.get("output_directory", ""))

    def _browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", self.output_dir_edit.text()
        )
        if directory:
            self.output_dir_edit.setText(directory)

    def _restore_defaults(self):
        self.settings.reset()
        self._load_values()

    def save_settings(self):
        """Persist current dialog values to the settings store."""
        self.settings.set("confidence_threshold", self.confidence_spin.value())
        self.settings.set("iou_threshold", self.iou_spin.value())
        self.settings.set("use_gpu", self.gpu_check.isChecked())
        self.settings.set("auto_save_results", self.auto_save_check.isChecked())
        self.settings.set("output_directory", self.output_dir_edit.text())

    def accept(self):
        self.save_settings()
        super().accept()
