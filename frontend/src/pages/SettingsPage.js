import React from 'react';
import { useAuthStore } from '../stores/authStore';

export const SettingsPage = () => {
  const { user } = useAuthStore();

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
        <div className="text-white text-2xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-xl rounded-lg overflow-hidden">
          <div className="p-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">
              Settings
            </h1>
            
            <div className="text-center py-12">
              <div className="text-gray-500 mb-4">
                Settings configuration coming soon
              </div>
              <div className="text-sm text-gray-400">
                Customize your deepfake detection preferences
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
