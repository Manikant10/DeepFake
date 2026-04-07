import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pickle
import json

class DeepFakeDetector:
    def __init__(self, model_path=None):
        self.model = None
        self.img_size = (224, 224)
        self.class_labels = ['REAL', 'FAKE']
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.build_model()
    
    def build_model(self):
        """Build the deepfake detection model using transfer learning"""
        base_model = MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        # Freeze the base model layers
        base_model.trainable = False
        
        # Add custom layers
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.3)(x)
        predictions = Dense(1, activation='sigmoid')(x)
        
        self.model = Model(inputs=base_model.input, outputs=predictions)
        
        self.model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        print("Model built successfully!")
    
    def preprocess_image(self, image_path):
        """Preprocess a single image for prediction"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, self.img_size)
        img = img.astype('float32') / 255.0
        img = np.expand_dims(img, axis=0)
        
        return img
    
    def predict(self, image_path):
        """Make prediction on a single image"""
        if self.model is None:
            raise ValueError("Model not loaded or built")
        
        processed_img = self.preprocess_image(image_path)
        prediction = self.model.predict(processed_img)[0][0]
        
        confidence = prediction if prediction > 0.5 else 1 - prediction
        label = 'FAKE' if prediction > 0.5 else 'REAL'
        
        return {
            'label': label,
            'confidence': float(confidence),
            'raw_prediction': float(prediction)
        }
    
    def extract_video_frames(self, video_path, max_frames=10):
        """Extract frames from video for analysis"""
        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Sample frames evenly throughout the video
        frame_indices = np.linspace(0, total_frames-1, max_frames, dtype=int)
        
        for frame_idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, self.img_size)
                frames.append(frame)
                frame_count += 1
        
        cap.release()
        
        if len(frames) == 0:
            raise ValueError("Could not extract frames from video")
        
        return np.array(frames)
    
    def predict_video(self, video_path):
        """Make prediction on video by analyzing multiple frames"""
        frames = self.extract_video_frames(video_path)
        frames = frames.astype('float32') / 255.0
        
        predictions = []
        for frame in frames:
            frame_batch = np.expand_dims(frame, axis=0)
            pred = self.model.predict(frame_batch, verbose=0)[0][0]
            predictions.append(pred)
        
        avg_prediction = np.mean(predictions)
        confidence = avg_prediction if avg_prediction > 0.5 else 1 - avg_prediction
        label = 'FAKE' if avg_prediction > 0.5 else 'REAL'
        
        # Analyze prediction consistency
        std_dev = np.std(predictions)
        consistency = 1.0 - min(std_dev, 0.5) * 2  # Normalize to 0-1
        
        return {
            'label': label,
            'confidence': float(confidence),
            'raw_prediction': float(avg_prediction),
            'frame_predictions': [float(p) for p in predictions],
            'consistency_score': float(consistency),
            'frames_analyzed': len(frames)
        }
    
    def save_model(self, path):
        """Save the trained model"""
        if self.model:
            self.model.save(path)
            print(f"Model saved to {path}")
        else:
            raise ValueError("No model to save")
    
    def load_model(self, path):
        """Load a trained model"""
        self.model = tf.keras.models.load_model(path)
        print(f"Model loaded from {path}")
    
    def get_model_summary(self):
        """Get model architecture summary"""
        if self.model:
            self.model.summary()
        else:
            print("No model available")

# Utility function to create dummy data for testing
def create_dummy_data(output_dir="dummy_data", num_samples=100):
    """Create dummy data for testing purposes"""
    os.makedirs(f"{output_dir}/REAL", exist_ok=True)
    os.makedirs(f"{output_dir}/FAKE", exist_ok=True)
    
    # Create dummy images (random noise)
    for i in range(num_samples // 2):
        # Real images
        real_img = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
        cv2.imwrite(f"{output_dir}/REAL/real_{i}.jpg", real_img)
        
        # Fake images
        fake_img = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
        cv2.imwrite(f"{output_dir}/FAKE/fake_{i}.jpg", fake_img)
    
    print(f"Created {num_samples} dummy images in {output_dir}")

if __name__ == "__main__":
    # Test the detector
    detector = DeepFakeDetector()
    detector.get_model_summary()
    
    # Create dummy data for testing
    create_dummy_data()
