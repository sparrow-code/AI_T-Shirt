from pydantic import BaseModel, EmailStr

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
    pic_object: str  # Base64 encoded image string

class ProfilePicResponse(BaseModel):
    status: bool
    message: str
    url: str