from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId

class User(BaseModel):
    name: str
    email: str = EmailStr
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

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
    
    def to_mongo(self) -> dict:
        """Convert the model to a MongoDB-ready dictionary with all defaults applied"""
        return self.model_dump(exclude_unset=False)