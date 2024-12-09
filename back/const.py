from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# ! Below Are Constants

# Server
HOST=os.getenv("HOST")
PORT=int(os.getenv("PORT"))
STAGE=os.getenv("STAGE")
BASE_URL=os.getenv("BASE_URL")
SECRET_KEY=os.getenv("SECRET_KEY")

# Database
MONGO_DB=os.getenv("MONGO_DB")

ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

STRIPE_API=os.getenv("STRIPE_API")
STRIPE_SECRET=os.getenv("STRIPE_SECRET")

ROOT_DIR =  Path(__file__).resolve().parent
OUTPUTS_DIR = ROOT_DIR / "output"
LOG_DIR = ROOT_DIR / "logs"
LOG_FILE = LOG_DIR / "server.log"