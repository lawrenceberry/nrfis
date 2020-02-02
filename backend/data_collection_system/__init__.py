import sys
import os
import logging
import logging.handlers

from database import Session, Basement, StrongFloor, SteelFrame

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Create logger
os.makedirs(os.path.join(ROOT_DIR, "logs"), exist_ok=True)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

fileHandler = logging.handlers.TimedRotatingFileHandler(
    os.path.join(ROOT_DIR, "logs/data_collection_system.log"), when="midnight", utc=True
)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)
