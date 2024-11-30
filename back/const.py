from pathlib import Path


ROOT_DIR =  Path(__file__).resolve().parent
OUTPUTS_DIR = ROOT_DIR / "output"
LOG_DIR = ROOT_DIR / "logs"
LOG_FILE = LOG_DIR / "server.log"