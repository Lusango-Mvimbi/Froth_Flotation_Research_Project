import axios from 'axios';
import { FlotationData, ProcessControls, Prediction, OptimalRanges } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const AUTH_BASE_URL = process.env.REACT_APP_AUTH_URL || 'http://localhost:8051';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API - Uses Flask server on port 8051
export const authAPI = {
  login: async (username: string, password: string) => {
    console.log('Making login request to:', `${AUTH_BASE_URL}/login`);
    console.log('Request data:', { username, password });
    
    const response = await axios.post(`${AUTH_BASE_URL}/login`, { 
      username, 
      password 
    });
    
    console.log('Response received:', response);
    return response.data;
  },
  
  logout: async () => {
    const response = await axios.post(`${AUTH_BASE_URL}/logout`);
    return response.data;
  },
  
  verifyToken: async () => {
    const token = localStorage.getItem('authToken');
    if (!token) {
      throw new Error('No token found');
    }
    
    const response = await axios.get(`${AUTH_BASE_URL}/verify`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  },
};

// Flotation Data API
export const flotationAPI = {
  // Get current real-time data
  getCurrentData: async (): Promise<FlotationData> => {
    const response = await api.get('/api/current-data');
    return response.data;
  },
  
  // Get historical data
  getHistoricalData: async (limit: number = 100): Promise<FlotationData[]> => {
    const response = await api.get(`/api/database/sensor-data?limit=${limit}`);
    return response.data.data || [];
  },
  
  // Get predictions (using current data for now)
  getPredictions: async (controls: ProcessControls): Promise<Prediction> => {
    // For now, return mock prediction data since there's no prediction endpoint
    return {
      predicted_pb: 45.2 + Math.random() * 5,
      recovery_efficiency: 85.5 + Math.random() * 10,
      confidence: 0.92,
      status: 'optimal',
      prediction_method: 'ML Model'
    };
  },
  
  // Update control settings
  updateControls: async (controls: ProcessControls): Promise<void> => {
    await api.post('/api/control-settings', controls);
  },
  
  // Get optimal ranges
  getOptimalRanges: async (): Promise<OptimalRanges> => {
    const response = await api.get('/api/optimal-ranges');
    return response.data;
  },
  
  // Get recommendations (mock data for now)
  getRecommendations: async (): Promise<any[]> => {
    // Return mock recommendations since there's no recommendations endpoint
    return [
      {
        id: 1,
        type: 'optimization',
        message: 'Consider increasing KEX flowrate to 50 L/min for better recovery',
        priority: 'medium',
        timestamp: new Date().toISOString()
      },
      {
        id: 2,
        type: 'maintenance',
        message: 'Check impeller condition - performance may be degrading',
        priority: 'low',
        timestamp: new Date().toISOString()
      }
    ];
  },
  
  // WebSocket connection for real-time updates
  getWebSocketUrl: (): string => {
    return `${API_BASE_URL.replace('http', 'ws')}/ws/flotation-data`;
  },
};

// Dashboard API
export const dashboardAPI = {
  // Get dashboard summary (mock data for now)
  getSummary: async () => {
    const currentData = await api.get('/api/current-data');
    const optimalRanges = await api.get('/api/optimal-ranges');
    return {
      current_performance: 87.5,
      target_performance: 90.0,
      system_status: 'operational',
      last_update: new Date().toISOString(),
      current_data: currentData.data,
      optimal_ranges: optimalRanges.data
    };
  },
  
  // Get system status
  getSystemStatus: async () => {
    const connections = await api.get('/api/connections');
    return {
      status: 'operational',
      uptime: '2h 15m',
      active_connections: connections.data.active_connections,
      last_check: new Date().toISOString()
    };
  },
  
  // Export data (mock for now)
  exportData: async (format: 'csv' | 'json' | 'excel', dateRange?: { start: string; end: string }) => {
    // Return mock export data
    return {
      success: true,
      message: `Data exported in ${format} format`,
      download_url: `/api/database/sensor-data?limit=1000`
    };
  },
};

// Error handling utility
export const handleAPIError = (error: any): string => {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

export default api;
