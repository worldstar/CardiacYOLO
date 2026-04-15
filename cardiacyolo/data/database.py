"""SQLite database for storing prediction history and audit logs."""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

logger = logging.getLogger("cardiacyolo")

# Default database location: user's home directory
DEFAULT_DB_PATH = Path.home() / ".cardiacyolo" / "cardiacyolo.db"


class Database:
    """Manages the local SQLite database."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        """Create tables if they don't exist."""
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_filename TEXT NOT NULL,
                    image_path TEXT,
                    model_name TEXT NOT NULL,
                    confidence_threshold REAL DEFAULT 0.5,
                    iou_threshold REAL DEFAULT 0.45,
                    num_detections INTEGER DEFAULT 0,
                    inference_time_ms REAL,
                    results_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_predictions_created
                    ON predictions(created_at);
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp
                    ON audit_logs(timestamp);
                """
            )
        logger.info(f"Database initialized at {self.db_path}")

    def save_prediction(
        self,
        image_filename: str,
        image_path: str,
        model_name: str,
        confidence_threshold: float,
        iou_threshold: float,
        num_detections: int,
        inference_time_ms: float,
        results_dict: Dict[str, Any],
    ) -> int:
        """Save a prediction record. Returns the new record id."""
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO predictions
                (image_filename, image_path, model_name, confidence_threshold,
                 iou_threshold, num_detections, inference_time_ms, results_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    image_filename,
                    image_path,
                    model_name,
                    confidence_threshold,
                    iou_threshold,
                    num_detections,
                    inference_time_ms,
                    json.dumps(results_dict),
                ),
            )
            return cursor.lastrowid

    def get_prediction_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent prediction records."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM predictions
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]

    def log_action(self, action: str, details: Optional[Dict[str, Any]] = None):
        """Log a user action to the audit trail."""
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO audit_logs (action, details) VALUES (?, ?)",
                (action, json.dumps(details) if details else None),
            )

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a setting value."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        """Set a setting value."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )
