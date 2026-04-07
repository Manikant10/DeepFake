# DeepFake Recognition System

A comprehensive full-stack application for detecting deepfakes in images and videos using advanced machine learning techniques.

## Features

- **Multi-format Support**: Analyze both images (JPEG, PNG, GIF) and videos (MP4, AVI, MOV)
- **Advanced ML Model**: Built with TensorFlow and MobileNetV2 for accurate detection
- **Real-time Processing**: Fast analysis with confidence scoring
- **Beautiful GUI**: Modern React frontend with Tailwind CSS
- **Analysis History**: Track and manage previous analyses
- **Statistical Dashboard**: Visual charts and insights
- **RESTful API**: Clean backend API with FastAPI

## Architecture

```
deepfake-recognition/
  frontend/          # React frontend application
    src/
      components/    # React components
      App.js         # Main application
  backend/           # Python backend API
    model/          # ML model implementation
    main.py         # FastAPI server
  requirements.txt   # Python dependencies
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- pip or conda

### Backend Setup

1. Navigate to the project directory:
```bash
cd deepfake-recognition
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the backend server:
```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Usage

1. **Upload Files**: Drag and drop or browse to upload images/videos
2. **Analyze**: Click "Analyze File" to process the media
3. **View Results**: Get instant feedback with confidence scores
4. **History**: Track all previous analyses
5. **Statistics**: View system-wide analytics and trends

## API Endpoints

- `POST /analyze/image` - Analyze uploaded images
- `POST /analyze/video` - Analyze uploaded videos
- `GET /results` - List all analysis results
- `GET /results/{file_id}` - Get specific analysis result
- `GET /stats` - Get system statistics
- `DELETE /results/{file_id}` - Delete analysis result

## Model Architecture

The deepfake detection model uses:
- **Base Architecture**: MobileNetV2 (transfer learning)
- **Custom Layers**: Dense layers with dropout for classification
- **Input**: 224x224 RGB images/video frames
- **Output**: Binary classification (REAL/FAKE) with confidence score

## Technical Details

### Image Processing
- Resizing to 224x224 pixels
- Normalization to [0,1] range
- RGB color space conversion

### Video Processing
- Frame extraction at regular intervals
- Multi-frame analysis
- Consistency scoring across frames

### Confidence Scoring
- High confidence: 80-100%
- Medium confidence: 60-79%
- Low confidence: 0-59%

## File Size Limits

- Images: Up to 50MB
- Videos: Up to 100MB
- Supported formats: JPEG, PNG, GIF, MP4, AVI, MOV

## Performance

- Image analysis: ~2-5 seconds
- Video analysis: ~10-60 seconds (depending on length and complexity)
- Concurrent processing: Multiple files supported

## Development

### Adding New Features

1. **Model Updates**: Modify `backend/model/deepfake_detector.py`
2. **API Changes**: Update `backend/main.py`
3. **Frontend**: Add components in `frontend/src/components/`

### Training Custom Models

To train with your own dataset:

1. Prepare data in `data/REAL` and `data/FAKE` folders
2. Use the training script (can be added to `backend/model/`)
3. Save trained model as `model/deepfake_model.h5`

## Troubleshooting

### Common Issues

1. **Model Loading Errors**: Ensure all dependencies are installed
2. **File Upload Issues**: Check file size and format restrictions
3. **Memory Issues**: Reduce batch size or frame count for video processing
4. **CORS Errors**: Ensure frontend is running on localhost:3000

### Logs

- Backend logs: Console output from FastAPI server
- Frontend logs: Browser developer tools console

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and research purposes. Please ensure compliance with applicable laws and regulations when using deepfake detection technology.

## Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation at `http://localhost:8000/docs`
- Open an issue on the project repository

---

**Note**: This system uses machine learning models for detection. Results should be used as part of a comprehensive analysis strategy and not as the sole determinant for content authenticity.
