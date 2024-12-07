from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL=os.getenv("BASE_URL")
SECRET=os.getenv("SECRET")
MONGO_DB=os.getenv("MONGO_DB")

SECRET_KEY="I_Love_Mine_Secret"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

STRIPE_API=os.getenv("STRIPE_API")
STRIPE_SECRET=os.getenv("STRIPE_SECRET")

ROOT_DIR =  Path(__file__).resolve().parent
OUTPUTS_DIR = ROOT_DIR / "output"
LOG_DIR = ROOT_DIR / "logs"
LOG_FILE = LOG_DIR / "server.log"