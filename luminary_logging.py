import os
import json
import time
import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = Path(__file__).resolve().parent / "logs" if 'Path' in globals() else "logs"
os.makedirs("logs", exist_ok=True)
LOG_FILE = os.path.join("logs", "luminary.log")

structured_logger = logging.getLogger("luminary_structured")
structured_logger.setLevel(logging.INFO)
structured_logger.propagate = False

if not structured_logger.handlers:
    # RotatingFileHandler: 10 MB per file, max 5 backup files
    rf_handler = RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    formatter = logging.Formatter("%(message)s")
    rf_handler.setFormatter(formatter)
    structured_logger.addHandler(rf_handler)

def log_structured_event(event_data: dict):
    """Log a single-line JSON event to logs/luminary.log."""
    if "timestamp" not in event_data:
        event_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    line = json.dumps(event_data, ensure_ascii=False)
    structured_logger.info(line)
