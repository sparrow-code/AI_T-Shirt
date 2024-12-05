from fastapi import APIRouter, Body, UploadFile, File, Form
from controller.img import ImageController

router = APIRouter(prefix="/designs", tags=["Design"])

@router.get("/history")
async def get_history():
    return await ImageController.get_history()

@router.post("/save")
async def save_design(request: dict = Body(...)):
    return await ImageController.save_design(request)

@router.post("/generate")
async def generate(request: dict = Body(...)):
    return await ImageController.generate_design(request)

@router.post("/remove-background")
async def remove_background(request: dict = Body(...)):
    return await ImageController.remove_background(request)

@router.post("/color-transparency")
async def color_transparency(
    file: UploadFile = File(...), 
    color: str = Form(...), 
    tolerance: float = Form(0.5)
):
    return await ImageController.color_transparency(file, color, tolerance)
