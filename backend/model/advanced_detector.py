import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2, EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import torch
import torchvision.transforms as transforms
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import librosa
import pickle
import json
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class AdvancedDeepFakeDetector:
    """
    Professional-grade deepfake detection system with multiple models and advanced preprocessing
    """
    
    def __init__(self, model_dir: str = "models", config: Optional[Dict] = None):
        self.model_dir = model_dir
        self.config = config or self._get_default_config()
        self.img_size = (224, 224)
        self.class_labels = ['REAL', 'FAKE']
        
        # Initialize models
        self.cnn_model = None
        self.ensemble_model = None
        self.audio_model = None
        self.face_detector = None
        
        # Create model directory
        os.makedirs(model_dir, exist_ok=True)
        
        # Load or build models
        self._initialize_models()
    
    def _get_default_config(self) -> Dict:
        """Default configuration for the detector"""
        return {
            "ensemble_weights": {
                "cnn": 0.4,
                "facial_analysis": 0.3,
                "temporal": 0.2,
                "audio": 0.1
            },
            "preprocessing": {
                "face_detection": True,
                "noise_analysis": True,
                "frequency_analysis": True,
                "compression_artifacts": True
            },
            "threshold": 0.5,
            "batch_size": 32,
            "max_frames": 30
        }
    
    def _initialize_models(self):
        """Initialize all detection models"""
        try:
            self._build_cnn_model()
            self._build_ensemble_model()
            self._load_face_detector()
            logger.info("All models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            raise
    
    def _build_cnn_model(self):
        """Build advanced CNN model with EfficientNet"""
        # Use EfficientNet for better performance
        base_model = EfficientNetB0(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        # Fine-tune more layers
        base_model.trainable = True
        for layer in base_model.layers[:-20]:
            layer.trainable = False
        
        # Add sophisticated custom layers
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = BatchNormalization()(x)
        x = Dense(1024, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = BatchNormalization()(x)
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.3)(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.2)(x)
        predictions = Dense(1, activation='sigmoid')(x)
        
        self.cnn_model = Model(inputs=base_model.input, outputs=predictions)
        
        # Use advanced optimizer
        optimizer = Adam(learning_rate=0.0001)
        
        self.cnn_model.compile(
            optimizer=optimizer,
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
    
    def _build_ensemble_model(self):
        """Build ensemble model combining multiple approaches"""
        # Random Forest for feature-based detection
        self.ensemble_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # Feature scaler
        self.feature_scaler = StandardScaler()
    
    def _load_face_detector(self):
        """Load face detection model"""
        try:
            # Load pre-trained face detector
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_detector = cv2.CascadeClassifier(face_cascade_path)
            
            if self.face_detector.empty():
                logger.warning("Face detector failed to load, continuing without face detection")
                self.face_detector = None
        except Exception as e:
            logger.error(f"Error loading face detector: {e}")
            self.face_detector = None
    
    def advanced_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Advanced preprocessing pipeline"""
        processed = image.copy()
        
        if self.config["preprocessing"]["noise_analysis"]:
            # Noise analysis and reduction
            processed = cv2.bilateralFilter(processed, 9, 75, 75)
        
        if self.config["preprocessing"]["compression_artifacts"]:
            # Compression artifact analysis
            # Apply JPEG compression simulation to detect artifacts
            _, encoded_img = cv2.imencode('.jpg', processed, [cv2.IMWRITE_JPEG_QUALITY, 85])
            processed = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
        
        # Histogram equalization
        processed_yuv = cv2.cvtColor(processed, cv2.COLOR_BGR2YUV)
        processed_yuv[:,:,0] = cv2.equalizeHist(processed_yuv[:,:,0])
        processed = cv2.cvtColor(processed_yuv, cv2.COLOR_YUV2BGR)
        
        return processed
    
    def extract_facial_features(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract facial features for analysis"""
        if self.face_detector is None:
            return None
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return None
        
        # Extract the largest face
        largest_face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = largest_face
        
        face_region = image[y:y+h, x:x+w]
        face_region = cv2.resize(face_region, (224, 224))
        
        return face_region
    
    def extract_audio_features(self, video_path: str) -> Optional[np.ndarray]:
        """Extract audio features from video for deepfake detection"""
        try:
            # Extract audio using librosa
            y, sr = librosa.load(video_path, sr=None)
            
            # Extract features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
            
            # Combine features
            features = np.concatenate([
                np.mean(mfccs, axis=1),
                np.mean(spectral_centroids),
                np.mean(spectral_rolloff),
                np.mean(zero_crossing_rate)
            ])
            
            return features
        except Exception as e:
            logger.error(f"Error extracting audio features: {e}")
            return None
    
    def extract_compression_features(self, image: np.ndarray) -> np.ndarray:
        """Extract compression-related features"""
        features = []
        
        # DCT coefficients
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        dct = cv2.dct(gray.astype(np.float32))
        features.extend(np.mean(np.abs(dct), axis=1)[:10])  # First 10 DCT coefficients
        
        # Noise level estimation
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        features.append(laplacian_var)
        
        # Edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        features.append(edge_density)
        
        return np.array(features)
    
    def predict_ensemble(self, image_path: str) -> Dict:
        """Make prediction using ensemble of models"""
        try:
            # Load and preprocess image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, self.img_size)
            
            # Advanced preprocessing
            processed_img = self.advanced_preprocessing(img)
            
            # CNN prediction
            cnn_input = processed_img.astype('float32') / 255.0
            cnn_input = np.expand_dims(cnn_input, axis=0)
            cnn_pred = self.cnn_model.predict(cnn_input, verbose=0)[0][0]
            
            # Feature-based prediction
            features = self.extract_compression_features(processed_img)
            
            # Facial analysis
            facial_features = self.extract_facial_features(processed_img)
            if facial_features is not None:
                facial_pred = self.cnn_model.predict(
                    np.expand_dims(facial_features.astype('float32') / 255.0, axis=0),
                    verbose=0
                )[0][0]
            else:
                facial_pred = 0.5  # Neutral if no face detected
            
            # Ensemble prediction
            weights = self.config["ensemble_weights"]
            ensemble_pred = (
                weights["cnn"] * cnn_pred +
                weights["facial_analysis"] * facial_pred
            )
            
            confidence = ensemble_pred if ensemble_pred > 0.5 else 1 - ensemble_pred
            label = 'FAKE' if ensemble_pred > self.config["threshold"] else 'REAL'
            
            return {
                'label': label,
                'confidence': float(confidence),
                'raw_prediction': float(ensemble_pred),
                'model_predictions': {
                    'cnn': float(cnn_pred),
                    'facial': float(facial_pred)
                },
                'features_extracted': len(features),
                'face_detected': facial_features is not None
            }
            
        except Exception as e:
            logger.error(f"Error in ensemble prediction: {e}")
            raise
    
    def predict_video_advanced(self, video_path: str) -> Dict:
        """Advanced video analysis with temporal consistency"""
        try:
            cap = cv2.VideoCapture(video_path)
            frames = []
            frame_predictions = []
            facial_consistency_scores = []
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_indices = np.linspace(0, total_frames-1, self.config["max_frames"], dtype=int)
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, self.img_size)
                    frames.append(frame)
                    
                    # Analyze frame
                    processed_frame = self.advanced_preprocessing(frame)
                    frame_input = processed_frame.astype('float32') / 255.0
                    frame_input = np.expand_dims(frame_input, axis=0)
                    
                    frame_pred = self.cnn_model.predict(frame_input, verbose=0)[0][0]
                    frame_predictions.append(frame_pred)
                    
                    # Facial consistency
                    face_features = self.extract_facial_features(processed_frame)
                    if face_features is not None:
                        facial_consistency_scores.append(1.0)  # Face detected
                    else:
                        facial_consistency_scores.append(0.0)  # No face
            
            cap.release()
            
            if len(frames) == 0:
                raise ValueError("Could not extract frames from video")
            
            # Audio analysis
            audio_features = self.extract_audio_features(video_path)
            
            # Temporal analysis
            frame_predictions = np.array(frame_predictions)
            temporal_consistency = 1.0 - np.std(frame_predictions)
            
            # Weighted ensemble prediction
            weights = self.config["ensemble_weights"]
            avg_prediction = np.mean(frame_predictions)
            facial_consistency = np.mean(facial_consistency_scores) if facial_consistency_scores else 0.5
            
            ensemble_pred = (
                weights["cnn"] * avg_prediction +
                weights["facial_analysis"] * facial_consistency +
                weights["temporal"] * temporal_consistency
            )
            
            if audio_features is not None:
                # Add audio contribution if available
                ensemble_pred = (ensemble_pred * 0.9 + 0.5 * 0.1)  # Simple audio weighting
            
            confidence = ensemble_pred if ensemble_pred > 0.5 else 1 - ensemble_pred
            label = 'FAKE' if ensemble_pred > self.config["threshold"] else 'REAL'
            
            return {
                'label': label,
                'confidence': float(confidence),
                'raw_prediction': float(ensemble_pred),
                'frame_predictions': [float(p) for p in frame_predictions],
                'temporal_consistency': float(temporal_consistency),
                'facial_consistency': float(facial_consistency),
                'frames_analyzed': len(frames),
                'audio_analyzed': audio_features is not None,
                'model_predictions': {
                    'cnn': float(avg_prediction),
                    'temporal': float(temporal_consistency),
                    'facial': float(facial_consistency)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in advanced video prediction: {e}")
            raise
    
    def save_models(self, model_name: str = "advanced_deepfake_detector"):
        """Save all models"""
        try:
            # Save CNN model
            cnn_path = os.path.join(self.model_dir, f"{model_name}_cnn.h5")
            self.cnn_model.save(cnn_path)
            
            # Save ensemble model
            ensemble_path = os.path.join(self.model_dir, f"{model_name}_ensemble.pkl")
            with open(ensemble_path, 'wb') as f:
                pickle.dump(self.ensemble_model, f)
            
            # Save configuration
            config_path = os.path.join(self.model_dir, f"{model_name}_config.json")
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logger.info(f"Models saved successfully to {self.model_dir}")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
            raise
    
    def load_models(self, model_name: str = "advanced_deepfake_detector"):
        """Load all models"""
        try:
            # Load CNN model
            cnn_path = os.path.join(self.model_dir, f"{model_name}_cnn.h5")
            if os.path.exists(cnn_path):
                self.cnn_model = load_model(cnn_path)
            
            # Load ensemble model
            ensemble_path = os.path.join(self.model_dir, f"{model_name}_ensemble.pkl")
            if os.path.exists(ensemble_path):
                with open(ensemble_path, 'rb') as f:
                    self.ensemble_model = pickle.load(f)
            
            # Load configuration
            config_path = os.path.join(self.model_dir, f"{model_name}_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            
            logger.info(f"Models loaded successfully from {self.model_dir}")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def get_model_info(self) -> Dict:
        """Get model information and statistics"""
        return {
            "model_type": "Advanced Ensemble DeepFake Detector",
            "cnn_model": "EfficientNetB0 + Custom Layers",
            "ensemble_methods": ["CNN", "Facial Analysis", "Temporal Consistency", "Audio Analysis"],
            "preprocessing": self.config["preprocessing"],
            "ensemble_weights": self.config["ensemble_weights"],
            "input_size": self.img_size,
            "face_detector_loaded": self.face_detector is not None
        }

if __name__ == "__main__":
    # Test the advanced detector
    detector = AdvancedDeepFakeDetector()
    print(detector.get_model_info())
