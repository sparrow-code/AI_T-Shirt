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
BasicInfoService = BasicInfoController(logger, connected_workers, task_queue)
ImageService = ImgProcessing(logger)



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
    try:
        if "image_data" not in design_data:
            raise HTTPException(status_code=400, detail="No image data provided")

        # Validate base64 image data
        try:
            image_data = design_data["image_data"]
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            import base64
            base64.b64decode(image_data)
        except Exception as e:
            logger.error(f"Invalid image data: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid image data")

        # Add timestamp and metadata
        design_entry = {
            "image_data": design_data["image_data"],
            "created_at": datetime.utcnow().isoformat(),
            "metadata": design_data.get("metadata", {})
        }

        design_history.append(design_entry)
        
        # Keep only last 5 designs
        while len(design_history) > 5:
            design_history.pop(0)
        
        return {"status": "success", "timestamp": design_entry["created_at"]}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving design: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
    try:
        # Add task to queue and get task ID
        task_id = await task_queue.add_task(request)
        logger.info(f"Created new task: {task_id}")
        
        return JSONResponse({
            "task_id": task_id,
            "status": "pending"
        })
        
    except Exception as e:
        logger.error(f"Error creating design: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test/health", tags=["test"])
async def test_health():
    """Simple health check for curl testing"""
    return JSONResponse(
        content={"status": "healthy", "timestamp": datetime.utcnow().isoformat()},
        headers={"Content-Type": "application/json"}
    )

@app.post("/test/design", tags=["test"])
async def test_design_generation(
    prompt: str = Body(..., embed=True),
    test_mode: bool = Body(False, embed=True)
):
    """Test endpoint for design generation"""
    try:
        if test_mode:
            return JSONResponse(
                content={
                    "status": "success",
                    "task_id": "test_task_123",
                    "message": "Test design request received",
                    "prompt": prompt,
                    "test_mode": True
                },
                headers={"Content-Type": "application/json"}
            )
        request = DesignRequest(prompt=prompt)
        result = await create_design(request)
        return JSONResponse(content=result, headers={"Content-Type": "application/json"})
    except Exception as e:
        logger.error(f"Error in test design generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/background-removal", tags=["test"])
async def test_background_removal(
    image_url: str = Body(..., embed=True),
    test_mode: bool = Body(False, embed=True)
):
    """Test endpoint for background removal"""
    try:
        if test_mode:
            return JSONResponse(
                content={
                    "status": "success",
                    "message": "Test background removal request received",
                    "image_url": image_url,
                    "test_mode": True
                },
                headers={"Content-Type": "application/json"}
            )
        return JSONResponse(
            content={"status": "success", "message": "Background removal completed"},
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        logger.error(f"Error in test background removal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test/workers", tags=["test"])
async def test_workers():
    """Test endpoint to check worker status"""
    try:
        return JSONResponse(
            content={
                "status": "success",
                "workers": {
                    "connected": len(connected_workers),
                    "ids": list(connected_workers.keys())
                }
            },
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        logger.error(f"Error in worker status check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test/run-all", tags=["test"])
async def run_all_tests():
    """Run all system tests and return results"""
    try:
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "tests": {
                "health": await test_health(),
                "workers": await test_workers(),
                "design": await test_design_generation(prompt="test design", test_mode=True),
                "background_removal": await test_background_removal(image_url="test.png", test_mode=True)
            }
        }
        return JSONResponse(content=results, headers={"Content-Type": "application/json"})
    except Exception as e:
        logger.error(f"Error running all tests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test", tags=["test"])
async def test_display():
    """Display comprehensive system test results"""
    try:
        # Get all test results
        results = await run_all_tests()
        
        # Generate HTML response
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI T-Shirt Designer - System Tests</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .test-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .success {{ color: green; }}
                .error {{ color: red; }}
                pre {{ background: #f5f5f5; padding: 10px; }}
            </style>
        </head>
        <body>
            <h1>AI T-Shirt Designer - System Tests</h1>
            <div class="test-section">
                <h2>Test Results</h2>
                <pre>{json.dumps(results, indent=2)}</pre>
            </div>
            <div class="test-section">
                <h2>Available Test Endpoints</h2>
                <ul>
                    <li><code>GET /test/health</code> - Health check</li>
                    <li><code>POST /test/design</code> - Test design generation</li>
                    <li><code>POST /test/background-removal</code> - Test background removal</li>
                    <li><code>GET /test/workers</code> - Check worker status</li>
                    <li><code>GET /test/run-all</code> - Run all tests</li>
                </ul>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, headers={"Content-Type": "text/html"})
    except Exception as e:
        logger.error(f"Error displaying test dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/designs/history")
async def get_design_history():
    """Get the design history"""
    try:
        history_file = OUTPUTS_DIR / "history.json"
        if not history_file.exists():
            return JSONResponse([])  # Return empty array if no history exists
            
        try:
            with open(history_file, "r") as f:
                history = json.load(f)
                # Return the last 10 designs, most recent first
                return JSONResponse(history[-10:])
        except json.JSONDecodeError:
            logger.error("Error decoding history file")
            return JSONResponse([])
            
    except Exception as e:
        logger.error(f"Error fetching design history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/designs/save")
async def save_to_history(request: dict = Body(...)):
    """Save a design to history"""
    try:
        history_file = OUTPUTS_DIR / "history.json"
        
        # Load existing history or create new
        if history_file.exists():
            try:
                with open(history_file, "r") as f:
                    history = json.load(f)
            except json.JSONDecodeError:
                history = []
        else:
            history = []
        
        # Create new history item
        new_item = {
            "id": str(uuid.uuid4()),
            "image_data": request["image_data"],
            "prompt": request.get("prompt", ""),
            "created_at": datetime.utcnow().isoformat(),
            "transform": request.get("transform", None)
        }
        
        # Add to history and save
        history.append(new_item)
        with open(history_file, "w") as f:
            json.dump(history, f)
            
        return JSONResponse({"status": "success", "id": new_item["id"]})
        
    except Exception as e:
        logger.error(f"Error saving to history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
        public_url = ngrok.connect(port)
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