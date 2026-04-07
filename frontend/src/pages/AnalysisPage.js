import React, { useState } from 'react';
import { useAuthStore } from '../stores/authStore';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const AnalysisPage = () => {
  const { user } = useAuthStore();
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState(null);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setResults(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      const response = await fetch('/api/v1/analyze/image', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      setResults(result);
    } catch (error) {
      console.error('Analysis error:', error);
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
                        {results.is_fake ? 'FAKE DETECTED' : 'REAL DETECTED'}
                      </h3>
                      <p className="text-gray-700">
                        Confidence: {(results.confidence * 100).toFixed(1)}%
                      </p>
                      <p className="text-sm text-gray-600">
                        Model: {results.model_used || 'RandomForest v1.0'}
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
