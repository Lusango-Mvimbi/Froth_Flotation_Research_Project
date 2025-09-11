import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, 
  LogOut,
  RefreshCw,
  WifiOff,
  Download,
  FileText,
  FileSpreadsheet,
  BarChart3,
  Monitor
} from 'lucide-react';
import { toast } from 'react-hot-toast';

import { DashboardState, FlotationData, ProcessControls, Prediction, OptimalRanges, TargetRanges } from '../types';
import { flotationAPI } from '../services/api';
import { useAuth } from '../hooks/useAuthRefactored';
import { useFuturePredictions } from '../hooks/useFuturePredictions';
import { useError } from '../contexts/ErrorContext';
import { classifyError, extractErrorMessage, createDataError } from '../utils/errorUtils';
import PredictionCards from './PredictionCards';
import FuturePredictionChart from './FuturePredictionChart';
import PredictiveRecommendations from './PredictiveRecommendations';
import HistoricalAnalysis from './HistoricalAnalysis';

import ConnectionStatus from './ConnectionStatus';

interface DashboardProps {
  controls?: ProcessControls;
  onControlChange?: (controls: ProcessControls) => void;
}

const TABS = [
  {
    id: 'monitor',
    label: 'Live Monitor',
    icon: Monitor,
    description: 'Real-time process monitoring and control'
  },
  {
    id: 'analysis',
    label: 'Historical Analysis',
    icon: BarChart3,
    description: 'Trend analysis and data insights'
  }
] as const;

type TabId = typeof TABS[number]['id'];

