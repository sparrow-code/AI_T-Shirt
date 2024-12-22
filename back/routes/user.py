
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()

@router.get("/credits")
async def credits():
    """
    
    """
    return

@router.get("/design")
async def design():
    return