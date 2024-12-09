# Class Which Contain All Image Related Functions

# ? Library To Work With Files
import io
import json
import uuid
from datetime import datetime
from utils.setup import logger

from routes.info import task_queue

# ? Library To Work With Image
from const import OUTPUTS_DIR
import cv2
import base64
import numpy as np
from PIL import Image
from models.design import DesignRequest
from rembg import remove

# ? To Process Response
from fastapi import HTTPException, Response
from fastapi.responses import JSONResponse

class ImgProcessing :

    def __init__(self) -> None:
        pass

    async def remove_bg(self, request) -> bytes:
        try:

            # Decode base64 image
            image_data = base64.b64decode(request["image"])
            input_image = Image.open(io.BytesIO(image_data))
            
            # Remove background
            output_image = remove(input_image)
            
            # Convert back to base64
            img_byte_arr = io.BytesIO()
            output_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            return JSONResponse({
                "image": f"data:image/png;base64,{base64.b64encode(img_byte_arr).decode('utf-8')}"
            })
        except Exception as e:
            logger.error(f"Error in background removal: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def color_transparency(self, file, color: str, tolerance: float) -> bytes:
        try:        
            # Process image
            contents = await file.read()
            nparr = np.frombuffer(contents, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert hex color to BGR
            color = color.lstrip('#')
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            bgr = (rgb[2], rgb[1], rgb[0])
            
            # Create mask for the specified color
            mask = cv2.inRange(img, 
                            np.array([max(0, x - int(tolerance * 255)) for x in bgr]),
                            np.array([min(255, x + int(tolerance * 255)) for x in bgr]))
            
            # Add alpha channel
            b, g, r = cv2.split(img)
            alpha = cv2.bitwise_not(mask)
            img_rgba = cv2.merge((b, g, r, alpha))
            
            # Convert to PNG
            is_success, buffer = cv2.imencode(".png", img_rgba)
            if not is_success:
                raise HTTPException(status_code=500, detail="Failed to encode image")
            
            return Response(content=buffer.tobytes(), media_type="image/png")
        except Exception as e:
            logger.error(f"Error in color transparency: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        
    async def adjust_transparency(self, request) -> bytes:
        try:       
            # Decode base64 image
            image_data = base64.b64decode(request["image"])
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
            
            # If image doesn't have alpha channel, add it
            if img.shape[2] == 3:
                b, g, r = cv2.split(img)
                alpha = np.ones(b.shape, dtype=b.dtype) * 255
                img = cv2.merge((b, g, r, alpha))
                
            # Adjust alpha channel
            b, g, r, a = cv2.split(img)
            transparency = float(request["transparency"])
            alpha = cv2.multiply(a, 1 - transparency)
            img_rgba = cv2.merge((b, g, r, alpha.astype(np.uint8)))
            
            # Convert to PNG
            is_success, buffer = cv2.imencode(".png", img_rgba)
            if not is_success:
                raise HTTPException(status_code=500, detail="Failed to encode image")
                
            # Convert to base64
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return JSONResponse({
                "image": f"data:image/png;base64,{img_base64}"
            })
        except Exception as e:
            logger.error(f"Error adjusting transparency: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ! Required Task Que
    async def generate_image(self, request) -> bytes:
        try:
            design_request = DesignRequest(
                prompt=request["prompt"],
                style=request.get("style", "realistic"),
                colors=request.get("colors", []),
                size=request.get("size", "M"),
                priority=request.get("priority", 1)
            )
            
            # Add task to queue and get task ID
            task_id = await task_queue.add_task(design_request)
            logger.info(f"Created new task: {task_id}")
            
            # Wait for the result (with timeout)
            result = await task_queue.wait_for_result(task_id, timeout=120)  # Increased timeout to 120 seconds
            
            if result and result.get("image_url"):
                return JSONResponse({
                    "result": {
                        "image_url": result["image_url"],
                        "task_id": task_id
                    }
                })
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Design generation failed or timed out. The server is taking longer than expected to respond."
                )
                    
        except Exception as e:
            logger.error(f"Error generating design: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ! Require Tast Que
    async def generate_image_fallback(self, request) -> bytes:
        try:
            design_request = DesignRequest(
                prompt=request["prompt"],
                negative_prompt="",
                num_inference_steps=20,  # Faster generation for fallback
                guidance_scale=7.0
            )
            
            # Add task to queue and get task ID
            task_id = await task_queue.add_task(design_request)
            logger.info(f"Created fallback task: {task_id}")
            
            # Wait for the result (with shorter timeout)
            result = await task_queue.wait_for_result(task_id, timeout=30)  # Shorter timeout for fallback
            
            if result and result.get("image_data"):
                return JSONResponse({
                    "result": {
                        "image_data": result["image_data"],
                        "task_id": task_id
                    }
                })
            else:
                raise HTTPException(status_code=500, detail="Fallback generation failed or timed out")
                
        except Exception as e:
            logger.error(f"Error in fallback generation: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def save_design(self, design_data, design_history) -> bytes:
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
    
    # ! Required Task Que
    async def create_design(self, request) -> bytes:
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
        
    async def save_design_history(self, request) -> bytes:
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
                "image_data": request["image_url"],
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
    
    async def get_design_history(self) -> bytes:
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