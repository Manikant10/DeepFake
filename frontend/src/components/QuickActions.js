import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Upload, FileImage, FileVideo, ArrowRight } from 'lucide-react';

export const QuickActions = () => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
        Quick Actions
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link to="/analysis">
          <motion.div
            whileHover={{ scale: 1.02 }}
            className="flex items-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer"
          >
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
                <Upload className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                New Analysis
              </h4>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Upload and analyze media
              </p>
            </div>
            <ArrowRight className="h-4 w-4 text-gray-400" />
          </motion.div>
        </Link>

        <Link to="/history">
          <motion.div
            whileHover={{ scale: 1.02 }}
            className="flex items-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer"
          >
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                <FileImage className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                View History
              </h4>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Browse past analyses
              </p>
            </div>
            <ArrowRight className="h-4 w-4 text-gray-400" />
          </motion.div>
        </Link>

        <Link to="/api-keys">
          <motion.div
            whileHover={{ scale: 1.02 }}
            className="flex items-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer"
          >
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                <FileVideo className="h-5 w-5 text-green-600 dark:text-green-400" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                API Access
              </h4>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Manage API keys
              </p>
            </div>
            <ArrowRight className="h-4 w-4 text-gray-400" />
          </motion.div>
        </Link>

        <Link to="/settings">
          <motion.div
            whileHover={{ scale: 1.02 }}
            className="flex items-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer"
          >
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                <Upload className="h-5 w-5 text-gray-600 dark:text-gray-400" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                Settings
              </h4>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Configure preferences
              </p>
            </div>
            <ArrowRight className="h-4 w-4 text-gray-400" />
          </motion.div>
        </Link>
      </div>
    </div>
  );
};
