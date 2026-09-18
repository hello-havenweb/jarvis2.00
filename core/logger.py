"""JARVIS logging configuration."""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


_INITIALIZED = False


def setup_logging(level: str = "INFO", log_file: str = "data/logs/jarvis.log",
                  max_size_mb: int = 10, backup_count: int = 5) -> logging.Logger:
    """Configure and return the root JARVIS logger."""
    global _INITIALIZED

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("jarvis")

    if _INITIALIZED:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)-7s] [%(name)-20s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File handler
    try:
        fh = RotatingFileHandler(
            str(log_path),
            maxBytes=max_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding="utf-8"
        )
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception as e:
        logger.warning(f"Could not create log file handler: {e}")

    _INITIALIZED = True
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a child logger under the jarvis namespace."""
    return logging.getLogger(f"jarvis.{name}")
