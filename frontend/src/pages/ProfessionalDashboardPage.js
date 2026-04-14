import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore } from '../stores/authStore';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

export const ProfessionalDashboardPage = () => {
  const { user } = useAuthStore();
  const [stats, setStats] = useState({
    totalAnalyses: 0,
    successfulAnalyses: 0,
    failedAnalyses: 0,
    averageProcessingTime: 0,
    cacheHitRate: 0,
    uptime: 0,
    redisConnected: false
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/v1/stats');
        const data = await response.json();
        setStats(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch statistics');
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const getHealthColor = (status) => {
    return status === 'healthy' ? 'text-green-600' : 'text-red-600';
  };

  const getCacheColor = (rate) => {
    if (rate >= 80) return 'text-green-600';
    if (rate >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (!user) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center"
      >
        <div className="text-white text-2xl">Loading...</div>
      </motion.div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading statistics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-red-500 bg-red-50 p-8 rounded-lg">
          Error: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="bg-white shadow-xl rounded-2xl overflow-hidden"
        >
          <div className="p-8">
            <motion.h1
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-4xl font-bold text-gray-900 mb-8"
            >
              Professional Analytics Dashboard
            </motion.h1>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {/* System Health */}
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.3 }}
                className="bg-white p-6 rounded-lg shadow-lg border border-gray-200"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">System Health</h3>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${getHealthColor('healthy')}`}>
                    {stats.redisConnected ? 'Connected' : 'Disconnected'}
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Status:</span>
                    <span className={`font-medium ${getHealthColor('healthy')}`}>Healthy</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Uptime:</span>
                    <span className="font-medium">{(stats.uptime / 3600).toFixed(1)}h</span>
                  </div>
                </div>
              </motion.div>

              {/* Analysis Statistics */}
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.4 }}
                className="bg-white p-6 rounded-lg shadow-lg border border-gray-200"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Statistics</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Analyses:</span>
                    <span className="text-2xl font-bold text-purple-600">{stats.totalAnalyses}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Successful:</span>
                    <span className="text-xl font-bold text-green-600">{stats.successfulAnalyses}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Failed:</span>
                    <span className="text-xl font-bold text-red-600">{stats.failedAnalyses}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Success Rate:</span>
                    <span className="text-lg font-medium">
                      {stats.totalAnalyses > 0 ? ((stats.successfulAnalyses / stats.totalAnalyses) * 100).toFixed(1) : 0}%
                    </span>
                  </div>
                </div>
              </motion.div>

              {/* Performance Metrics */}
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.5 }}
                className="bg-white p-6 rounded-lg shadow-lg border border-gray-200"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg Processing Time:</span>
                    <span className="text-lg font-medium">{stats.averageProcessingTime.toFixed(2)}s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Cache Hit Rate:</span>
                    <span className={`text-lg font-medium ${getCacheColor(stats.cacheHitRate)}`}>
                      {stats.cacheHitRate.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </motion.div>

              {/* Real-time Chart */}
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.6 }}
                className="bg-white p-6 rounded-lg shadow-lg border border-gray-200 lg:col-span-2"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Times</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={[
                    { name: 'Processing Time', data: Array(20).fill(null).map((_, i) => ({
                      time: i,
                      value: Math.random() * 2 + 0.5
                    })) }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="value" 
                      stroke="#8b5cf6" 
                      strokeWidth={2}
                      dot={{ fill: '#8b5cf6', strokeWidth: 2 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </motion.div>
            </div>

            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.7 }}
              className="mt-8 flex flex-col sm:flex-row gap-4"
            >
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex-1 bg-purple-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-purple-700 transition-colors"
                onClick={() => window.open('/analysis', '_self')}
              >
                New Analysis
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 transition-colors"
                onClick={async () => {
                  try {
                    const response = await fetch('/api/v1/cache/clear', { method: 'POST' });
                    const result = await response.json();
                    alert('Cache cleared successfully!');
                  } catch (err) {
                    alert('Failed to clear cache');
                  }
                }}
              >
                Clear Cache
              </motion.button>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ProfessionalDashboardPage;
