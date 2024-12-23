from fastapi.staticfiles import StaticFiles
from const import *
from utils.setup import setup_directories, logger
from utils.smtp import smtp_utils

# Create an Fast API App
from routes import auth, info, design, user, order, product, analytics

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

origins = [
    "https://poodle-feasible-sadly.ngrok-free.app",
    "https://aitshirts.in",
    "http://localhost:8000",
    "http://localhost:3000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Initialize FastAPI app
app = FastAPI(
    title="AI T-Shirt Design API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

setup_directories()

@app.on_event("startup")
async def startup_event():
    smtp_utils.start_session()

@app.on_event("shutdown")
async def shutdown_event():
    smtp_utils.close_session()


app.mount("/images", StaticFiles(directory=OUTPUTS_DIR), name="images")

@app.get("/")
async def root():
    return RedirectResponse(url="/api/info/health")


app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(design.router, prefix="/api/design", tags=["Design"])
app.include_router(info.router, prefix="/api/info", tags=["Info"])
app.include_router(order.router, prefix="/api/order", tags=["Order"])
app.include_router(product.router, prefix="/api/product", tags=["Product"])
app.include_router(user.router, prefix="/api/user", tags=["User"])



# ! Websocket Worker




if __name__ == "__main__":
    import uvicorn
        
    if STAGE == "DEV":
        from pyngrok import ngrok
        
        # Configure ngrok with your auth token (required for custom domains)
        ngrok.set_auth_token(NGROK_TOKEN)  # Make sure to add your token
        
        # Connect with your custom domain
        try:
            # Use your static domain
            tunnel = ngrok.connect(
                addr=PORT,
                proto="http",
                hostname="poodle-feasible-sadly.ngrok-free.app"  # Your static domain
            )
            logger.info(f"FastAPI is accessible at: {tunnel.public_url}")
        except Exception as e:
            logger.error(f"Failed to establish ngrok tunnel: {str(e)}")
            
    logger.info(f"Server initialization complete. Starting server on {HOST}:{PORT}")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
        workers=1,
        log_level="info"
    )