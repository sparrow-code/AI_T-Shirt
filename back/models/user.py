from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from beanie import Document, Indexed
from bson import ObjectId

class User(Document):
    name: str
    email: str = Indexed(str, unique=True)  # Correct way to define unique index in Beanie
    hashed_password: str
    profile_pic: Optional[str] = ""
    profession: Optional[str] = ""
    country: str = "Choose Your Country"
    address: Optional[str] = ""
    location: Optional[str] = ""
    phone: Optional[str] = ""
    credits: int = 0
    is_verify: bool = False
    role: str = "user"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)