#!/usr/bin/env python3
"""
CardiacYOLO - AI-Powered Valvular Regurgitation Detection
Main entry point for the application.
"""

import sys
from pathlib import Path

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from cardiacyolo.gui.main_window import MainWindow
from cardiacyolo.utils.logger import setup_logger


def main():
    """Application entry point."""
    logger = setup_logger()
    logger.info("Starting CardiacYOLO application...")

    app = QApplication(sys.argv)
    app.setApplicationName("CardiacYOLO")
    app.setOrganizationName("CardiacYOLO Team")
    app.setApplicationDisplayName("CardiacYOLO - Valvular Regurgitation Detection")

    icon_path = PROJECT_ROOT / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()

    logger.info("Application started successfully")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
