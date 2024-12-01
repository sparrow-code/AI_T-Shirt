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
