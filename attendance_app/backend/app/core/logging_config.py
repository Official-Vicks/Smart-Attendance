import logging
import sys
from pythonjsonlogger import jsonlogger
from app.core.logging_filter import ContextFilter


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 🔥 REMOVE existing handlers (VERY IMPORTANT)
    logger.handlers.clear()


    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(user_id)s %(school_id)s %(role)s"
    )

    # -----------------------------
    # 1. Console Handler (Terminal)
    # -----------------------------
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(ContextFilter())

    # -----------------------------
    # 2. File Handler (Persistent)
    # -----------------------------
    file_handler = logging.FileHandler("app.log")
    file_handler.setFormatter(formatter)
    file_handler.addFilter(ContextFilter())

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)