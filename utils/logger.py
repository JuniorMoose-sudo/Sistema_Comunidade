import logging
import os
from typing import Optional


_LOGGER: Optional[logging.Logger] = None


def get_logger(name: str = "app") -> logging.Logger:
    """Retorna um logger configurado para a aplicação."""
    global _LOGGER

    if _LOGGER is not None:
        return _LOGGER

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

    _LOGGER = logging.getLogger(name)
    return _LOGGER

