import base64
from datetime import datetime, time, timedelta
import hashlib
import json
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from const import *
from utils.db import db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_jwt_token(token: str):
    if not is_token_active(token):  # Check if the token is active
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


SESSION_COLLECTION = "sessions"

def create_session(user_id: str, token: str, expire_at: datetime):
    session_data = {
        "user_id": user_id,
        "token": token,
        "created_at": datetime.now(),
        "expire_at": datetime.now() + timedelta(weeks=1),
    }
    db[SESSION_COLLECTION].create_index([("expire_at", 1)], expireAfterSeconds=0)
    db[SESSION_COLLECTION].insert_one(session_data)

def is_token_active(token: str):
    session = db[SESSION_COLLECTION].find_one({"token": token, "expire_at": {"$gt": datetime.utcnow()}})
    return bool(session)

def invalidate_session(token: str):
    db[SESSION_COLLECTION].delete_one({"token": token})