const Dashboard: React.FC<DashboardProps> = ({ controls, onControlChange }) => {
  const { logout } = useAuth();
  const { futurePredictions, loading: futurePredictionsLoading, fetchPredictions } = useFuturePredictions();
  const { addError } = useError();
  const [activeTab, setActiveTab] = useState<TabId>('monitor');
  
  const [state, setState] = useState<DashboardState>({
    data: [],
    currentData: null,
    controls: controls || { kex: 0, sipx: 0 },
    predictions: null,
    recommendations: [],
    optimalRanges: null,
    targetRanges: null,
    loading: true,
    error: null,
    serverConnected: false,
  });
  

  // Update state when controls change from props
  useEffect(() => {
    if (controls) {
      setState(prev => ({ ...prev, controls }));
    }
  }, [controls]);





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
          addError(createDataError('Unable to fetch optimal ranges for controls'));
        }
        
        // Try to fetch target ranges
        let targetRanges: TargetRanges | null = null;
        try {
          targetRanges = await flotationAPI.getTargetRanges();
        } catch (error) {
          console.warn('⚠️ Could not fetch target ranges:', error);
          addError(createDataError('Unable to fetch target ranges for predictions'));
        }
        
        // Fetch current control settings - must succeed
        const currentControls = await flotationAPI.getControlSettings();
        
        
        // Use the API controls as the initial values
        const preservedControls = currentControls;
        
        
        // Historical data fetching removed - not currently used
        
        // Try to fetch current data
        let currentData: FlotationData | null = null;
        try {
          currentData = await flotationAPI.getCurrentData();
        } catch (error) {
          console.warn('⚠️ Could not fetch current data:', error);
          addError(createDataError('Unable to fetch current system data'));
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
          recommendations: [], // Recommendations are now handled by PredictiveRecommendations component
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
        const errorType = classifyError(error);
        const errorMessage = extractErrorMessage(error);
        
        addError({
          type: errorType,
          message: errorMessage,
          recoverable: true,
          suggestions: [
            'Check if the backend server is running',
            'Verify your internet connection',
            'Try refreshing the page',
            'Contact IT support if the issue persists'
          ]
        });
        
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
  }, [addError]);

  // Fetch future predictions when current data changes
  useEffect(() => {
    if (state.currentData) {
      console.log('Dashboard: Current data changed, fetching future predictions');
      fetchPredictions(state.currentData, !futurePredictions);
    }
  }, [state.currentData, fetchPredictions, futurePredictions]);

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
        
        // Controls are now managed by TabbedDashboard, so we don't fetch them here
        const updatedControls = state.controls;
        
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
          recommendations: [], // Recommendations are now handled by PredictiveRecommendations component
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
  }, [state.serverConnected, state.controls]); // Include all dependencies


  // Export functions
  const exportToCSV = () => {
    if (!state.currentData) {
      toast.error('No data available to export');
      return;
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `flotation-data-${timestamp}.csv`;
    
    // Prepare CSV data
    const csvData = [
      ['Parameter', 'Value', 'Unit', 'Timestamp'],
      ['Pb Concentrate', state.currentData.Actual_Pb_Concentrate || 0, '%', state.currentData.timestamp],
      ['KEX Flowrate', state.currentData.Pb_Conditioner_KEX_Flowrate || 0, 'L/min', state.currentData.timestamp],
      ['SIPX Flowrate', state.currentData.Pb_Rougher1_SIPX_Flowrate || 0, 'L/min', state.currentData.timestamp],
      ['Air Flow', state.currentData.Pb_Rougher1_AirFlow || 0, 'm³/min', state.currentData.timestamp],
      ['Level', state.currentData.Pb_Rougher1_Level || 0, '%', state.currentData.timestamp],
      ['Feed Pb', state.currentData.Feed_Pb || 0, '%', state.currentData.timestamp],
      ['Feed Zn', state.currentData.Feed_Zn || 0, '%', state.currentData.timestamp],
    ];

    // Add future predictions if available
    if (futurePredictions?.future_predictions) {
      csvData.push(['', '', '', '']); // Empty row
      csvData.push(['Future Predictions', '', '', '']);
      Object.entries(futurePredictions.future_predictions).forEach(([horizon, pred]) => {
        csvData.push([`${horizon} Prediction`, pred.prediction, '%', pred.prediction_time]);
      });
    }

    const csvContent = csvData.map(row => row.join(',')).join('\n');
    
    // Create and download file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    
    toast.success('Data exported to CSV successfully!');
  };

  const exportToPDF = () => {
    if (!state.currentData) {
      toast.error('No data available to export');
      return;
    }

    // Create a simple PDF-like report
    const timestamp = new Date().toLocaleString();
    const reportContent = `
FROTH FLOTATION DIGITAL TWIN - SYSTEM REPORT
Generated: ${timestamp}

CURRENT SYSTEM STATUS:
=====================
Pb Concentrate: ${state.currentData.Actual_Pb_Concentrate || 0}%
KEX Flowrate: ${state.currentData.Pb_Conditioner_KEX_Flowrate || 0} L/min
SIPX Flowrate: ${state.currentData.Pb_Rougher1_SIPX_Flowrate || 0} L/min
Air Flow: ${state.currentData.Pb_Rougher1_AirFlow || 0} m³/min
Level: ${state.currentData.Pb_Rougher1_Level || 0}%
Feed Pb: ${state.currentData.Feed_Pb || 0}%
Feed Zn: ${state.currentData.Feed_Zn || 0}%

FUTURE PREDICTIONS:
==================
${futurePredictions?.future_predictions ? 
  Object.entries(futurePredictions.future_predictions).map(([horizon, pred]) => 
    `${horizon}: ${pred.prediction.toFixed(2)}% (R²: ${pred.model_performance.r2_score.toFixed(3)})`
  ).join('\n') : 'No predictions available'}

SYSTEM STATUS: ${state.serverConnected ? 'CONNECTED' : 'DISCONNECTED'}
    `.trim();

    const filename = `flotation-report-${new Date().toISOString().replace(/[:.]/g, '-')}.txt`;
    const blob = new Blob([reportContent], { type: 'text/plain;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    
    toast.success('Report exported successfully!');
  };

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
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-white mb-2">Loading Dashboard</h2>
          <p className="text-slate-300">Connecting to flotation system...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700">
      {/* Header */}
      <motion.header
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-slate-800 border-b border-slate-600 shadow-sm"
      >
        <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div className="flex flex-row justify-between items-center py-4">
          <div className="flex items-center space-x-3">
            <Activity className="h-8 w-8 text-primary-400 flex-shrink-0" />
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
                Froth Flotation Digital Twin
              </h1>
              <p className="text-sm text-slate-300">Industrial Process Monitoring Dashboard</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
              <ConnectionStatus connected={state.serverConnected} />
              
              
              {/* Export Dropdown */}
              <div className="relative group">
                <button className="flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-2 bg-success-600 hover:bg-success-700 text-white rounded-lg transition-colors duration-200 text-sm">
                  <Download className="h-3 w-3 sm:h-4 sm:w-4" />
                  <span className="hidden sm:inline">Export</span>
                </button>
                
                {/* Dropdown Menu */}
                <div className="absolute right-0 mt-2 w-48 bg-slate-700 border border-slate-600 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  <div className="py-1">
                    <button
                      onClick={exportToCSV}
                      className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-white hover:bg-slate-600 transition-colors"
                    >
                      <FileSpreadsheet className="h-4 w-4" />
                      <span>Export to CSV</span>
                    </button>
                    <button
                      onClick={exportToPDF}
                      className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-white hover:bg-slate-600 transition-colors"
                    >
                      <FileText className="h-4 w-4" />
                      <span>Export Report</span>
                    </button>
                  </div>
                </div>
              </div>
              
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="flex items-center space-x-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-800 text-white rounded-lg transition-colors duration-200 text-sm"
              >
                <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
              
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-4 py-2 bg-danger-600 hover:bg-danger-700 text-white rounded-lg transition-colors duration-200 text-sm"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Tab Navigation - Positioned below header */}
      <div className="bg-slate-800 border-b border-slate-600 shadow-sm">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex space-x-1 py-3">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-3 px-6 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-primary-600 text-white shadow-lg'
                      : 'text-slate-300 hover:text-white hover:bg-slate-700'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <div className="text-left">
                    <div className="font-semibold">{tab.label}</div>
                    <div className={`text-xs ${
                      isActive ? 'text-primary-100' : 'text-slate-400'
                    }`}>
                      {tab.description}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-6 bg-transparent">
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

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'monitor' && (
            <motion.div
              key="monitor"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <AnimatePresence>
          {/* Prediction Cards */}
          <motion.div
            key="prediction-cards"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-4 sm:mb-6"
          >
            {(() => {
              console.log('Dashboard: Passing data to PredictionCards:', {
                predictions: state.predictions,
                currentData: state.currentData,
                targetRanges: state.targetRanges,
                futurePredictions: futurePredictions
              });
              return (
                <PredictionCards 
                  predictions={state.predictions}
                  currentData={state.currentData}
                  targetRanges={state.targetRanges}
                  futurePredictions={futurePredictions}
                  loading={futurePredictionsLoading}
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
            className="mb-4 sm:mb-6"
          >
            <FuturePredictionChart
              currentData={state.currentData}
              historicalData={state.data}
              futurePredictions={futurePredictions}
              loading={futurePredictionsLoading}
            />
          </motion.div>

          {/* Predictive Recommendations */}
          <motion.div
            key="predictive-recommendations"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-4 sm:mb-6"
          >
            <PredictiveRecommendations
              currentData={state.currentData}
              targetRanges={state.targetRanges}
              onControlChange={onControlChange}
              currentControls={state.controls}
            />
          </motion.div>




              </AnimatePresence>
            </motion.div>
          )}

          {activeTab === 'analysis' && (
            <motion.div
              key="analysis"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <HistoricalAnalysis />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

export default Dashboard;
