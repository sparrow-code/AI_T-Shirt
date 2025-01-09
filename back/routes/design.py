from fastapi import APIRouter, Body, Depends, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer
from controller.img import ImgProcessing
from schemas.design import BGRemoveRequest, ImageGenerateRequest
from utils.auth import decode_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

ImageSevice = ImgProcessing()
design_history: list = []

@router.get("/history", summary="Get History", description="Get Top 5 AI Image History")
async def get_history():
    return await ImageSevice.get_design_history()

@router.post("/save", summary="Need To Code", description="Save A Design To History")
async def save_design(design_data: dict):
    """Save a design to history."""
    return await ImageSevice.save_design(design_data, design_history)

@router.post("/save/history", summary="Save to History", description="Save A Design To History")
async def save_design(request: dict = Body(...)):
    return await ImageSevice.save_design_history(request)

@router.post("/generate", summary="Generate AI Image", description="It will Only Generate Image using AI")
async def generate(request: ImageGenerateRequest):
    request_data = request.dict()
    return await ImageSevice.generate_image(request_data)

@router.post("/remove-background")
async def remove_background(request: BGRemoveRequest):
    return await ImageSevice.remove_bg(request)

@router.post("/color-transparency")
async def color_transparency(
    file: UploadFile = File(...), 
    color: str = Form(...), 
    tolerance: float = Form(0.5)
):
    return await ImageSevice.color_transparency(file, color, tolerance)
