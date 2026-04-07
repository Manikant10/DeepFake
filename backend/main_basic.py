from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="DeepFake Recognition API",
    description="Professional deepfake detection platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will be updated with specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "DeepFake Recognition API - Running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "deepfake-api"}

@app.get("/docs")
async def docs():
    return {"message": "API Documentation available at /docs", "docs": "/docs"}

@app.get("/api/v1/status")
async def api_status():
    return {
        "api_version": "1.0.0",
        "status": "running",
        "features": {
            "authentication": True,
            "deepfake_detection": False,  # Will be enabled after ML models
            "database": True
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
