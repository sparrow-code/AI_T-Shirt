from io import BytesIO
import re
from uuid import uuid4
from PIL import Image
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from models.user import User
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

    # Create new user document with all defaults
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    
    # Insert user with all default values automatically handled
    result = db.users.insert_one(new_user.to_mongo())
    user_id = result.inserted_id
    
    # Create token
    token = str(uuid4())
    db.tokens.create_index([("expire_at", 1)], expireAfterSeconds=0)
    db.tokens.insert_one({
        "user_id": user_id,
        "token": token,
        "expire_at": datetime.now() + timedelta(hours=1)
    })

    # Send verification email
    verification_url = f'{FRONT_URL}/verify/{token}'
    subject = "Email Verification"
    body = f'Click the link to verify your email: {verification_url}'

    try:
        smtp_utils.send_email(subject, body, [user.email])
    except HTTPException as e:
        return {
            "status": False,
            "message": "Failed to send verification email"
        }

    return {
        "status": True,
        "message": "Registration successful. Check your email for verification."
    }

def login_user(user, response):
    db_user = db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token, expire_at = create_access_token(
        data={"sub": db_user["email"]}, expires_delta=timedelta(weeks=1)
    )

    if expire_at.tzinfo is None:
        expire_at = expire_at.replace(tzinfo=timezone.utc)

    response.set_cookie(
        key="access_token",
        value=access_token,
        expires=expire_at,
        secure=True
    )
    create_session(user_id=str(db_user["_id"]), token=access_token, expire_at=expire_at)

    return {
        "status" : True,
        "access_token": access_token,
        "token_type": "bearer",
        "message" : "User verified successfully"
    }

def get_user_details(token, id=False):
    user_data = verify_jwt_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    projection = {"hashed_password": 0}
    if not id:
        projection["_id"] = 0 

    user = db.users.find_one({"email": user_data["sub"]}, projection)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if "_id" in user:
        user["uid"] = "UID_" +  str(user['_id'])
        user.pop("_id")
        user.pop("updated_at")
        user.pop("created_at")

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
        secure=True
    )
    create_session(user_id=str(session["user_id"]), token=access_token, expire_at=expire_at)

    return {
        "status" : True,
        "access_token": access_token,
        "token_type": "bearer",
        "message" : "User verified successfully"
    }

def logout_user(token, response):    
    invalidate_session(token)
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}

def update_profile(usrName, user_data):
    update_data = user_data.model_dump()
    update_data["updated_at"] = datetime.now()

    result = db.user.find_one_and_update(
            {"email": usrName},
            {"$set": update_data},
            return_document=True
        )
    if result is None:
        return {
            "status" : False,
            "message" : f"User with email {usrName} not found"
        }
        
    return {
        "status": "success",
        "message": "Profile updated successfully",
    }


def save_pic(
        pic_data: str,
        usrName: str,
        max_file_size_mb: int = 5,
        allowed_formats: set = {'jpeg', 'png', 'gif'},
        max_dimension: int = 2000):
            usrName = usrName.split("@")[0]
            username = re.sub(r'[<>:"/\\|?*]', '_', usrName)
            # Create directory if not exists
            output_dir = OUTPUTS_DIR / username
            output_dir.mkdir(parents=True, exist_ok=True)

            try:
                # Decode the base64 encoded image data
                image_data = base64.b64decode(pic_data)
                image = Image.open(BytesIO(image_data))
            except Exception as e:
                return {
                    "status": False,
                    "message": "Invalid image data"
                }

            # Validate image format
            if image.format.lower() not in allowed_formats:
                return {
                    "status": False,
                    "message": f"Unsupported file format. Allowed formats are {', '.join(allowed_formats)}"
                }

            # Validate image size
            if len(image_data) > max_file_size_mb * 1024 * 1024:
                return {
                    "status": False,
                    "message": f"File size exceeds the {max_file_size_mb} MB limit"
                }

            # Validate image dimensions
            if image.width > max_dimension or image.height > max_dimension:
                return {
                    "status": False,
                    "message": f"Image dimensions exceed the {max_dimension}x{max_dimension} limit"
                }

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"profile_{timestamp}.{image.format.lower()}"
            file_path = os.path.join(output_dir, filename)

            try:
                # Save the image to the directory
                image.save(file_path)
            except Exception:
                return {
                    "status": False,
                    "message": "Failed to save image"
                }

            # Clean up old profile pictures
            for old_file in os.listdir(output_dir):
                if old_file.startswith("profile_") and old_file != filename:
                    try:
                        os.remove(os.path.join(output_dir, old_file))
                    except Exception:
                        pass  # Ignore errors in cleanup

            # Generate URL for the saved image
            image_url = f"/images/{username}/{filename}"
            db.users.find_one_and_update(
                {"email": usrName}, 
                {"$set": {"profile_pic": image_url}}
            )

            return {
                "status": True,
                "message": "Profile picture uploaded successfully",
                "url": image_url
            }