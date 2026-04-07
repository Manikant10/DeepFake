import React from 'react';
import { motion } from 'framer-motion';
import { Clock, CheckCircle, XCircle, FileImage, FileVideo } from 'lucide-react';
import { useQuery } from 'react-query';
import { useAnalysisStore } from '../stores/authStore';

export const RecentActivity = () => {
  const { getAnalyses } = useAnalysisStore();

  const { data: analyses, isLoading } = useQuery(
    'recent-analyses',
    () => getAnalyses(1, 5),
    {
      refetchInterval: 30000,
    }
  );

  const getActivityIcon = (fileType, result) => {
    if (fileType === 'image') {
      return <FileImage className="h-4 w-4" />;
    } else {
      return <FileVideo className="h-4 w-4" />;
    }
  };

  const getResultColor = (result) => {
    return result === 'REAL' ? 'text-green-500' : 'text-red-500';
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diff = now - time;

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          Recent Activity
        </h3>
        <Clock className="h-5 w-5 text-gray-400" />
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mt-2"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : analyses && analyses.length > 0 ? (
        <div className="space-y-3">
          {analyses.map((analysis, index) => (
            <motion.div
              key={analysis.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <div className={`flex-shrink-0 p-2 rounded-lg ${
                analysis.label === 'REAL' 
                  ? 'bg-green-100 dark:bg-green-900/20' 
                  : 'bg-red-100 dark:bg-red-900/20'
              }`}>
                {getActivityIcon(analysis.file_type, analysis.label)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {analysis.file_name}
                  </p>
                  <span className={`text-xs font-medium ${getResultColor(analysis.label)}`}>
                    {analysis.label}
                  </span>
                </div>
                <div className="flex items-center space-x-2 mt-1">
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {formatTimeAgo(analysis.created_at)}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {(analysis.confidence * 100).toFixed(1)}% confidence
                  </span>
                </div>
              </div>

              <div className="flex-shrink-0">
                {analysis.label === 'REAL' ? (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                ) : (
                  <XCircle className="h-4 w-4 text-red-500" />
                )}
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <div className="text-gray-400 mb-2">
            <Clock className="h-8 w-8 mx-auto" />
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            No recent activity
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
            Start analyzing media to see activity here
          </p>
        </div>
      )}
    </div>
  );
};
