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
FRONT_URL=os.getenv("FRONT_URL")
SECRET_KEY=os.getenv("SECRET_KEY")

# Database
MONGO_DB=os.getenv("MONGO_DB")

ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# SMTP
EMAIL_ADDRESS=os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD=os.getenv("EMAIL_PASSWORD")
EMAIL_HOST=os.getenv("EMAIL_HOST")
EMAIL_PORT=os.getenv("EMAIL_PORT")

RAZORPAY_API=os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_SECRET=os.getenv("RAZORPAY_KEY_SECRET")

NGROK_TOKEN=os.getenv("NGROK_TOKEN")

ROOT_DIR =  Path(__file__).resolve().parent
OUTPUTS_DIR = ROOT_DIR / "output"
LOG_DIR = ROOT_DIR / "logs"
LOG_FILE = LOG_DIR / "server.log"