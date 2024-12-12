import logging
from const import *

def setup_directories():
    """Setup required directories"""
    if not OUTPUTS_DIR.exists():
        OUTPUTS_DIR.mkdir(parents=True)
        print(f"Created directory: {OUTPUTS_DIR}")
    else:
        print(f"Directory already exists: {OUTPUTS_DIR}")

    # Create LOG_DIR if it doesn't exist
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True)
        print(f"Created directory: {LOG_DIR}")
    else:
        print(f"Directory already exists: {LOG_DIR}")

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()