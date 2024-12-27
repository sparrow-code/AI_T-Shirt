from fastapi import APIRouter, Depends, Response, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from schemas.auth import *
from controller.auth import (get_user_details, login_user, logout_user, register_user, save_pic, update_profile, verify_token)
from datetime import datetime

from utils.auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
router = APIRouter()

# Helper function to get current timestamp
def get_current_timestamp():
    return datetime.utcnow()


@router.post("/register")
def register(user: UserRegister):
    return register_user(user)

@router.post("/login", summary="Login With Form Data")
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    email = form_data.username
    password = form_data.password
    user = UserLogin(email=email, password=password)
    return login_user(user, response)

@router.post("/login/json", summary="Login With JSON")
def login_json(response: Response, user: UserLogin):
    return login_user(user, response)

@router.get("/verify/{token}",  summary="Verify user")
def verify(response: Response, token: str):
    return verify_token(token, response)

@router.get("/me",  summary="Get current user details", description="This endpoint requires an Authorization header with a Bearer token.")
def me(token: str = Depends(oauth2_scheme)):
    return get_user_details(token)

@router.get("/logout",  summary="Logout user", description="This endpoint requires an Authorization header with a Bearer token.")
def logout(response: Response, token: str = Depends(oauth2_scheme)):
    return logout_user(token, response)

@router.post("/upload/profile-pic")
async def upload_profile_pic(pic_data: ProfilePicUpload, response : Response, token: str = Depends(oauth2_scheme)):
    current_user = decode_access_token(token)
    usrName = current_user["sub"]

    return save_pic(pic_data.pic_object,
                    usrName,
                    max_file_size_mb=5,
                    allowed_formats={'jpeg', 'png', 'gif'},
                    max_dimension=2000)

@router.put("/profile")
async def update_user_profile(user_data : UserRequest, token : str = Depends(oauth2_scheme)) :
    current_user = decode_access_token(token)
    usrName = current_user["sub"]

    return update_profile(usrName, user_data)
    
