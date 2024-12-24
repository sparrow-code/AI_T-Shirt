from fastapi import APIRouter, Depends, Response, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from schemas.auth import *
from controller.auth import get_user_details, login_user, logout_user, register_user, verify_token
from datetime import datetime

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

@router.get("/verify/{token}", tags=["Auth"], summary="Verify user")
def verify(token: str, response: Response):
    return verify_token(token, response)

@router.get("/me", tags=["Auth"], summary="Get current user details", description="This endpoint requires an Authorization header with a Bearer token.")
def me(token: str = Depends(oauth2_scheme)):
    return get_user_details(token)

@router.get("/logout", tags=["Auth"], summary="Logout user", description="This endpoint requires an Authorization header with a Bearer token.")
def logout(response: Response, token: str = Depends(oauth2_scheme)):
    return logout_user(token, response)
