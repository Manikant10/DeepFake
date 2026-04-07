import React from 'react';
import { motion } from 'framer-motion';
import { Outlet } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { useAuthStore } from '../stores/authStore';

export const Layout = () => {
  const { user } = useAuthStore();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Helmet>
        <title>DeepFake Recognition System</title>
        <meta name="description" content="Professional deepfake detection platform" />
      </Helmet>

      <div className="flex">
        {/* Sidebar */}
        <Sidebar />

        {/* Main content */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <Header user={user} />

          {/* Page content */}
          <main className="flex-1 p-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Outlet />
            </motion.div>
          </main>
        </div>
      </div>
    </div>
  );
};
