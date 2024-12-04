from dotenv import load_dotenv
from const import *
from utils.setup import *
import os
import sys
import json
import base64
import logging
import uuid
from datetime import datetime

from utils.cors import CORSStaticFiles

from typing import Optional, Dict, Set
from fastapi.responses import RedirectResponse

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, File, UploadFile, Response, BackgroundTasks, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse, HTMLResponse

# Function Are Imported Here
from models.task import TaskStatus
from models.design import DesignRequest
from utils.task_queue import TaskQueue
from function.common import serialize_datetime

# Services Are Imported Here
from controller.info import BasicInfoController
from controller.img import ImgProcessing
from controller.payment import PaymentService

load_dotenv()
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Initialize directories and logging
setup_directories()
logger = setup_logging(logging)
logger.info("Starting FastAPI server initialization...")

# Initialize FastAPI app
app = FastAPI(
    title="AI T-Shirt Design API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
    max_age=3600
)


# Mount static files directory
app.mount("/images", CORSStaticFiles(directory=str(OUTPUTS_DIR)), name="images")

design_history: list = []

# Connected workers
connected_workers: Dict[str, WebSocket] = {}

# init class service
task_queue = TaskQueue(logger)
BasicInfoService = BasicInfoController(logger)
ImageService = ImgProcessing(logger)
PaymentService = PaymentService(logger)



@app.get("/")
async def root():
    """Root endpoint that redirects to /health"""
    return RedirectResponse(url="/health")

@app.get("/health")
async def health_check() : 
    return await BasicInfoService.health_check_controller(task_queue, connected_workers)

@app.get("/status")
async def service_status():
    return await BasicInfoService.service_status_controller( task_queue, connected_workers)

@app.get("/previous-designs")
async def get_previous_designs():
    """Get the last 5 generated designs."""
    try:
        return JSONResponse(content={
            "designs": design_history[-5:],
            "total": len(design_history)
        })
    except Exception as e:
        logger.error(f"Error getting design history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-design")
async def save_design(design_data: dict):
    """Save a design to history."""
    return await ImageService.save_design(design_data, design_history)
   

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Get the status of a design request"""
    return await BasicInfoService.status(task_queue, task_id)

@app.post("/remove-background")
async def remove_background(request: dict = Body(...)):
    """Remove background from uploaded image"""
    return await ImageService.remove_bg(request)
        

@app.post("/color-transparency")
async def color_transparency(
    file: UploadFile = File(...),
    color: str = Form(...),
    tolerance: float = Form(0.5)
):
    """Make specific color transparent"""
    return await ImageService.color_transparency(file, color, tolerance)

@app.post("/adjust-transparency")
async def adjust_transparency(request: dict = Body(...)):
    """Make image transparent based on transparency value"""
    return await ImageService.adjust_transparency(request)

@app.post("/generate")
async def generate_design(request: dict = Body(...)):
   """Primary endpoint for design generation"""
   return await ImageService.generate_image(request, task_queue)

@app.post("/designs/generate-fallback")
async def generate_design_fallback(request: dict = Body(...)):
    """Fallback endpoint for design generation with simplified parameters"""
    return await ImageService.generate_image_fallback(request, task_queue)

@app.post("/design")
async def create_design(request: DesignRequest):
    """Create a new design request and save it to history if successful."""
    return await ImageService.create_design(request, task_queue)

@app.get("/designs/history")
async def get_design_history():
    """Get the design history"""
    return await ImageService.get_design_history()

@app.post("/designs/save")
async def save_to_history(request: dict = Body(...)):
    """Save a design to history"""
    return await ImageService.save_design_history(request)

@app.get("/payment/create")
async def create_payment():
    session = await PaymentService.create_pay_session(10, "usd", "Test Payment")
    return {"checkout_url": session.url}

# Success/Cancel Endpoint
@app.get("/payment/{check}")
async def payment_status(check: str, session_id: str):
    session = await PaymentService.payment_status(session_id)
    if session == "complete":
        return {"message": "Payment successful! Thank you for your purchase."}
    elif session == "cancel":
        return {"message": "Payment canceled. Please try again."}
    else:
        raise HTTPException(status_code=404, detail="Invalid payment status")


@app.websocket("/ws")
async def websocket_worker(websocket: WebSocket):
    """WebSocket endpoint for worker connections"""
    await websocket.accept()
    worker_id = None
    
    try:
        while True:
            data = await websocket.receive_json()
            logger.info(f"Received WebSocket message: {data}")
            
            message_type = data.get("type")
            
            if message_type == "connect":
                worker_id = data.get("worker_id")
                connected_workers[worker_id] = websocket
                await websocket.send_json({
                    "type": "connected",
                    "status": "ok"
                })
                logger.info(f"Worker {worker_id} connected")
            
            elif message_type == "worker_status":
                if worker_id:
                    next_task = await task_queue.get_next_task()
                    if next_task:
                        await websocket.send_json({
                            "type": "task",
                            "data": {
                                "id": next_task.id,
                                **next_task.request
                            }
                        })
            
            elif message_type == "result":
                task_id = data.get("task_id")
                if task_id:
                    # Handle image data
                    image_data = data.get("image_data")
                    image_name = data.get("image_name")
                    
                    if image_data and image_name:
                        image_path = OUTPUTS_DIR / image_name
                        image_bytes = base64.b64decode(image_data)
                        
                        with open(image_path, "wb") as f:
                            f.write(image_bytes)
                        logger.info(f"Saved image to: {image_path}")
                        
                        # Update task status with correct image URL
                        result = {
                            "image_url": f"/images/{image_name}",
                            "metadata": data.get("metadata", {})
                        }
                    else:
                        result = {"error": data.get("error", "Unknown error")}
                    
                    await task_queue.update_task_status(
                        task_id,
                        TaskStatus.COMPLETED if data.get("status") == "completed" else TaskStatus.FAILED,
                        result
                    )
    
    except WebSocketDisconnect:
        if worker_id:
            logger.info(f"Worker {worker_id} disconnected")
            if worker_id in connected_workers:
                del connected_workers[worker_id]
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if worker_id and worker_id in connected_workers:
            del connected_workers[worker_id]

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    stage = os.getenv("STAGE", "DEV")
    logger.info(f"Stage >>> {stage}")
        
    if stage == "DEV":
        from pyngrok import ngrok
        public_url = ngrok.connect(port, "http", subdomain="poodle-feasible-sadly.ngrok-free.app")
        logger.info(f"FastAPI is accessible at: {public_url}")
    
    logger.info(f"Server initialization complete. Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        workers=1,
        log_level="info"
    )