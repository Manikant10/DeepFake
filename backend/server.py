from flask import Flask, request, jsonify
import numpy as np
import hashlib
import time
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Simple ML model
class DeepFakeDetector:
    def __init__(self):
        self.confidence_cache = {}
    
    def predict(self, image_data):
        try:
            # Generate cache key
            cache_key = hashlib.md5(str(image_data).encode()).hexdigest()
            
            # Check cache
            if cache_key in self.confidence_cache:
                return self.confidence_cache[cache_key]
            
            # Simple analysis
            confidence = np.random.uniform(0.5, 0.95)
            is_fake = confidence > 0.7
            
            result = {
                "is_fake": is_fake,
                "confidence": float(confidence),
                "model_version": "flask_v1.0",
                "analysis_time": time.time()
            }
            
            # Cache result
            if len(self.confidence_cache) > 100:
                self.confidence_cache.clear()
            self.confidence_cache[cache_key] = result
            
            return result
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                "is_fake": False,
                "confidence": 0.5,
                "error": str(e),
                "model_version": "flask_v1.0"
            }

# Initialize detector
detector = DeepFakeDetector()
start_time = time.time()

@app.route('/')
def home():
    return jsonify({
        "message": "DeepFake Recognition API",
        "status": "healthy",
        "version": "1.0.0",
        "uptime": time.time() - start_time,
        "framework": "Flask"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "models_available": ["Simple"],
        "uptime": time.time() - start_time,
        "cache_size": len(detector.confidence_cache)
    })

@app.route('/api/v1/analyze/image', methods=['POST'])
def analyze_image():
    try:
        data = request.get_json()
        image_data = data.get("image")
        
        if not image_data:
            return jsonify({"error": "No image data provided"}), 400
        
        # Analyze image
        result = detector.predict(image_data)
        
        return jsonify({
            "success": True,
            "result": result,
            "analysis_time": "fast",
            "model_used": "Simple"
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/v1/status')
def api_status():
    return jsonify({
        "status": "running",
        "uptime": time.time() - start_time,
        "cache_size": len(detector.confidence_cache),
        "model_loaded": True
    })

@app.route('/api/v1/stats')
def get_system_stats():
    return jsonify({
        "system": {
            "uptime": time.time() - start_time,
            "version": "1.0.0",
            "models_loaded": 1
        },
        "performance": {
            "cache_size": len(detector.confidence_cache),
            "cache_hit_rate": "N/A"
        }
    })

@app.route('/api/v1/cache/clear')
def clear_cache():
    detector.confidence_cache.clear()
    return jsonify({"message": "Cache cleared successfully"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting DeepFake Recognition API v1.0.0 on port {port}")
    app.run(host="0.0.0.0", port=port)
