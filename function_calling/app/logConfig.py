import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from enum import Enum

class Handler(str,Enum):
    FILE = "fileHandler"
    STREAM = "streamHandler"
    ROTATING = "rotatingFileHandler"
    
def setUpLogger(dir_name, file_name, handler : Handler):
    if handler != Handler.STREAM:
    # dir and file setup
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        file_path = dir_path / f"{file_name}.log"
        if not file_path.exists():
            file_path.touch()
        
        # logger
    logger = logging.getLogger("mylogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
        
    formatter = logging.Formatter(
        fmt="{asctime} - {name} - {levelname} {filename}:{funcName}:{lineno} - {message}",
        style="{"
    )
    if handler == Handler.FILE:
        file_handler = logging.FileHandler(file_path).setFormatter(formatter)
        logger.addHandler(file_handler)
    
    elif handler == Handler.STREAM:
        logger.addHandler(logging.StreamHandler().setFormatter(formatter))
        
    elif handler == Handler.ROTATING:
        logger.addHandler(
            RotatingFileHandler(file_path, maxBytes=10_000, backupCount=3).setFormatter(formatter)
        )
    
    return logger
    
        