"""
logger.py
---------
Application logging module.
"""

import logging
from datetime import datetime
from pathlib import Path


class LoggerManager:
    """Application logger."""

    _logger = None

    @staticmethod
    def get_logger() -> logging.Logger:

        if LoggerManager._logger:
            return LoggerManager._logger

        project_root = Path(__file__).resolve().parent.parent

        log_folder = project_root / "logs"

        log_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        log_file = log_folder / (
            datetime.now().strftime("%Y-%m-%d") + ".log"
        )

        logger = logging.getLogger("NetOpsAutomationSuite")

        logger.setLevel(logging.INFO)

        # Prevent duplicate handlers
        if not logger.handlers:

            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(message)s",
                "%Y-%m-%d %H:%M:%S",
            )

            file_handler = logging.FileHandler(
                log_file,
                encoding="utf-8",
            )

            file_handler.setFormatter(formatter)

            logger.addHandler(file_handler)

        LoggerManager._logger = logger

        return logger

    @staticmethod
    def info(message: str) -> None:
        LoggerManager.get_logger().info(message)

    @staticmethod
    def warning(message: str) -> None:
        LoggerManager.get_logger().warning(message)

    @staticmethod
    def error(message: str) -> None:
        LoggerManager.get_logger().error(message)

    @staticmethod
    def success(message: str) -> None:
        """
        SUCCESS is logged as INFO with a prefix.
        """
        LoggerManager.get_logger().info(
            f"SUCCESS | {message}"
        )