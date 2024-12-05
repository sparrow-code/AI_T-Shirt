from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class UserInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    hashed_password: str
    role: str = "user"  # Default role
    is_active: bool = True

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True
