# app/utils/logger.py

import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """Создаёт настроенный логгер."""
    logger = logging.getLogger(name)
    
    # Избегаем дублирования хендлеров
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger
