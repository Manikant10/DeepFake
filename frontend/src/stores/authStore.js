import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import axios from 'axios';

// Configure axios defaults
axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'https://deepfake-backend.onrender.com';

// Add request interceptor for auth token
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for token refresh
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post('/auth/refresh', {
            refresh_token: refreshToken
          });

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);

          // Retry the original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return axios(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export const useAuthStore = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      refreshToken: null,
      isLoading: false,
      isAuthenticated: false,

      // Actions
      login: async (credentials) => {
        set({ isLoading: true });
        try {
          const response = await axios.post('/auth/login', credentials);
          const { access_token, refresh_token } = response.data;

          // Store tokens
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);

          // Get user info
          const userResponse = await axios.get('/auth/me');
          const user = userResponse.data;

          set({
            user,
            token: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
          });

          return { success: true };
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      register: async (userData) => {
        set({ isLoading: true });
        try {
          const response = await axios.post('/auth/register', userData);
          const user = response.data;

          set({ isLoading: false });
          return { success: true, user };
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: async () => {
        try {
          // Call logout endpoint if available
          await axios.post('/auth/logout');
        } catch (error) {
          // Continue with logout even if API call fails
        } finally {
          // Clear local storage
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');

          // Reset state
          set({
            user: null,
            token: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      checkAuth: async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
          set({ isAuthenticated: false, isLoading: false });
          return;
        }

        set({ isLoading: true });
        try {
          const response = await axios.get('/auth/me');
          const user = response.data;

          set({
            user,
            token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          // Token is invalid, clear it
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          set({
            user: null,
            token: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      updateProfile: async (profileData) => {
        set({ isLoading: true });
        try {
          const response = await axios.put('/auth/profile', profileData);
          const updatedUser = response.data;

          set({
            user: updatedUser,
            isLoading: false,
          });

          return { success: true, user: updatedUser };
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      changePassword: async (passwordData) => {
        set({ isLoading: true });
        try {
          await axios.post('/auth/change-password', passwordData);
          set({ isLoading: false });
          return { success: true };
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export const useAnalysisStore = create(
  persist(
    (set, get) => ({
      // State
      analyses: [],
      currentAnalysis: null,
      isAnalyzing: false,
      analysisHistory: [],
      stats: null,

      // Actions
      uploadAndAnalyze: async (file, analysisType = 'auto') => {
        set({ isAnalyzing: true });
        try {
          const formData = new FormData();
          formData.append('file', file);

          const endpoint = file.type.startsWith('image/') 
            ? '/analyze/image' 
            : '/analyze/video';

          const response = await axios.post(endpoint, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
            timeout: 300000, // 5 minutes timeout
          });

          const analysis = response.data;

          // Update analyses list
          set((state) => ({
            currentAnalysis: analysis,
            analyses: [analysis, ...state.analyses],
            isAnalyzing: false,
          }));

          return { success: true, analysis };
        } catch (error) {
          set({ isAnalyzing: false });
          throw error;
        }
      },

      getAnalyses: async (page = 1, limit = 50) => {
        try {
          const response = await axios.get(`/analyses?page=${page}&limit=${limit}`);
          const analyses = response.data;

          set((state) => ({
            analyses: page === 1 ? analyses : [...state.analyses, ...analyses],
          }));

          return { success: true, analyses };
        } catch (error) {
          throw error;
        }
      },

      getAnalysisById: async (analysisId) => {
        try {
          const response = await axios.get(`/analyses/${analysisId}`);
          const analysis = response.data;

          set({ currentAnalysis: analysis });
          return { success: true, analysis };
        } catch (error) {
          throw error;
        }
      },

      deleteAnalysis: async (analysisId) => {
        try {
          await axios.delete(`/analyses/${analysisId}`);

          set((state) => ({
            analyses: state.analyses.filter(a => a.id !== analysisId),
            currentAnalysis: state.currentAnalysis?.id === analysisId ? null : state.currentAnalysis,
          }));

          return { success: true };
        } catch (error) {
          throw error;
        }
      },

      getStats: async () => {
        try {
          const response = await axios.get('/stats');
          const stats = response.data;

          set({ stats });
          return { success: true, stats };
        } catch (error) {
          throw error;
        }
      },

      clearCurrentAnalysis: () => {
        set({ currentAnalysis: null });
      },

      reset: () => {
        set({
          analyses: [],
          currentAnalysis: null,
          isAnalyzing: false,
          analysisHistory: [],
          stats: null,
        });
      },
    }),
    {
      name: 'analysis-storage',
      partialize: (state) => ({
        analyses: state.analyses.slice(0, 100), // Keep only last 100 analyses
        stats: state.stats,
      }),
    }
  )
);

export const useSettingsStore = create(
  persist(
    (set, get) => ({
      // State
      settings: {
        theme: 'dark',
        language: 'en',
        notifications: {
          email: true,
          push: false,
          analysis_complete: true,
          security_alerts: true,
        },
        analysis: {
          default_confidence_threshold: 0.5,
          auto_delete_results: false,
          result_retention_days: 30,
        },
        ui: {
          compact_mode: false,
          show_advanced_metrics: true,
          auto_refresh_dashboard: true,
        },
      },

      // Actions
      updateSettings: async (newSettings) => {
        try {
          // Update local state immediately for responsive UI
          set((state) => ({
            settings: { ...state.settings, ...newSettings },
          }));

          // Save to backend
          await axios.put('/user/settings', newSettings);
          return { success: true };
        } catch (error) {
          // Revert on error
          set((state) => ({
            settings: get().settings,
          }));
          throw error;
        }
      },

      resetSettings: () => {
        set({
          settings: {
            theme: 'dark',
            language: 'en',
            notifications: {
              email: true,
              push: false,
              analysis_complete: true,
              security_alerts: true,
            },
            analysis: {
              default_confidence_threshold: 0.5,
              auto_delete_results: false,
              result_retention_days: 30,
            },
            ui: {
              compact_mode: false,
              show_advanced_metrics: true,
              auto_refresh_dashboard: true,
            },
          },
        });
      },
    }),
    {
      name: 'settings-storage',
    }
  )
);

// API utilities
export const api = {
  // Auth endpoints
  auth: {
    login: (credentials) => axios.post('/auth/login', credentials),
    register: (userData) => axios.post('/auth/register', userData),
    me: () => axios.get('/auth/me'),
    refresh: (refreshToken) => axios.post('/auth/refresh', { refresh_token: refreshToken }),
    logout: () => axios.post('/auth/logout'),
  },

  // Analysis endpoints
  analysis: {
    analyzeImage: (formData) => axios.post('/analyze/image', formData),
    analyzeVideo: (formData) => axios.post('/analyze/video', formData),
    getAnalyses: (params) => axios.get('/analyses', { params }),
    getAnalysis: (id) => axios.get(`/analyses/${id}`),
    deleteAnalysis: (id) => axios.delete(`/analyses/${id}`),
  },

  // Stats endpoints
  stats: {
    getSystem: () => axios.get('/stats'),
    getUser: () => axios.get('/user/stats'),
  },

  // Settings endpoints
  settings: {
    get: () => axios.get('/user/settings'),
    update: (settings) => axios.put('/user/settings', settings),
  },

  // API Keys endpoints
  apiKeys: {
    create: (keyData) => axios.post('/api-keys', keyData),
    list: () => axios.get('/api-keys'),
    delete: (id) => axios.delete(`/api-keys/${id}`),
    regenerate: (id) => axios.post(`/api-keys/${id}/regenerate`),
  },
};

export default useAuthStore;
