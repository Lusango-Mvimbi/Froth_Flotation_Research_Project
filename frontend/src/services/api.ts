import axios from 'axios';
import { FlotationData, ProcessControls, OptimalRanges, TargetRanges, FuturePredictionResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const AUTH_BASE_URL = process.env.REACT_APP_AUTH_URL || 'http://localhost:8051';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,  // Increased timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication and retry initialization
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Initialize retry count for new requests
    if (!(config as any)._retryCount) {
      (config as any)._retryCount = 0;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling and retry logic
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Handle authentication errors
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
      return Promise.reject(error);
    }
    
    // Retry logic for network errors or 5xx errors
    if ((!error.response || error.response.status >= 500) && 
        !(originalRequest as any)._retry && 
        (originalRequest as any)._retryCount < 3) {
      
      (originalRequest as any)._retry = true;
      (originalRequest as any)._retryCount = ((originalRequest as any)._retryCount || 0) + 1;
      
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, 1000 * (originalRequest as any)._retryCount));
      
      return api(originalRequest);
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
  

  
  // Get current control settings
  getControlSettings: async (): Promise<ProcessControls> => {
    const response = await api.get(`/api/control-settings?t=${Date.now()}`);
    return response.data.controls;
  },
  
  // Update control settings
  updateControls: async (controls: ProcessControls): Promise<void> => {
    await api.post('/api/control-settings', controls);
  },
  
  // Get optimal ranges
  getOptimalRanges: async (): Promise<OptimalRanges> => {
    const response = await api.get('/api/optimal-ranges');
    return response.data.control_ranges;  // Use control_ranges instead of parameter_ranges
  },
  
  // Get target ranges for prediction cards
  getTargetRanges: async (): Promise<TargetRanges> => {
    const response = await api.get('/api/target-ranges');
    return response.data.target_ranges;
  },
  
  // Get optimization data
  getOptimizationData: async (): Promise<any> => {
    const response = await api.get('/api/optimization-data');
    return response.data.optimization_data;
  },
  
  // Get future predictions
  getFuturePredictions: async (inputData: Partial<FlotationData>): Promise<FuturePredictionResponse> => {
    const response = await api.post('/api/predict-future', inputData);
    return response.data;
  },
  
  // Optimize reagent rates (for simulation)
  optimizeReagentRates: async (reagentSettings: { kex: number; sipx: number }): Promise<any> => {
    const response = await api.post('/api/optimize-reagent-rates', reagentSettings);
    return response.data;
  },
  

  
  // WebSocket connection for real-time updates
  getWebSocketUrl: (): string => {
    return `${API_BASE_URL.replace('http', 'ws')}/ws/flotation-data`;
  },
};

// Dashboard API
export const dashboardAPI = {
  // Get dashboard summary from real data
  getSummary: async () => {
    const currentData = await api.get('/api/current-data');
    const optimalRanges = await api.get('/api/optimal-ranges');
    const data = currentData.data;
    
    return {
      current_performance: data.Pb_Recovery * 100,
      target_performance: data.Target_Performance,
      system_status: data.Process_Status,
      last_update: data.timestamp,
      current_data: data,
      optimal_ranges: optimalRanges.data
    };
  },
  
  // Get system status from real data
  getSystemStatus: async () => {
    const connections = await api.get('/api/connections');
    const status = await api.get('/status');
    return {
      status: status.data.status,
      uptime: status.data.uptime,
      active_connections: connections.data.active_connections,
      last_check: status.data.timestamp
    };
  },
  
  // Export data using real endpoint
  exportData: async (format: 'csv' | 'json' | 'excel', dateRange?: { start: string; end: string }) => {
    const response = await api.get(`/api/database/sensor-data?limit=1000`);
    return {
      success: true,
      message: `Data exported in ${format} format`,
      download_url: `/api/database/sensor-data?limit=1000`,
      data: response.data
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
