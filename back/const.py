from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.resolve()
OUTPUTS_DIR = ROOT_DIR / "outputs"
LOG_DIR = ROOT_DIR / "logs"
LOG_FILE = LOG_DIR / "server.log"