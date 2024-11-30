# create a function with name health_check in 

async def health_check_controller():
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