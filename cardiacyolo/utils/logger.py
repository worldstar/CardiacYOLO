"""Logging configuration for CardiacYOLO."""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name="cardiacyolo", level=logging.INFO):
    """Configure and return a logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_dir = Path.home() / ".cardiacyolo" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"cardiacyolo_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
