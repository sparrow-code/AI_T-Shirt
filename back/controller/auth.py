from fastapi import HTTPException
from utils.db import db
from utils.auth import *
from datetime import datetime, timedelta

def register_user(user):
    if db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    user_data = {
        "email": user.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True,
    }
    db.users.insert_one(user_data)

    return {"message": "User registered successfully"}

def login_user(user, response):
    db_user = db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token, expire_at = create_access_token(data={"sub": db_user["email"]}, expires_delta=timedelta(minutes=60))
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    # Create session in database
    create_session(user_id=str(db_user["_id"]), token=access_token, expire_at=expire_at)

    return {"access_token": access_token, "token_type": "bearer"}

def get_user_details(token):
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.users.find_one({"email": user_data["sub"]}, {"_id": 0, "hashed_password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

def logout_user(token, response):
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    invalidate_session(token)
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}