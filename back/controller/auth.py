from uuid import uuid4
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from utils.db import db
from utils.auth import *
from datetime import datetime, timedelta, timezone
from utils.smtp import smtp_utils
from bson import ObjectId
from utils.setup import logger

def register_user(user):
    if db.users.find_one({"email": user.email}):
        return {
            "status": False,
            "message": "Email already registered"
        }

    hashed_password = hash_password(user.password)
    date = datetime.now()
    token = str(uuid4())
    user_data = {
        "name" : user.name,
        "email": user.email,
        "hashed_password": hashed_password,
        "created_at": date,
        "updated_at": date,
        "credits" : 0,
        "is_verify" : False,
        "role": "user",
        "is_active": True,
    }
    db.users.insert_one(user_data)
    db.tokens.create_index([("expire_at", 1)], expireAfterSeconds=0)
    db.tokens.insert_one({"user_id": user_data["_id"], "token": token, "expire_at": datetime.now() + timedelta(hours=1)})

    verification_url = f'{FRONT_URL}/verify/{token}'
    subject = "Email Verification"
    body = f'Click the link to verify your email: {verification_url}'

    try:
        smtp_utils.send_email(subject, body, [user.email])
    except HTTPException as e:
        return { 
            "status" : False,
            "message" :"Failed to send verification email"
        }

    return {"status": True, "message": "Registration successful. Check your email for verification."}


def login_user(user, response):
    db_user = db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token, expire_at = create_access_token(data={"sub": db_user["email"]}, expires_delta=timedelta(weeks=1))
    response.set_cookie(key="access_token", value=access_token, expires=expire_at, secure=True)

    # Create session in database
    create_session(user_id=str(db_user["_id"]), token=access_token, expire_at=expire_at)

    return {"access_token": access_token, "token_type": "bearer"}

def get_user_details(token, id=False):
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    projection = {"hashed_password": 0}
    if not id:
        projection["_id"] = 0 

    user = db.users.find_one({"email": user_data["sub"]}, projection)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if "_id" in user:
        user["uid"] = "UID_" +  str(user.pop('_id'))

    return {
        "status" : True,
        "message" : "User details retrieved successfully",
        "user" : user
    }

def verify_token(token, response):
    session = db.tokens.find_one_and_delete({"token": token, "expire_at": {"$gt": datetime.utcnow()}})
    if not session:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.users.update_one(
        {"_id": ObjectId(session["user_id"])},
        {"$set": {"is_verify": True}}
    )

    if user.modified_count == 0:
        raise HTTPException(status_code=400, detail="User not found or already verified")

    updated_user = db.users.find_one({"_id": ObjectId(session["user_id"])})
    if not updated_user:
        raise HTTPException(status_code=400, detail="User not found after update")

    access_token, expire_at = create_access_token(
        data={"sub": updated_user["email"]}, expires_delta=timedelta(weeks=1)
    )

    if expire_at.tzinfo is None:
        expire_at = expire_at.replace(tzinfo=timezone.utc)

    response.set_cookie(
        key="access_token",
        value=access_token,
        expires=expire_at,
        secure=True,
        httponly=True
    )
    create_session(user_id=str(session["user_id"]), token=access_token, expire_at=expire_at)

    return {
        "status" : True,
        "access_token": access_token,
        "token_type": "bearer",
        "message" : "User verified successfully"
    }

def logout_user(token, response):
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    invalidate_session(token)
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}