from pydantic import BaseSettings

from const import MONGO_DB, SECRET

class Settings(BaseSettings):
    SECRET_KEY: str = SECRET
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MONGO_URI: str = MONGO_DB
    DATABASE_NAME: str = "AI_T_Shirt"

settings = Settings()
