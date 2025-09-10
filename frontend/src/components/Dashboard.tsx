import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, 
  LogOut,
  RefreshCw,
  WifiOff
} from 'lucide-react';
import { toast } from 'react-hot-toast';

import { DashboardState, FlotationData, ProcessControls, Prediction, OptimalRanges, TargetRanges } from '../types';
import { flotationAPI } from '../services/api';
import { useAuth } from '../hooks/useAuthRefactored';
import PredictionCards from './PredictionCards';
import ControlPanel from './ControlPanel';
import FuturePredictionChart from './FuturePredictionChart';
import PredictiveRecommendations from './PredictiveRecommendations';

import ConnectionStatus from './ConnectionStatus';

const Dashboard: React.FC = () => {
  const { logout } = useAuth();
  
  const [state, setState] = useState<DashboardState>({
    data: [],
    currentData: null,
    controls: {
      kex: 0,
      sipx: 0,
    },
    predictions: null,
    recommendations: [],
    optimalRanges: null,
    targetRanges: null,
    loading: true,
    error: null,
    serverConnected: false,
  });
  
  // Track if controls were manually changed
  const [controlsManuallyChanged, setControlsManuallyChanged] = useState(false);
  const [lastManualChangeTime, setLastManualChangeTime] = useState<number | null>(null);





  const [isRefreshing, setIsRefreshing] = useState(false);

  // Fetch initial data
  useEffect(() => {
    const initializeDashboard = async () => {
      try {
        setState(prev => ({ ...prev, loading: true, error: null }));
        
        // Try to fetch optimal ranges
        let optimalRanges: OptimalRanges | null = null;
        try {
          optimalRanges = await flotationAPI.getOptimalRanges();
        } catch (error) {
          console.warn('⚠️ Could not fetch optimal ranges:', error);
        }
        
        // Try to fetch target ranges
        let targetRanges: TargetRanges | null = null;
        try {
          targetRanges = await flotationAPI.getTargetRanges();
        } catch (error) {
          console.warn('⚠️ Could not fetch target ranges:', error);
        }
        
        // Fetch current control settings - must succeed
        const currentControls = await flotationAPI.getControlSettings();
        
        
        // Use the API controls as the initial values
        const preservedControls = currentControls;
        
        
        // Try to fetch historical data (currently unused but kept for future use)
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        let historicalData: FlotationData[] = [];
        try {
          historicalData = await flotationAPI.getHistoricalData(100);
        } catch (error) {
          console.warn('⚠️ Could not fetch historical data:', error);
        }
        
        // Try to fetch current data
        let currentData: FlotationData | null = null;
        try {
          currentData = await flotationAPI.getCurrentData();
        } catch (error) {
          console.warn('⚠️ Could not fetch current data:', error);
        }
        
        
        

        
        // Create predictions from current data (which includes ML predictions)
        let predictions: Prediction | null = null;
        if (currentData) {
          predictions = {
            predicted_pb: currentData.Predicted_Pb_Concentrate || 0,
            recovery_efficiency: (currentData.Predicted_Pb_Recovery || 0) * 100,
            status: currentData.Process_Status || 'unknown',
            prediction_method: 'ML Model' as const
          };
        }
        
        // Determine if server is connected based on successful API calls
        const serverConnected = !!currentData;
        
        
        
        // Create live data array with current data for real-time updates
        const liveData = currentData ? [currentData] : [];
        
        setState(prev => ({
          ...prev,
          data: liveData, // Use current data for live graph instead of historical data
          currentData,
          predictions,
          controls: preservedControls,
          optimalRanges,
          targetRanges,
          recommendations: (currentData?.Recommendations || []).map((rec: string, index: number) => ({
            id: `rec-${index}`,
            type: 'info' as const,
            message: rec,
            timestamp: currentData?.timestamp || new Date().toISOString()
          })),
          loading: false,
          serverConnected,
          error: serverConnected ? null : 'Backend services not available'
        }));
        

        
        if (serverConnected) {
          toast.success('Dashboard connected successfully!');
        } else {
          throw new Error('Backend connection failed - dashboard requires real-time data');
        }
      } catch (error) {
        console.error('❌ Failed to initialize dashboard:', error);
        setState(prev => ({
          ...prev,
          loading: false,
          error: 'Failed to initialize dashboard',
          serverConnected: false,
        }));
        toast.error('Failed to initialize dashboard');
      }
    };

    initializeDashboard();
  }, []);

  // Real-time data polling (only if server is connected)
  useEffect(() => {
    if (!state.serverConnected) return;

    // Polling enabled with proper manual change preservation

    const interval = setInterval(async () => {
      try {
        const currentData = await flotationAPI.getCurrentData();
        
        // Create predictions from current data (which includes ML predictions)
        const predictions = {
          predicted_pb: currentData.Predicted_Pb_Concentrate || currentData.Pb_Concentrate || 0,
          recovery_efficiency: currentData.Predicted_Pb_Recovery ? (currentData.Predicted_Pb_Recovery * 100) : (currentData.Pb_Recovery || 0) * 100, // Convert from decimal to percentage
          status: currentData.Process_Status || 'optimal',
          prediction_method: 'ML Model' as const
        };
        
        // Keep current control settings - don't fetch from API to avoid overriding manual changes
        let updatedControls = state.controls;
        
        // Only fetch from API if controls were not manually changed recently
        const timeSinceLastManualChange = lastManualChangeTime ? Date.now() - lastManualChangeTime : Infinity;
        const shouldPreserveManualChanges = controlsManuallyChanged && timeSinceLastManualChange < 12000; // 12 seconds (3 polling cycles)
        
        // Fetch control settings from backend if:
        // 1. Controls were not manually changed recently, OR
        // 2. Controls are at default values (0,0) and we need initial values
        if (!shouldPreserveManualChanges) {
          try {
            updatedControls = await flotationAPI.getControlSettings();
            console.log('🔄 Fetched control settings from backend:', updatedControls);
          } catch (error) {
            console.warn('Could not fetch control settings:', error);
          }
        }
        
        // Disabled random control fetching to prevent overriding Quick Action updates
        // if (Math.random() < 0.1) { // Only 10% chance to check controls
        //   try {
        //     updatedControls = await flotationAPI.getControlSettings();
        //   } catch (error) {
        //     console.warn('Could not fetch updated control settings:', error);
        //   }
        // }
        
        
        
        setState(prev => ({
          ...prev,
          currentData,
          predictions,
          controls: updatedControls,
          recommendations: (currentData?.Recommendations || []).map((rec: string, index: number) => ({
            id: `rec-${index}`,
            type: 'info' as const,
            message: rec,
            timestamp: currentData?.timestamp || new Date().toISOString()
          })),
          data: [...prev.data.slice(-99), currentData], // Keep last 100 points
        }));
        
      } catch (error) {
        console.error('Failed to fetch real-time data:', error);
        
        // Only show connection lost if we were previously connected
        if (state.serverConnected) {
          setState(prev => ({ ...prev, serverConnected: false }));
          toast.error('Connection lost - trying to reconnect...');
        }
      }
    }, 4000); // Aligned with backend data generation (4 seconds)

    return () => clearInterval(interval);
  }, [state.serverConnected, controlsManuallyChanged, lastManualChangeTime, state.controls]); // Include all dependencies

  // Handle control changes
  const handleControlChange = useCallback(async (controls: ProcessControls) => {
    try {
      if (state.serverConnected) {
        await flotationAPI.updateControls(controls);
      }
      setState(prev => ({ ...prev, controls }));
      setControlsManuallyChanged(true); // Mark that controls were manually changed
      setLastManualChangeTime(Date.now()); // Record when the change was made
      
      // Don't fetch current data here to avoid overriding control values
      // The polling will handle updating current data
      
      toast.success('Controls updated successfully');
    } catch (error) {
      console.error('Failed to update controls:', error);
      toast.error('Failed to update controls');
    }
  }, [state.serverConnected]);

  // Manual refresh
  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      let currentData: FlotationData | null = null;
      let predictions: Prediction | null = null;
      let serverConnected = false;

      try {
        currentData = await flotationAPI.getCurrentData();
        
        // Create predictions from current data
        predictions = {
          predicted_pb: currentData.Predicted_Pb_Concentrate || currentData.Pb_Concentrate || 0,
          recovery_efficiency: currentData.Predicted_Pb_Recovery ? (currentData.Predicted_Pb_Recovery * 100) : (currentData.Pb_Recovery || 0) * 100,
          status: currentData.Process_Status || 'optimal',
          prediction_method: 'ML Model' as const
        };
        
        serverConnected = true;
      } catch (error) {
        console.error('Refresh failed - backend required:', error);
        throw error;
      }
      
      setState(prev => ({
        ...prev,
        currentData,
        predictions,
        recommendations: (currentData?.Recommendations || []).map((rec: string, index: number) => ({
          id: `rec-${index}`,
          type: 'info' as const,
          message: rec,
          timestamp: new Date().toISOString()
        })),
        serverConnected,
        error: serverConnected ? null : 'Backend services not available'
      }));
      
      if (serverConnected) {
        toast.success('Data refreshed successfully');
      } else {
        toast.error('Refresh failed - backend connection required');
        throw new Error('Backend connection failed');
      }
    } catch (error) {
      console.error('Failed to refresh data:', error);
      toast.error('Failed to refresh data');
    } finally {
      setIsRefreshing(false);
    }
  };

  // Fetch optimization data on component mount and periodically


  // Handle logout
  const handleLogout = async () => {
    try {
      console.log('🔐 Logging out...');
      await logout(); // Use the proper logout method from useAuth
      console.log('✅ Logout successful');
    } catch (error) {
      console.error('❌ Logout error:', error);
      // Fallback: clear localStorage and redirect
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
      localStorage.removeItem('auth_token');
      localStorage.removeItem('current_user');
      window.location.href = '/login';
    }
  };

  if (state.loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-700 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-white mb-2">Loading Dashboard</h2>
          <p className="text-dark-300">Connecting to flotation system...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-700">
      {/* Header */}
      <motion.header
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-gradient-to-r from-dark-800 to-dark-700 border-b border-dark-600 shadow-lg"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center py-4 space-y-4 sm:space-y-0">
            <div className="flex items-center space-x-3 min-w-0">
              <Activity className="h-6 w-6 sm:h-8 sm:w-8 text-primary-400 flex-shrink-0" />
              <div className="min-w-0">
                <h1 className="text-lg sm:text-xl lg:text-2xl font-bold bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent truncate">
                  Froth Flotation Digital Twin
                </h1>
                <p className="text-xs sm:text-sm text-dark-300 truncate">Industrial Process Monitoring Dashboard</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2 sm:space-x-4 w-full sm:w-auto">
              <ConnectionStatus connected={state.serverConnected} />
              
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-800 text-white rounded-lg transition-colors duration-200 text-sm"
              >
                <RefreshCw className={`h-3 w-3 sm:h-4 sm:w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                <span className="hidden sm:inline">Refresh</span>
              </button>
              
              <button
                onClick={handleLogout}
                className="flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-2 bg-danger-600 hover:bg-danger-700 text-white rounded-lg transition-colors duration-200 text-sm"
              >
                <LogOut className="h-3 w-3 sm:h-4 sm:w-4" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Connection Status Banner */}
        {state.error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-danger-900/20 border border-danger-700 rounded-lg flex items-center space-x-2"
          >
            <WifiOff className="h-5 w-5 text-danger-400" />
            <span className="text-danger-400 text-sm">
              {state.error}
            </span>
          </motion.div>
        )}

        <AnimatePresence>
          {/* Prediction Cards */}
          <motion.div
            key="prediction-cards"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-6"
          >
            {(() => {
              console.log('Dashboard: Passing data to PredictionCards:', {
                predictions: state.predictions,
                currentData: state.currentData,
                targetRanges: state.targetRanges
              });
              return (
                <PredictionCards 
                  predictions={state.predictions}
                  currentData={state.currentData}
                  targetRanges={state.targetRanges}
                />
              );
            })()}
          </motion.div>

          {/* Future Prediction Chart */}
          <motion.div
            key="future-prediction-chart"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="mb-6"
          >
            <FuturePredictionChart
              currentData={state.currentData}
              historicalData={state.data}
            />
          </motion.div>

          {/* Predictive Recommendations */}
          <motion.div
            key="predictive-recommendations"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-6"
          >
            <PredictiveRecommendations
              currentData={state.currentData}
              targetRanges={state.targetRanges}
              onControlChange={handleControlChange}
              currentControls={state.controls}
            />
          </motion.div>

          {/* Control Panel */}
          <motion.div
            key="control-panel"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="mb-6"
          >
            <ControlPanel
              controls={state.controls}
              optimalRanges={state.optimalRanges}
              onControlChange={handleControlChange}
            />
          </motion.div>


        </AnimatePresence>
      </main>
    </div>
  );
};

export default Dashboard;
