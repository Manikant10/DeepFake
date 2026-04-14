import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { motion, AnimatePresence } from 'framer-motion';

export const ProfessionalAnalysisPage = () => {
  const { user } = useAuthStore();
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedModel, setSelectedModel] = useState('ensemble');
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    // Simulate real-time progress updates
    if (isAnalyzing) {
      const interval = setInterval(() => {
        setAnalysisProgress(prev => Math.min(prev + 10, 100));
      }, 500);
      
      return () => clearInterval(interval);
    }
  }, [isAnalyzing]);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setResults(null);
    setAnalysisProgress(0);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragActive(false);
  };

  const handleDrop = ( (e) => {
    e.preventDefault();
    setDragActive(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    setAnalysisProgress(0);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('model', selectedModel);
      
      const response = await fetch('/api/v1/analyze/image', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      setResults(result);
      
      // Add to uploaded files history
      const newFile = {
        id: Date.now(),
        name: selectedFile.name,
        size: selectedFile.size,
        type: selectedFile.type,
        timestamp: new Date().toISOString(),
        result: result.result
      };
      setUploadedFiles(prev => [newFile, ...prev]);
      
    } catch (error) {
      console.error('Analysis error:', error);
    } finally {
      setIsAnalyzing(false);
      setAnalysisProgress(100);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceIcon = (isFake, confidence) => {
    if (isFake && confidence >= 0.8) return '⚠️';
    if (isFake && confidence >= 0.6) return '⚡';
    if (!isFake && confidence >= 0.8) return '✅';
    return '❓';
  };

  if (!user) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center"
      >
        <LoadingSpinner size="lg" />
      </motion.div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
      >
        <div className="bg-white shadow-xl rounded-2xl overflow-hidden">
          <div className="p-8">
            <motion.h1
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="text-4xl font-bold text-gray-900 mb-2"
            >
              Professional Deepfake Analysis
            </motion.h1>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-gray-600 mb-8"
            >
              Advanced AI-powered deepfake detection with ensemble models
            </motion.p>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
              {/* Model Selection */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
                className="bg-gray-50 p-6 rounded-lg border border-gray-200"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  AI Model
                </h3>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="ensemble">Ensemble (Recommended)</option>
                  <option value="random_forest">Random Forest</option>
                  <option value="gradient_boosting">Gradient Boosting</option>
                </select>
              </motion.div>

              {/* File Upload */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
                className="bg-gray-50 p-6 rounded-lg border border-gray-200"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Upload File
                </h3>
                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-all ${
                    dragActive ? 'border-purple-500 bg-purple-50' : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                >
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleFileSelect(e.target.files[0])}
                    className="hidden"
                    id="file-upload"
                  />
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer flex flex-col items-center justify-center space-y-2"
                  >
                    <motion.div
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-4"
                    >
                      <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.587 3.418l-2.292 2.292A4 4 0 011.414 0l2.292-2.292a4 4 0 011.414 0L7 18m0 4a4 4 0 01-4 4m0-4a4 4 0 004 4m0 4a4 4 0 004-4" />
                      </svg>
                    </motion.div>
                    <span className="text-gray-700 font-medium">
                      {selectedFile ? selectedFile.name : 'Click to upload or drag & drop'}
                    </span>
                    <span className="text-sm text-gray-500">
                      Supports: JPG, PNG, GIF (Max 10MB)
                    </span>
                  </label>
                </div>
              </motion.div>

              {/* Analysis Progress */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.5 }}
                className="bg-gray-50 p-6 rounded-lg border border-gray-200"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Analysis Progress
                </h3>
                {isAnalyzing ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Processing...</span>
                      <span className="text-sm font-medium text-purple-600">{analysisProgress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <motion.div
                        className="bg-purple-600 h-2 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${analysisProgress}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                    <div className="text-xs text-gray-500 mt-2">
                      Extracting features, analyzing with ensemble models...
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    Upload a file to see analysis progress
                  </div>
                )}
              </motion.div>
            </div>

            {/* Results Section */}
            <AnimatePresence>
              {results && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.5 }}
                  className="bg-gradient-to-r from-purple-50 to-blue-50 p-8 rounded-xl border border-purple-200"
                >
                  <div className="text-center">
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.3, delay: 0.2 }}
                      className="inline-flex items-center justify-center w-20 h-20 bg-white rounded-full mb-4"
                    >
                      <span className="text-3xl">
                        {getConfidenceIcon(results.result.is_fake, results.result.confidence)}
                      </span>
                    </motion.div>
                    
                    <h3 className={`text-2xl font-bold mb-2 ${getConfidenceColor(results.result.confidence)}`}>
                      {results.result.is_fake ? '🚨 FAKE DETECTED' : '✅ AUTHENTIC'}
                    </h3>
                    
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.5, delay: 0.3 }}
                      className="space-y-4"
                    >
                      <div className="bg-white p-6 rounded-lg shadow-sm">
                        <h4 className="font-semibold text-gray-900 mb-2">Confidence Score</h4>
                        <div className="flex items-center justify-center">
                          <div className="text-4xl font-bold text-purple-600">
                            {(results.result.confidence * 100).toFixed(1)}%
                          </div>
                        </div>
                        <div className="mt-2 h-2 bg-gray-200 rounded-full">
                          <div
                            className={`h-2 rounded-full transition-all duration-500 ${
                              results.result.confidence >= 0.8 ? 'bg-green-500' :
                              results.result.confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${results.result.confidence * 100}%` }}
                          />
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 mt-4">
                        <div className="text-center">
                          <p className="text-sm text-gray-600">Processing Time</p>
                          <p className="text-lg font-semibold">{results.processing_time.toFixed(2)}s</p>
                        </div>
                        <div className="text-center">
                          <p className="text-sm text-gray-600">Model Used</p>
                          <p className="text-lg font-semibold">{results.model_info.model_used}</p>
                        </div>
                      </div>
                    </motion.div>
                    
                    <div className="mt-6 bg-white p-6 rounded-lg shadow-sm">
                      <h4 className="font-semibold text-gray-900 mb-2">Technical Details</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Model Version:</span>
                          <span className="font-medium">{results.result.model_version}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Features Extracted:</span>
                          <span className="font-medium">{results.result.feature_count}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Ensemble Models:</span>
                          <span className="font-medium">{results.result.ensemble_models.join(', ')}</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default ProfessionalAnalysisPage;
