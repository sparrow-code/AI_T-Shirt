from http.client import HTTPException
from typing import Optional
from fastapi import APIRouter, Depends, Response, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from schemas.auth import *
from controller.auth import get_user_details, login_user, logout_user, register_user
from datetime import datetime

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Helper function to get current timestamp
def get_current_timestamp():
    return datetime.utcnow()


@router.post("/register")
def register(user: UserRegister):
    return register_user(user)

@router.post("/login")
def login(response: Response, 
    form_data: Optional[OAuth2PasswordRequestForm] = Depends(),
    json_data: Optional[UserLogin] = None
):
    if json_data:
        username = json_data.username
        password = json_data.password
    elif form_data:
        username = form_data.username
        password = form_data.password
    else:
        raise HTTPException(
            status_code=422,
            detail="Either form data or JSON body is required"
        )


    user = UserLogin(email=username, password=password)
    return login_user(user, response)

@router.get("/me", tags=["Auth"], summary="Get current user details", description="This endpoint requires an Authorization header with a Bearer token.")
def me(token: str = Depends(oauth2_scheme)):
    return get_user_details(token)

@router.get("/logout", tags=["Auth"], summary="Logout user", description="This endpoint requires an Authorization header with a Bearer token.")
def logout(response: Response, token: str = Depends(oauth2_scheme)):
    return logout_user(token, response)
