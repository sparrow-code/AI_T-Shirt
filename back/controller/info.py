from datetime import datetime
import json

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from const import *
from utils.setup import logger


class BasicInfoController:
    def __init__(self):
        pass

    # now create a function

    async def health_check_controller(self, task_queue, connected_workers):
        """Health check endpoint"""
        response_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "components": {
                "workers": {
                    "status": "healthy" if connected_workers else "degraded",
                    "count": len(connected_workers)
                },
                "queue": {
                    "status": "healthy",
                    "size": task_queue.size()
                },
                "storage": {
                    "status": "healthy"
                }
            }
        }

        try:
            # Check if outputs directory is writable
            test_file = OUTPUTS_DIR / "test.txt"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except Exception as e:
                logger.error(f"Outputs directory not writable: {str(e)}")
                response_data["status"] = "degraded"
                response_data["components"]["storage"] = {
                    "status": "unhealthy",
                    "error": "Outputs directory not writable"
                }

            # Update overall status based on component statuses
            if any(component["status"] == "unhealthy" for component in response_data["components"].values()):
                response_data["status"] = "unhealthy"
            elif any(component["status"] == "degraded" for component in response_data["components"].values()):
                response_data["status"] = "degraded"

            return JSONResponse(
                status_code=200,  # Always return 200 OK, let the client decide based on the status field
                content=response_data
            )
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return JSONResponse(
                status_code=500,  # Only return 500 for unexpected errors
                content={
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

    async def service_status_controller(self, task_queue, connected_workers):
        """Get detailed service status"""
        try:
            return {
                "status": "online",
                "workers": {
                    "connected": len(connected_workers),
                    "ids": list(connected_workers.keys())
                },
                "queue": {
                    "size": task_queue.size(),
                    "pending": task_queue.pending_count(),
                    "processing": task_queue.processing_count()
                },
                "storage": {
                    "outputs_dir": str(OUTPUTS_DIR),
                    "space_available": True  # TODO: Add actual disk space check
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting service status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        
    async def get_task_status_controller(self, task_queue, task_id) -> dict:
        try:
            status = await task_queue.get_task_status(task_id)
            if not status:
                logger.error(f"Task not found: {task_id}")
                raise HTTPException(status_code=404, detail="Task not found")
            
            logger.info(f"Task status: {json.dumps(status)}")
            return JSONResponse(status)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))