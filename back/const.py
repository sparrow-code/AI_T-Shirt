from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL=os.getenv("BASE_URL")

STRIPE_API=os.getenv("STRIPE_API")
STRIPE_SECRET=os.getenv("STRIPE_SECRET")

ROOT_DIR =  Path(__file__).resolve().parent
OUTPUTS_DIR = ROOT_DIR / "output"
LOG_DIR = ROOT_DIR / "logs"
LOG_FILE = LOG_DIR / "server.log"