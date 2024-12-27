from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class ProfilePicUpload(BaseModel):
    pic_object: str

class ProfilePicResponse(BaseModel):
    status: bool
    message: str
    url: str

class UserRequest(BaseModel):
    name: str
    profession: str
    country: str
    address: str
    location: str
    phone: str
    web: str
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

    def to_mongo(self) -> dict:
        """Convert the model to a MongoDB-ready dictionary"""
        return self.model_dump(exclude_unset=True)