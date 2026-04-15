"""Panel for displaying inference results."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QFormLayout
)


class ResultsPanel(QWidget):
    """Displays inference results in a table and summary."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Summary group
        summary_group = QGroupBox("Summary")
        summary_layout = QFormLayout()

        self.model_label = QLabel("—")
        self.time_label = QLabel("—")
        self.count_label = QLabel("—")
        self.count_label.setFont(QFont("", 14, QFont.Weight.Bold))

        summary_layout.addRow("Model:", self.model_label)
        summary_layout.addRow("Inference Time:", self.time_label)
        summary_layout.addRow("Detections:", self.count_label)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        # Detections table
        table_group = QGroupBox("Detections")
        table_layout = QVBoxLayout()

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Class", "Confidence", "Bounding Box"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group, stretch=1)

        # Status / hint
        self.status_label = QLabel("No predictions yet. Open an image to begin.")
        self.status_label.setStyleSheet("color: #888888; font-style: italic;")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

    def display_results(self, result):
        """Update the panel with a new InferenceResult."""
        self.model_label.setText(result.model_name or "—")
        self.time_label.setText(f"{result.inference_time_ms:.1f} ms")
        self.count_label.setText(str(result.num_detections()))

        if result.num_detections() == 0:
            self.count_label.setStyleSheet("color: #d9534f;")
            self.status_label.setText(
                "No detections found. Try lowering the confidence threshold."
            )
        else:
            self.count_label.setStyleSheet("color: #5cb85c;")
            self.status_label.setText(
                f"Found {result.num_detections()} detection(s). "
                "Verify all results with clinical judgment."
            )

        self.table.setRowCount(0)
        for det in result.detections:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(det.class_name))
            conf_item = QTableWidgetItem(f"{det.confidence * 100:.1f}%")
            conf_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, conf_item)

            bbox_str = (
                f"({det.bbox[0]:.0f}, {det.bbox[1]:.0f}, "
                f"{det.bbox[2]:.0f}, {det.bbox[3]:.0f})"
            )
            self.table.setItem(row, 2, QTableWidgetItem(bbox_str))

    def clear(self):
        self.model_label.setText("—")
        self.time_label.setText("—")
        self.count_label.setText("—")
        self.count_label.setStyleSheet("")
        self.table.setRowCount(0)
        self.status_label.setText("No predictions yet. Open an image to begin.")
