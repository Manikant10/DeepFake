import React, { useState } from 'react';
import { useAuthStore } from '../stores/authStore';
import { LoadingSpinner } from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import { extractErrorMessageFromResponse, extractErrorMessage, toSafeNumber } from '../utils/http';

export const AnalysisPage = () => {
  const { user } = useAuthStore();
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  const validateFile = (file) => {
    if (!file) return 'Please select a file before running analysis.';
    if (!file.type?.startsWith('image/') && !file.type?.startsWith('video/')) {
      return 'Unsupported file format. Upload an image or video file.';
    }

    const maxSizeInBytes = file.type.startsWith('video/')
      ? 100 * 1024 * 1024
      : 50 * 1024 * 1024;

    if (file.size > maxSizeInBytes) {
      return `File is too large. Maximum size is ${file.type.startsWith('video/') ? '100MB' : '50MB'}.`;
    }

    return '';
  };

  const handleFileSelect = (file) => {
    const validationError = validateFile(file);
    if (validationError) {
      setSelectedFile(null);
      setErrorMessage(validationError);
      toast.error(validationError);
      return;
    }
    setSelectedFile(file);
    setResults(null);
    setErrorMessage('');
  };

  const handleAnalyze = async () => {
    const validationError = validateFile(selectedFile);
    if (validationError) {
      setErrorMessage(validationError);
      toast.error(validationError);
      return;
    }

    setIsAnalyzing(true);
    setErrorMessage('');
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      const response = await fetch('/api/v1/analyze/image', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const apiError = await extractErrorMessageFromResponse(
          response,
          `Analysis request failed (${response.status}).`
        );
        throw new Error(apiError);
      }
      
      const payload = await response.json();
      const result = payload?.result ?? payload;

      if (typeof result?.is_fake !== 'boolean' || Number.isNaN(Number(result?.confidence))) {
        throw new Error('The server returned an unexpected analysis response.');
      }

      setResults({
        ...result,
        confidence: toSafeNumber(result.confidence, 0),
        model_used: payload?.model_info?.model_used || result?.model_used || 'Unknown',
        processing_time: toSafeNumber(payload?.processing_time ?? result?.processing_time, 0),
      });
      toast.success('Analysis completed successfully.');
    } catch (error) {
      const message = extractErrorMessage(error, 'Unable to analyze the file right now.');
      setErrorMessage(message);
      toast.error(message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-xl rounded-lg overflow-hidden">
          <div className="p-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">
              Deepfake Analysis
            </h1>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* File Upload Section */}
              <div className="bg-gray-50 p-6 rounded-lg">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Upload File
                </h2>
                <p className="text-sm text-gray-500 mb-4">
                  Supported formats: images and videos. Max size: 50MB (images), 100MB (videos).
                </p>
                
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <input
                    type="file"
                    accept="image/*,video/*"
                    onChange={(e) => handleFileSelect(e.target.files[0])}
                    className="hidden"
                    id="file-upload"
                  />
                  <label 
                    htmlFor="file-upload"
                    className="cursor-pointer bg-white text-gray-700 hover:text-gray-900 font-medium py-4 px-6 rounded-lg border border-gray-300 hover:border-gray-400 transition-colors"
                  >
                    {selectedFile ? selectedFile.name : 'Choose file to analyze'}
                  </label>
                </div>
                
                {selectedFile && (
                  <button
                    onClick={handleAnalyze}
                    disabled={isAnalyzing}
                    className="w-full bg-purple-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 transition-colors"
                  >
                    {isAnalyzing ? 'Analyzing...' : 'Analyze File'}
                  </button>
                )}

                {errorMessage && (
                  <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {errorMessage}
                  </div>
                )}
              </div>

              {/* Results Section */}
              <div className="bg-gray-50 p-6 rounded-lg">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Analysis Results
                </h2>
                
                {results ? (
                  <div className="space-y-4">
                    <div className={`p-4 rounded-lg ${
                      results.is_fake ? 'bg-red-100 border-red-200' : 'bg-green-100 border-green-200'
                    }`}>
                      <h3 className={`text-lg font-semibold ${
                        results.is_fake ? 'text-red-800' : 'text-green-800'
                      }`}>
                        {results.is_fake ? 'Potential Manipulation Detected' : 'Content Appears Authentic'}
                      </h3>
                      <p className="text-gray-700">
                        Confidence: {(results.confidence * 100).toFixed(1)}%
                      </p>
                      <p className="text-sm text-gray-600">
                        Model: {results.model_used}
                      </p>
                      <p className="text-sm text-gray-600">
                        Processing time: {results.processing_time.toFixed(2)}s
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    Upload a file to see analysis results
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisPage;
