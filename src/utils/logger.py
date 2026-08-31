import logging
import sys
from pathlib import Path
from typing import Optional

_CONFIGURED = False


def setup_logging(log_file: Optional[str] = None, level: int = logging.INFO) -> None:
    """Configures the root 'retrobandaid' logger. Safe to call multiple times."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    logger = logging.getLogger("retrobandaid")
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Returns a child logger under the 'retrobandaid' namespace."""
    if not _CONFIGURED:
        setup_logging()
    return logging.getLogger(f"retrobandaid.{name}")
