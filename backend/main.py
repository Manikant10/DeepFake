from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import tempfile
import shutil
from pathlib import Path
import uuid
import json
from datetime import datetime
import cv2

from model.deepfake_detector import DeepFakeDetector

app = FastAPI(title="DeepFake Recognition API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
detector = None
UPLOAD_DIR = "uploads"
RESULTS_DIR = "results"

# Create necessary directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Initialize the deepfake detector on startup"""
    global detector
    try:
        detector = DeepFakeDetector()
        print("DeepFake detector initialized successfully")
    except Exception as e:
        print(f"Error initializing detector: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "DeepFake Recognition API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "detector_loaded": detector is not None}

@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    """Analyze an uploaded image for deepfake detection"""
    if detector is None:
        raise HTTPException(status_code=500, detail="Detector not initialized")
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_extension = Path(file.filename).suffix
    filename = f"{file_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Analyze the image
        result = detector.predict(file_path)
        
        # Add metadata
        result.update({
            "file_id": file_id,
            "filename": file.filename,
            "file_size": os.path.getsize(file_path),
            "analysis_type": "image",
            "timestamp": datetime.now().isoformat()
        })
        
        # Save results
        result_path = os.path.join(RESULTS_DIR, f"{file_id}_result.json")
        with open(result_path, "w") as f:
            json.dump(result, f, indent=2)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return result
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/video")
async def analyze_video(file: UploadFile = File(...)):
    """Analyze an uploaded video for deepfake detection"""
    if detector is None:
        raise HTTPException(status_code=500, detail="Detector not initialized")
    
    # Validate file type
    if not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_extension = Path(file.filename).suffix
    filename = f"{file_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Analyze the video
        result = detector.predict_video(file_path)
        
        # Add metadata
        result.update({
            "file_id": file_id,
            "filename": file.filename,
            "file_size": os.path.getsize(file_path),
            "analysis_type": "video",
            "timestamp": datetime.now().isoformat()
        })
        
        # Save results
        result_path = os.path.join(RESULTS_DIR, f"{file_id}_result.json")
        with open(result_path, "w") as f:
            json.dump(result, f, indent=2)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return result
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/results/{file_id}")
async def get_result(file_id: str):
    """Retrieve analysis results by file ID"""
    result_path = os.path.join(RESULTS_DIR, f"{file_id}_result.json")
    
    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Result not found")
    
    with open(result_path, "r") as f:
        result = json.load(f)
    
    return result

@app.get("/results")
async def list_results():
    """List all analysis results"""
    results = []
    
    for filename in os.listdir(RESULTS_DIR):
        if filename.endswith("_result.json"):
            file_id = filename.replace("_result.json", "")
            result_path = os.path.join(RESULTS_DIR, filename)
            
            try:
                with open(result_path, "r") as f:
                    result = json.load(f)
                    results.append({
                        "file_id": file_id,
                        "filename": result.get("filename"),
                        "analysis_type": result.get("analysis_type"),
                        "label": result.get("label"),
                        "confidence": result.get("confidence"),
                        "timestamp": result.get("timestamp")
                    })
            except Exception as e:
                print(f"Error reading result {filename}: {e}")
    
    # Sort by timestamp (newest first)
    results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return {"results": results}

@app.delete("/results/{file_id}")
async def delete_result(file_id: str):
    """Delete analysis results"""
    result_path = os.path.join(RESULTS_DIR, f"{file_id}_result.json")
    
    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Result not found")
    
    os.remove(result_path)
    return {"message": "Result deleted successfully"}

@app.get("/stats")
async def get_stats():
    """Get analysis statistics"""
    results = []
    
    for filename in os.listdir(RESULTS_DIR):
        if filename.endswith("_result.json"):
            result_path = os.path.join(RESULTS_DIR, filename)
            try:
                with open(result_path, "r") as f:
                    result = json.load(f)
                    results.append(result)
            except Exception:
                continue
    
    total_analyses = len(results)
    real_count = sum(1 for r in results if r.get("label") == "REAL")
    fake_count = sum(1 for r in results if r.get("label") == "FAKE")
    image_count = sum(1 for r in results if r.get("analysis_type") == "image")
    video_count = sum(1 for r in results if r.get("analysis_type") == "video")
    
    return {
        "total_analyses": total_analyses,
        "real_detected": real_count,
        "fake_detected": fake_count,
        "image_analyses": image_count,
        "video_analyses": video_count,
        "accuracy_percentage": round((real_count + fake_count) / max(total_analyses, 1) * 100, 2)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
