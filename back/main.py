from const import *

# Create an Fast API App
from fastapi import FastAPI
from routes import auth, info, design
from utils.setup import setup_directories, logger

app = FastAPI()
setup_directories()

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(info.router, prefix="/api/info", tags=["info"])
app.include_router(design.router, prefix="/api/design", tags=["design"])



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