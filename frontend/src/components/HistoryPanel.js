import React, { useState, useEffect } from 'react';
import { Trash2, Eye, Calendar, FileImage, FileVideo, CheckCircle, XCircle } from 'lucide-react';
import axios from 'axios';

const HistoryPanel = ({ history, onHistoryUpdate }) => {
  const [selectedResult, setSelectedResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleDelete = async (fileId) => {
    if (!window.confirm('Are you sure you want to delete this analysis result?')) {
      return;
    }

    setLoading(true);
    try {
      await axios.delete(`http://localhost:8000/results/${fileId}`);
      onHistoryUpdate(); // Refresh history
    } catch (error) {
      console.error('Error deleting result:', error);
      alert('Failed to delete result');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (fileId) => {
    try {
      const response = await axios.get(`http://localhost:8000/results/${fileId}`);
      setSelectedResult(response.data);
    } catch (error) {
      console.error('Error fetching result details:', error);
      alert('Failed to fetch result details');
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-50';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <div className="result-card">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-gray-800">Analysis History</h3>
        <span className="text-sm text-gray-600">
          {history.length} {history.length === 1 ? 'analysis' : 'analyses'}
        </span>
      </div>

      {history.length === 0 ? (
        <div className="text-center py-8">
          <Calendar className="w-16 h-16 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600">No analysis history available</p>
          <p className="text-sm text-gray-500 mt-2">Upload and analyze files to see them here</p>
        </div>
      ) : (
        <div className="space-y-4">
          {history.map((item) => (
            <div
              key={item.file_id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    {item.analysis_type === 'image' ? (
                      <FileImage className="w-8 h-8 text-blue-500" />
                    ) : (
                      <FileVideo className="w-8 h-8 text-purple-500" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {item.filename}
                    </p>
                    <div className="flex items-center space-x-4 mt-1">
                      <span className="text-xs text-gray-500">
                        {formatDate(item.timestamp)}
                      </span>
                      <span className="text-xs text-gray-500">
                        {formatFileSize(item.file_size)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2">
                    {item.label === 'REAL' ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-500" />
                    )}
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      item.label === 'REAL' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {item.label}
                    </span>
                  </div>
                  
                  <div className={`px-2 py-1 rounded text-xs font-medium ${getConfidenceColor(item.confidence)}`}>
                    {(item.confidence * 100).toFixed(1)}%
                  </div>

                  <div className="flex space-x-1">
                    <button
                      onClick={() => handleViewDetails(item.file_id)}
                      className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                      title="View details"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(item.file_id)}
                      disabled={loading}
                      className="p-1 text-red-600 hover:bg-red-50 rounded disabled:opacity-50"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Details Modal */}
      {selectedResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-screen overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-bold text-gray-900">Analysis Details</h3>
                <button
                  onClick={() => setSelectedResult(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-gray-600">File Name:</span>
                    <p className="font-medium">{selectedResult.filename}</p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Analysis Type:</span>
                    <p className="font-medium capitalize">{selectedResult.analysis_type}</p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Result:</span>
                    <div className="flex items-center mt-1">
                      {selectedResult.label === 'REAL' ? (
                        <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-500 mr-2" />
                      )}
                      <span className={`font-bold ${
                        selectedResult.label === 'REAL' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {selectedResult.label}
                      </span>
                    </div>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Confidence:</span>
                    <p className="font-medium">{(selectedResult.confidence * 100).toFixed(2)}%</p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">File Size:</span>
                    <p className="font-medium">{formatFileSize(selectedResult.file_size)}</p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Analysis Date:</span>
                    <p className="font-medium">{formatDate(selectedResult.timestamp)}</p>
                  </div>
                </div>

                {selectedResult.frame_predictions && (
                  <div>
                    <span className="text-sm text-gray-600">Frame Analysis:</span>
                    <div className="mt-2 p-3 bg-gray-50 rounded">
                      <p className="text-sm">
                        <span className="font-medium">Frames Analyzed:</span> {selectedResult.frames_analyzed}
                      </p>
                      <p className="text-sm mt-1">
                        <span className="font-medium">Consistency Score:</span> {(selectedResult.consistency_score * 100).toFixed(2)}%
                      </p>
                      <div className="mt-2">
                        <span className="text-sm font-medium">Frame Predictions:</span>
                        <div className="mt-1 flex flex-wrap gap-1">
                          {selectedResult.frame_predictions.map((pred, index) => (
                            <span
                              key={index}
                              className={`px-2 py-1 text-xs rounded ${
                                pred > 0.5 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                              }`}
                            >
                              {pred > 0.5 ? 'FAKE' : 'REAL'} ({(pred * 100).toFixed(0)}%)
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t">
                  <button
                    onClick={() => setSelectedResult(null)}
                    className="w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HistoryPanel;
