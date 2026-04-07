import React from 'react';
import { motion } from 'framer-motion';
import { Helmet } from 'react-helmet-async';
import { useQuery } from 'react-query';
import {
  Shield,
  TrendingUp,
  Clock,
  Users,
  FileImage,
  FileVideo,
  CheckCircle,
  XCircle,
  BarChart3,
  Activity,
} from 'lucide-react';
import { useAnalysisStore } from '../stores/authStore';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { StatsCard } from '../components/StatsCard';
import { RecentActivity } from '../components/RecentActivity';
import { QuickActions } from '../components/QuickActions';

export const DashboardPage = () => {
  const { getStats } = useAnalysisStore();

  const { data: stats, isLoading, error } = useQuery(
    'system-stats',
    getStats,
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 mb-4">
          <XCircle className="h-12 w-12 mx-auto" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          Error loading dashboard
        </h3>
        <p className="text-gray-500 dark:text-gray-400">
          Unable to load system statistics. Please try again.
        </p>
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>Dashboard - DeepFake Recognition</title>
        <meta name="description" content="DeepFake Recognition system dashboard" />
      </Helmet>

      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Dashboard
            </h1>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Welcome to your DeepFake Recognition dashboard
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-2 px-3 py-1 bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400 rounded-full">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">System Online</span>
            </div>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          <StatsCard
            title="Total Analyses"
            value={stats?.total_analyses || 0}
            icon={Activity}
            color="purple"
            trend="+12%"
            description="Last 30 days"
          />
          <StatsCard
            title="Real Detected"
            value={stats?.real_detected || 0}
            icon={CheckCircle}
            color="green"
            trend="+8%"
            description="Authentic content"
          />
          <StatsCard
            title="Fake Detected"
            value={stats?.fake_detected || 0}
            icon={XCircle}
            color="red"
            trend="+15%"
            description="Manipulated content"
          />
          <StatsCard
            title="Active Users"
            value={stats?.active_users || 0}
            icon={Users}
            color="blue"
            trend="+5%"
            description="Currently online"
          />
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <QuickActions />
        </motion.div>

        {/* Charts and Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Analysis Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-lg shadow p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Analysis Trends
              </h3>
              <BarChart3 className="h-5 w-5 text-gray-400" />
            </div>
            <div className="h-64 flex items-center justify-center text-gray-500 dark:text-gray-400">
              <div className="text-center">
                <BarChart3 className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>Chart visualization coming soon</p>
              </div>
            </div>
          </motion.div>

          {/* Recent Activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <RecentActivity />
          </motion.div>
        </div>

        {/* Additional Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FileImage className="h-8 w-8 text-blue-500" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Image Analyses
                </h3>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {stats?.image_analyses || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FileVideo className="h-8 w-8 text-purple-500" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Video Analyses
                </h3>
                <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {stats?.video_analyses || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Clock className="h-8 w-8 text-green-500" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Avg. Processing Time
                </h3>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {stats?.avg_processing_time ? `${stats.avg_processing_time.toFixed(1)}s` : 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </>
  );
};
