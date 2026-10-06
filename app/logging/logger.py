"""
Production structured logging system with custom SUCCESS level,
disk persistence, retention management, and live UI log buffering.
"""

from __future__ import annotations
import os
import sys
import time
import glob
import logging
from pathlib import Path
from typing import Optional, List
from .buffer_handler import BufferLogHandler

# Define SUCCESS level between INFO (20) and WARNING (30)
SUCCESS_LEVEL_NUM = 25
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")


def log_success(self, message, *args, **kws):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)


logging.Logger.success = log_success  # type: ignore

_BUFFER_HANDLER: Optional[BufferLogHandler] = None
_ROOT_LOGGER: Optional[logging.Logger] = None


def get_default_log_dir() -> Path:
    """Returns %APPDATA%/VirtualDesktopWorkspaceManager/logs or fallback."""
    app_data = os.environ.get("APPDATA")
    if app_data:
        log_dir = Path(app_data) / "VirtualDesktopWorkspaceManager" / "logs"
    else:
        log_dir = Path.home() / ".virtual_desktop_manager" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(
    log_dir: Optional[str] = None,
    log_level: str = "INFO",
    retention_days: int = 14
) -> logging.Logger:
    """Initializes the unified application logger with console, file, and buffer outputs."""
    global _BUFFER_HANDLER, _ROOT_LOGGER

    logger = logging.getLogger("VDWM")
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    logger.propagate = False

    # Clear existing handlers to avoid duplicates on re-init
    for h in list(logger.handlers):
        logger.removeHandler(h)

    # Formatter: matches prompt format "YYYY-MM-DD HH:MM:SS [LEVEL] message"
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    # 2. In-memory buffer handler for UI
    if _BUFFER_HANDLER is None:
        _BUFFER_HANDLER = BufferLogHandler(capacity=2000)
    _BUFFER_HANDLER.setFormatter(formatter)
    _BUFFER_HANDLER.setLevel(logging.DEBUG)  # Buffer receives all levels
    logger.addHandler(_BUFFER_HANDLER)

    # 3. File handler
    target_dir = Path(log_dir) if log_dir else get_default_log_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    date_str = time.strftime("%Y%m%d")
    log_file = target_dir / f"workspace_{date_str}.log"
    file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)

    # Clean old logs according to retention
    clean_old_logs(target_dir, retention_days)

    _ROOT_LOGGER = logger
    return logger


def clean_old_logs(log_dir: Path, retention_days: int) -> None:
    """Purges log files older than retention_days."""
    if retention_days <= 0:
        return
    now = time.time()
    cutoff = now - (retention_days * 86400)
    try:
        for file_path in log_dir.glob("workspace_*.log"):
            if file_path.stat().st_mtime < cutoff:
                file_path.unlink(missing_ok=True)
    except Exception:
        pass


def get_logger() -> logging.Logger:
    """Returns the application logger, initializing if needed."""
    global _ROOT_LOGGER
    if _ROOT_LOGGER is None:
        return setup_logging()
    return _ROOT_LOGGER


def get_buffer_handler() -> BufferLogHandler:
    """Returns the UI log buffer handler."""
    global _BUFFER_HANDLER
    if _BUFFER_HANDLER is None:
        setup_logging()
    assert _BUFFER_HANDLER is not None
    return _BUFFER_HANDLER
