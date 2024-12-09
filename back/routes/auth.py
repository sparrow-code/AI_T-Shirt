from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from controller.auth import get_user_details, login_user, logout_user, register_user
from datetime import datetime

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Helper function to get current timestamp
def get_current_timestamp():
    return datetime.utcnow()



@router.post("/register")
def register(user: UserRegister):
    return register_user(user)

@router.post("/login")
def login(user: UserLogin, response: Response):
    return login_user(user, response)

@router.get("/me")
def me(token: str = Depends(oauth2_scheme)):
    return get_user_details(token)

@router.get("/logout")
def logout(response: Response, token: str = Depends(oauth2_scheme)):
    return logout_user(token, response)

"""
# Register route
@router.post("/register", response_model=Token)
def register(user: UserRegister):
    existing_user = db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    created_at = updated_at = get_current_timestamp()

    user_data = {
        "email": user.email,
        "hashed_password": hashed_password,
        "role": "user",
        "is_active": True,
        "created_at": created_at,
        "updated_at": updated_at,
    }
    db.users.insert_one(user_data)

    # Create JWT token
    access_token = create_access_token(data={"sub": user.email})

    # Store this token into session db
    session_expiration_time = timedelta(hours=1)
    expire_at = get_current_timestamp() + session_expiration_time
    session_data = {
        "user_id": str(user_data["_id"]),
        "access_token": access_token,
        "created_at": get_current_timestamp(),
        "updated_at": get_current_timestamp(),
        "expire_at": expire_at
    }

    return {"access_token": access_token, "token_type": "bearer"}

# Login route
@router.post("/login", response_model=Token)
def login(user: UserLogin):
    db_user = db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Create JWT token
    access_token = create_access_token(data={"sub": user.email})

    # Store this token into session db
    session_expiration_time = timedelta(hours=1)
    expire_at = get_current_timestamp() + session_expiration_time
    session_data = {
        "user_id": str(db_user["_id"]),
        "access_token": access_token,
        "created_at": get_current_timestamp(),
        "updated_at": get_current_timestamp(),
        "expire_at": expire_at
    }
    return {"access_token": access_token, "token_type": "bearer"}

# Logout route
@router.get("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(token: str = Depends(oauth2_scheme)):
    # Here, you may add logic to invalidate the session if needed (e.g., delete session in DB)
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid session")

    return {"message": "Logged out successfully"}

# Me route
@router.get("/me")
def me(token: str = Depends(oauth2_scheme)):
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid session")

    user = db.users.find_one({"email": user_data["sub"]}, {"_id": 0, "hashed_password": 0})
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    return user

"""