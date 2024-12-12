from const import *

# Create an Fast API App
from routes import auth, info, design, user
from utils.setup import setup_directories, logger

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()
setup_directories()

# Initialize FastAPI app
app = FastAPI(
    title="AI T-Shirt Design API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

@app.get("/")
async def root():
    return RedirectResponse(url="/api/info/health")

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(info.router, prefix="/api/info", tags=["Info"])
app.include_router(design.router, prefix="/api/design", tags=["Design"])
app.include_router(user.router, prefix="/api/user", tags=["User"])



# ! Websocket Worker




if __name__ == "__main__":
    import uvicorn
        
    if STAGE == "DEV":
        from pyngrok import ngrok
        public_url = ngrok.connect(PORT, "http", "poodle-feasible-sadly.ngrok-free.app")
        logger.info(f"FastAPI is accessible at: {public_url}")
    
    logger.info(f"Server initialization complete. Starting server on {HOST}:{PORT}")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
        workers=1,
        log_level="info"
    )