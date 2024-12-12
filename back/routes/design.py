from fastapi import APIRouter, Body, UploadFile, File, Form
from controller.img import ImgProcessing

router = APIRouter()

ImageSevice = ImgProcessing()
design_history: list = []

@router.get("/history")
async def get_history():
    return await ImageSevice.get_design_history()

@router.post("/save")
async def save_design(design_data: dict):
    """Save a design to history."""
    return await ImageSevice.save_design(design_data, design_history)

@router.post("/save/history")
async def save_design(request: dict = Body(...)):
    return await ImageSevice.save_design_history(request)

@router.post("/generate")
async def generate(request: dict = Body(...)):
    return await ImageSevice.generate_image(request)

@router.post("/remove-background")
async def remove_background(request: dict = Body(...)):
    return await ImageSevice.remove_bg(request)

@router.post("/color-transparency")
async def color_transparency(
    file: UploadFile = File(...), 
    color: str = Form(...), 
    tolerance: float = Form(0.5)
):
    return await ImageSevice.color_transparency(file, color, tolerance)
