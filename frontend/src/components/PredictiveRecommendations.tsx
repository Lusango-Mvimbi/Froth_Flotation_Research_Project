import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Info,
  Settings,
  Target,
  Clock,
  Zap,
  ArrowUp,
  ArrowDown,
  RotateCcw,
  Brain
} from 'lucide-react';
import { FlotationData, ProcessControls, Recommendation } from '../types';
import { RecommendationsSkeleton } from './LoadingSkeleton';
import { flotationAPI } from '../services/api';
import { useFuturePredictions } from '../hooks/useFuturePredictions';

interface PredictiveRecommendationsProps {
  currentData: FlotationData | null;
  targetRanges: any;
  onControlChange?: (controls: ProcessControls) => void;
  currentControls?: ProcessControls;
}


const PredictiveRecommendations: React.FC<PredictiveRecommendationsProps> = ({ 
  currentData, 
  targetRanges,
  onControlChange,
  currentControls
}) => {
  const { futurePredictions, loading, refreshing, fetchPredictions } = useFuturePredictions();
  const [selectedRecommendation, setSelectedRecommendation] = useState<string | null>(null);
  const [simulationModal, setSimulationModal] = useState<{
    isOpen: boolean;
    data: any;
    recommendation: Recommendation | null;
  }>({
    isOpen: false,
    data: null,
    recommendation: null
  });
  const [quickActionModal, setQuickActionModal] = useState<{
    isOpen: boolean;
    recommendation: Recommendation | null;
    success: boolean;
    message: string;
  }>({
    isOpen: false,
    recommendation: null,
    success: false,
    message: ''
  });


  // Fetch future predictions when current data changes
  useEffect(() => {
    if (currentData) {
      // Debounce the fetch to prevent excessive API calls and synchronize with other components
      const timeoutId = setTimeout(() => {
        const isInitialLoad = !futurePredictions;
        fetchPredictions(currentData, isInitialLoad);
      }, 1500); // Increased to 1.5s delay to reduce API calls
      
      return () => clearTimeout(timeoutId);
    }
  }, [currentData, fetchPredictions, futurePredictions]);

  // Parse backend recommendations into structured format
  const parseBackendRecommendations = useCallback(() => {
    if (!currentData?.Recommendations || !Array.isArray(currentData.Recommendations)) {
      return [];
    }

    return currentData.Recommendations.map((rec: string, index: number) => {
      // Parse the recommendation string to extract structured information
      let type = 'info';
      let title = rec;
      let parameter = 'System_Status';
      let actionType = 'info';
      let impact = 'medium';
      let confidence = 0.8;
      let currentValue = 0;
      let suggestedValue = 0;

      // Parse different types of recommendations
      if (rec.includes('TARGETS ACHIEVED')) {
        type = 'success';
        actionType = 'info';  // Targets achieved is informational, not actionable
        impact = 'high';
        confidence = 1.0;
        title = 'TARGETS ACHIEVED';
      } else if (rec.toLowerCase().includes('increase') || rec.toLowerCase().includes('decrease')) {
        type = 'optimization';
        if (rec.toLowerCase().includes('increase')) {
          actionType = 'increase';
        } else if (rec.toLowerCase().includes('decrease')) {
          actionType = 'decrease';
        }
        impact = 'high';
        confidence = 0.8;
        
        // Extract parameter name and values
        if (rec.includes('KEX')) {
          parameter = 'Pb_Conditioner_KEX_Flowrate';
          // Parse "from X to Y" pattern
          const fromMatch = rec.match(/from ([\d.]+) to ([\d.]+)/);
          if (fromMatch) {
            currentValue = parseFloat(fromMatch[1]);
            suggestedValue = parseFloat(fromMatch[2]);
          }
          title = rec.includes('increase') ? 'Increase KEX to Meet Target' : 'Decrease KEX for Efficiency';
        } else if (rec.includes('SIPX')) {
          parameter = 'Pb_Rougher1_SIPX_Flowrate';
          // Parse "from X to Y" pattern
          const fromMatch = rec.match(/from ([\d.]+) to ([\d.]+)/);
          if (fromMatch) {
            currentValue = parseFloat(fromMatch[1]);
            suggestedValue = parseFloat(fromMatch[2]);
          }
          title = rec.includes('increase') ? 'Increase SIPX Flow Rate' : 'Decrease SIPX for Efficiency';
        }
      } else if (rec.includes('WARNING:')) {
        type = 'warning';
        actionType = 'info';  // Warnings are informational, no direct action needed
        impact = 'medium';
        confidence = 0.7;
        title = 'System Warning';
      } else if (rec.includes('Expected outcomes:')) {
        type = 'info';
        actionType = 'info';
        impact = 'low';
        confidence = 0.8;
        title = 'Expected Outcomes';
      } else if (rec.includes('Current settings are near optimal')) {
        type = 'success';
        actionType = 'info';  // System optimal is informational, no action needed
        impact = 'medium';
        confidence = 0.9;
        title = 'System Optimal';
      }

      return {
        id: `backend-rec-${index}`,
        type: type as any,
        title: title,
        description: rec,
        parameter: parameter,
        currentValue: currentValue || (currentData as any)[parameter] || 0,
        suggestedValue: suggestedValue || (currentData as any)[parameter] || 0,
        expectedOutcome: rec,
        timeHorizon: '15-30 minutes',
        confidence: confidence,
        impact: impact as any,
        actionType: actionType as any
      };
    });
  }, [currentData]);

  // Always use backend recommendations parsed from currentData
  const allRecommendations = parseBackendRecommendations();
  
  // Group recommendations by type for better organization
  const groupedRecommendations = useMemo(() => {
    const actionable = allRecommendations.filter(rec => rec.actionType !== 'info');
    const informational = allRecommendations.filter(rec => rec.actionType === 'info');
    
    return {
      actionable: actionable.slice(0, 4), // Limit actionable to 4
      informational: informational.slice(0, 3) // Limit informational to 3
    };
  }, [allRecommendations]);

  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case 'improvement':
        return <TrendingUp className="h-5 w-5 text-success-400" />;
      case 'risk':
        return <AlertTriangle className="h-5 w-5 text-danger-400" />;
      case 'optimization':
        return <Target className="h-5 w-5 text-primary-400" />;
      case 'info':
        return <Info className="h-5 w-5 text-info-400" />;
      default:
        return <Info className="h-5 w-5 text-slate-400" />;
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'text-red-400 bg-red-900/20 border border-red-800/30';
      case 'medium':
        return 'text-orange-400 bg-orange-900/20 border border-orange-800/30';
      case 'low':
        return 'text-blue-400 bg-blue-900/20 border border-blue-800/30';
      default:
        return 'text-slate-300 bg-slate-700/20 border border-slate-600/30';
    }
  };

  const getActionIcon = (actionType: string) => {
    switch (actionType) {
      case 'increase':
        return <ArrowUp className="h-4 w-4" />;
      case 'decrease':
        return <ArrowDown className="h-4 w-4" />;
      case 'maintain':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <Settings className="h-4 w-4" />;
    }
  };

  const handleQuickAction = async (recommendation: Recommendation) => {
    try {
      // Ensure we have current controls - fail if not available
      if (!currentControls) {
        setQuickActionModal({
          isOpen: true,
          recommendation,
          success: false,
          message: 'Current control settings not available. Please refresh the page.'
        });
        return;
      }
      
      // Map recommendation parameters to control settings
      let controlSettings: { kex?: number; sipx?: number } = {};
      
      if (recommendation.parameter === 'Pb_Conditioner_KEX_Flowrate') {
        controlSettings.kex = recommendation.suggestedValue;
      } else if (recommendation.parameter === 'Pb_Rougher1_SIPX_Flowrate') {
        controlSettings.sipx = recommendation.suggestedValue;
      } else if (recommendation.parameter === 'Pb_Rougher1_AirFlow') {
        // Air flow is not directly controllable via KEX/SIPX, but we can adjust them as a proxy
        const currentKex = currentControls?.kex || 0;
        const currentSipx = currentControls?.sipx || 0;
        
        if (recommendation.actionType === 'decrease') {
          // Reduce KEX and SIPX to compensate for high air flow
          controlSettings.kex = Math.max(currentKex - 3, 30);
          controlSettings.sipx = Math.max(currentSipx - 2, 15);
        }
      } else if (recommendation.parameter === 'Pb_Concentrate') {
        // For Pb concentrate recommendations, we need to adjust KEX and SIPX
        // This is a simplified approach - in reality, you'd use optimization algorithms
        const currentKex = currentControls?.kex || 0;
        const currentSipx = currentControls?.sipx || 0;
        
        const actionType = (recommendation.actionType || 'maintain').toLowerCase();
        
        if (actionType === 'increase') {
          controlSettings.kex = Math.min(currentKex + 5, 80);
          controlSettings.sipx = Math.min(currentSipx + 3, 50);
        } else if (actionType === 'decrease') {
          controlSettings.kex = Math.max(currentKex - 5, 0);
          controlSettings.sipx = Math.max(currentSipx - 3, 0);
        } else if (actionType === 'maintain') {
          // For maintain, keep current values but ensure they're within optimal ranges
          controlSettings.kex = currentKex;
          controlSettings.sipx = currentSipx;
        }
      }
      
      // Only proceed if we have valid control settings
      if (Object.keys(controlSettings).length > 0) {
        const fullControlSettings: ProcessControls = {
          kex: controlSettings.kex ?? currentControls.kex,
          sipx: controlSettings.sipx ?? currentControls.sipx
        };
        
        // Update control settings via API
        await flotationAPI.updateControls(fullControlSettings);
        
        // Update the parent component's controls state to refresh the UI
        if (onControlChange) {
          onControlChange(fullControlSettings);
        }
        
        // Show success modal
        setQuickActionModal({
          isOpen: true,
          recommendation,
          success: true,
          message: `Updated: ${Object.entries(controlSettings).map(([key, value]) => `${key.toUpperCase()}: ${value}`).join(', ')}`
        });
        
        // Refresh predictions after control change
        setTimeout(() => {
          fetchPredictions(currentData, false);
        }, 2000);
      } else {
        // Show warning modal
        setQuickActionModal({
          isOpen: true,
          recommendation,
          success: false,
          message: 'This parameter is not directly controllable.'
        });
      }
    } catch (error) {
      console.error('Quick action failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      // Show error modal
      setQuickActionModal({
        isOpen: true,
        recommendation,
        success: false,
        message: `Error: ${errorMessage}`
      });
    }
  };

  const handleSimulateScenario = async (recommendation: Recommendation) => {
    try {
      console.log('Simulating scenario:', recommendation);
      
      // Prepare simulation parameters
      let simulationParams: { kex?: number; sipx?: number } = {};
      
      if (recommendation.parameter === 'Pb_Conditioner_KEX_Flowrate') {
        simulationParams.kex = recommendation.suggestedValue;
      } else if (recommendation.parameter === 'Pb_Rougher1_SIPX_Flowrate') {
        simulationParams.sipx = recommendation.suggestedValue;
      } else if (recommendation.parameter === 'Pb_Concentrate') {
        // For Pb concentrate recommendations, simulate with adjusted KEX and SIPX
        const currentKex = currentControls?.kex || 0;
        const currentSipx = currentControls?.sipx || 0;
        
        if (recommendation.actionType === 'increase') {
          simulationParams.kex = Math.min(currentKex + 5, 80);
          simulationParams.sipx = Math.min(currentSipx + 3, 50);
        } else if (recommendation.actionType === 'decrease') {
          simulationParams.kex = Math.max(currentKex - 5, 0);
          simulationParams.sipx = Math.max(currentSipx - 3, 0);
        }
      }
      
      // Get current settings to complete the simulation parameters
      const apiControls = await flotationAPI.getControlSettings();
      const fullSimulationParams = {
        kex: simulationParams.kex ?? apiControls.kex,
        sipx: simulationParams.sipx ?? apiControls.sipx
      };
      
      // Run simulation via optimization API
      const simulationResult = await flotationAPI.optimizeReagentRates(fullSimulationParams);
      
      // Extract simulation data from the nested structure
      const optimizationData = simulationResult.optimization_result;
      
      if (!optimizationData || !optimizationData.current_simulation || !optimizationData.optimal_simulation) {
        throw new Error('Invalid simulation data structure received from API');
      }
      
      // Get actual current system data instead of optimization result data
      const currentDataResponse = await flotationAPI.getCurrentData();
      const currentSystemData = currentDataResponse;
      
      // Use the average values from the optimization result for optimal predictions
      const optimalRecovery = optimizationData.optimal_avg_recovery;
      const optimalConcentrate = optimizationData.optimal_avg_concentrate;
      
      // Get the optimal settings for display
      const optimalKex = optimizationData.optimal_settings.KEX;
      const optimalSipx = optimizationData.optimal_settings.SIPX;
      
      // Use actual current system data
      const currentRecovery = currentSystemData.Actual_Pb_Recovery || 0; // Already a decimal (0.5 = 50%)
      const currentConcentrate = currentSystemData.Actual_Pb_Concentrate || 0;
      const currentKex = currentSystemData.Pb_Conditioner_KEX_Flowrate;
      const currentSipx = currentSystemData.Pb_Rougher1_SIPX_Flowrate;
      
      setSimulationModal({
        isOpen: true,
        data: {
          currentRecovery,
          optimalRecovery,
          currentConcentrate,
          optimalConcentrate,
          currentKex,
          currentSipx,
          optimalKex,
          optimalSipx,
          simulationParams: fullSimulationParams
        },
        recommendation
      });
      
    } catch (error) {
      console.error('Simulation failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      toast.error(`Simulation failed: ${recommendation.title} - ${errorMessage}`, {
        duration: 5000,
      });
    }
  };

  return (
    <div className="bg-slate-800 border border-slate-600 rounded-xl p-6 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Brain className="h-6 w-6 text-primary-400" />
          <div>
            <h3 className="text-lg font-semibold text-white">Predictive Recommendations</h3>
            <p className="text-sm text-slate-300">AI-powered insights and action suggestions</p>
          </div>
        </div>
        
      </div>

      {/* Loading State */}
      {loading && (
        <RecommendationsSkeleton />
      )}


      {/* Recommendations Grid */}
      {!loading && (groupedRecommendations.actionable.length > 0 || groupedRecommendations.informational.length > 0) && (
        <div className="relative">
          {/* Subtle refreshing overlay */}
          {refreshing && (
            <div className="absolute top-0 right-0 z-10 flex items-center space-x-2 px-3 py-1 bg-primary-600/90 text-white rounded-lg text-xs font-medium">
              <RotateCcw className="h-3 w-3 animate-spin" />
              <span>Updating...</span>
            </div>
          )}
          
          {/* Recommendation count indicator */}
          {allRecommendations.length > 7 && (
            <div className="absolute top-0 left-0 z-10 flex items-center space-x-2 px-3 py-1 bg-slate-600/90 text-white rounded-lg text-xs font-medium">
              <span>Showing {groupedRecommendations.actionable.length + groupedRecommendations.informational.length} of {allRecommendations.length} recommendations</span>
            </div>
          )}

          {/* Actionable Recommendations Section */}
          {groupedRecommendations.actionable.length > 0 && (
            <div className="mb-6">
              <div className="flex items-center space-x-2 mb-3">
                <div className="h-1 w-8 bg-primary-500 rounded"></div>
                <h3 className="text-sm font-semibold text-primary-400 uppercase tracking-wide">Actionable Recommendations</h3>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4">
                {groupedRecommendations.actionable.map((recommendation) => (
            <motion.div
              key={recommendation.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`bg-slate-700/50 rounded-lg p-4 border border-slate-600 hover:border-primary-500/50 transition-all duration-200 ${
                selectedRecommendation === recommendation.id ? 'ring-2 ring-primary-500/50' : ''
              }`}
              onClick={() => setSelectedRecommendation(recommendation.id)}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  {getRecommendationIcon(recommendation.type)}
                  <div>
                    <h4 className="text-sm font-semibold text-white">{recommendation.title}</h4>
                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(recommendation.impact || 'medium')}`}>
                      {(recommendation.impact || 'medium').toUpperCase()} IMPACT
                    </span>
                  </div>
                </div>
                <div className="flex items-center space-x-1 text-xs text-slate-400">
                  <Clock className="h-3 w-3" />
                  <span>{recommendation.timeHorizon}</span>
                </div>
              </div>

              {/* Description */}
              <p className="text-sm text-slate-300 mb-3">{recommendation.description}</p>

              {/* Parameter Details */}
              <div className="bg-slate-600/50 rounded-lg p-3 mb-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-slate-400">Parameter</span>
                  <span className="text-xs text-slate-400">Current → Suggested</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-white">{recommendation.parameter}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-slate-300">{recommendation.currentValue}</span>
                    <ArrowUp className="h-3 w-3 text-primary-400" />
                    <span className="text-sm font-medium text-primary-400">{recommendation.suggestedValue}</span>
                  </div>
                </div>
              </div>

              {/* Expected Outcome */}
              <div className="mb-3">
                <span className="text-xs text-slate-400">Expected Outcome:</span>
                <p className="text-sm text-white font-medium">{recommendation.expectedOutcome}</p>
              </div>

              {/* Confidence */}
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs text-slate-400">Model Confidence</span>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-slate-600 rounded-full h-2">
                    <div 
                      className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(recommendation.confidence || 0.8) * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-white">{((recommendation.confidence || 0.8) * 100).toFixed(0)}%</span>
                </div>
              </div>

              {/* Action Buttons */}
              {/* Only show action buttons for actionable recommendations */}
              {recommendation.actionType !== 'info' && (
                <div className="flex space-x-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleQuickAction(recommendation);
                    }}
                    className={`flex items-center space-x-1 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-200 ${
                      recommendation.actionType === 'increase' 
                        ? 'bg-success-600 text-white hover:bg-success-700'
                        : recommendation.actionType === 'decrease'
                        ? 'bg-warning-600 text-white hover:bg-warning-700'
                        : 'bg-primary-600 text-white hover:bg-primary-700'
                    }`}
                  >
                    {getActionIcon(recommendation.actionType || 'maintain')}
                    <span>Quick Action</span>
                  </button>
                  
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSimulateScenario(recommendation);
                    }}
                    className="flex items-center space-x-1 px-3 py-2 bg-slate-600 text-slate-300 hover:text-white rounded-lg text-xs font-medium transition-all duration-200"
                  >
                    <Zap className="h-3 w-3" />
                    <span>Simulate</span>
                  </button>
                </div>
              )}
              
              {/* Show "Info Only" label for informational recommendations */}
              {recommendation.actionType === 'info' && (
                <div className="flex items-center space-x-1 px-3 py-2 bg-slate-700/50 text-slate-400 rounded-lg text-xs font-medium">
                  <Info className="h-3 w-3" />
                  <span>Info Only</span>
                </div>
              )}
            </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Informational Recommendations Section */}
          {groupedRecommendations.informational.length > 0 && (
            <div>
              <div className="flex items-center space-x-2 mb-3">
                <div className="h-1 w-8 bg-slate-500 rounded"></div>
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wide">System Status</h3>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 sm:gap-4">
                {groupedRecommendations.informational.map((recommendation) => (
                  <motion.div
                    key={recommendation.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-slate-700/30 rounded-lg p-4 border border-slate-600/50 hover:border-slate-500/50 transition-all duration-200"
                  >
                    {/* Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        {getRecommendationIcon(recommendation.type)}
                        <span className="text-sm font-medium text-slate-300">{recommendation.title}</span>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(recommendation.impact)}`}>
                        {recommendation.impact.toUpperCase()}
                      </span>
                    </div>

                    {/* Description */}
                    <p className="text-sm text-slate-400 mb-3 leading-relaxed">
                      {recommendation.description}
                    </p>

                    {/* Info Only label */}
                    <div className="flex items-center space-x-1 px-3 py-2 bg-slate-700/50 text-slate-400 rounded-lg text-xs font-medium">
                      <Info className="h-3 w-3" />
                      <span>Info Only</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* All Systems Optimal - Single TARGETS ACHIEVED recommendation */}
      {!loading && groupedRecommendations.actionable.length === 0 && groupedRecommendations.informational.length === 1 && 
       groupedRecommendations.informational[0]?.title === 'TARGETS ACHIEVED' && (
        <div className="text-center py-12">
          <div className="bg-gradient-to-br from-success-500/20 to-success-600/20 rounded-2xl p-8 border border-success-500/30">
            <CheckCircle className="h-16 w-16 text-success-400 mx-auto mb-6" />
            <h3 className="text-2xl font-bold text-success-400 mb-3">TARGETS ACHIEVED</h3>
            <h4 className="text-lg font-semibold text-white mb-2">All Systems Optimal</h4>
            <p className="text-slate-300 mb-4">Your flotation process is performing at peak efficiency</p>
            <div className="flex items-center justify-center space-x-2 text-sm text-slate-400">
              <div className="h-1 w-8 bg-success-500 rounded"></div>
              <span>No immediate action required</span>
              <div className="h-1 w-8 bg-success-500 rounded"></div>
            </div>
          </div>
        </div>
      )}

      {/* No Recommendations - True empty state */}
      {!loading && groupedRecommendations.actionable.length === 0 && groupedRecommendations.informational.length === 0 && (
        <div className="text-center py-8">
          <CheckCircle className="h-12 w-12 text-success-400 mx-auto mb-4" />
          <h4 className="text-lg font-semibold text-white mb-2">All Systems Optimal</h4>
          <p className="text-slate-300">No immediate recommendations at this time</p>
        </div>
      )}


      {/* Simulation Results Modal */}
      {simulationModal.isOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-slate-800 border border-slate-600 rounded-xl p-4 max-w-lg w-full max-h-[80vh] overflow-y-auto shadow-sm"
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-primary-600 rounded-lg">
                  <Zap className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Simulation Results</h3>
                  <p className="text-sm text-slate-300">{simulationModal.recommendation?.title}</p>
                </div>
              </div>
              <button
                onClick={() => setSimulationModal({ isOpen: false, data: null, recommendation: null })}
                className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
              >
                <svg className="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Simulation Data */}
            {simulationModal.data && (
              <div className="space-y-4">
                {/* Current vs Expected Comparison */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
                  {/* Current Settings */}
                  <div className="bg-slate-700/50 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-slate-300 mb-3">Current Settings</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-slate-400">KEX Flowrate:</span>
                        <span className="text-sm font-medium text-white">{simulationModal.data.currentKex}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-slate-400">SIPX Flowrate:</span>
                        <span className="text-sm font-medium text-white">{simulationModal.data.currentSipx}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-slate-400">Pb Concentrate:</span>
                        <span className="text-sm font-medium text-white">{simulationModal.data.currentConcentrate.toFixed(2)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-slate-400">Recovery Rate:</span>
                        <span className="text-sm font-medium text-white">{(simulationModal.data.currentRecovery * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>

                  {/* Expected Outcome */}
                  <div className="bg-slate-700/50 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-slate-300 mb-3">Expected Outcome</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-slate-400">KEX Flowrate:</span>
                        <span className="text-sm font-medium text-primary-400">{simulationModal.data.optimalKex}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-slate-400">SIPX Flowrate:</span>
                        <span className="text-sm font-medium text-primary-400">{simulationModal.data.optimalSipx}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-slate-400">Pb Concentrate:</span>
                        <span className="text-sm font-medium text-primary-400">{simulationModal.data.optimalConcentrate.toFixed(2)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-slate-400">Recovery Rate:</span>
                        <span className="text-sm font-medium text-primary-400">{(simulationModal.data.optimalRecovery * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Performance Impact */}
                <div className="bg-slate-700/50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-slate-300 mb-3">Performance Impact</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-white mb-1">
                        {((simulationModal.data.optimalConcentrate - simulationModal.data.currentConcentrate) / simulationModal.data.currentConcentrate * 100).toFixed(1)}%
                      </div>
                      <div className="text-xs text-slate-400">Pb Concentrate Change</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-white mb-1">
                        {((simulationModal.data.optimalRecovery - simulationModal.data.currentRecovery) / simulationModal.data.currentRecovery * 100).toFixed(1)}%
                      </div>
                      <div className="text-xs text-slate-400">Recovery Rate Change</div>
                    </div>
                  </div>
                </div>

                {/* Recommendation Details */}
                {simulationModal.recommendation && (
                  <div className="bg-slate-700/50 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-slate-300 mb-3">Recommendation Details</h4>
                    <div className="space-y-2">
                      <p className="text-sm text-white">{simulationModal.recommendation.description}</p>
                      <p className="text-sm text-slate-300">{simulationModal.recommendation.expectedOutcome}</p>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-slate-400">Time Horizon:</span>
                        <span className="text-xs font-medium text-white">{simulationModal.recommendation.timeHorizon}</span>
                        <span className="text-xs text-slate-400">•</span>
                        <span className="text-xs text-slate-400">Confidence:</span>
                        <span className="text-xs font-medium text-white">{((simulationModal.recommendation.confidence || 0.8) * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex space-x-3 pt-4">
                  <button
                    onClick={async () => {
                      if (simulationModal.data) {
                        try {
                          // Apply the optimal settings from the simulation
                          const optimalControls = {
                            kex: simulationModal.data.optimalKex,
                            sipx: simulationModal.data.optimalSipx
                          };
                          
                          
                          // Update control settings via API
                          await flotationAPI.updateControls(optimalControls);
                          
                          // Update the parent component's controls state
                          if (onControlChange) {
                            onControlChange(optimalControls);
                          }
                          
                          // Show success message
                          toast.success(`Applied optimal settings: KEX=${optimalControls.kex}, SIPX=${optimalControls.sipx}`, {
                            duration: 4000,
                          });
                          
                          // Close modal
                          setSimulationModal({ isOpen: false, data: null, recommendation: null });
                          
                          // Refresh predictions after control change
                          setTimeout(() => {
                            fetchPredictions(currentData, false);
                          }, 2000);
                          
                        } catch (error) {
                          console.error('Failed to apply optimal settings:', error);
                          const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
                          toast.error(`Failed to apply optimal settings: ${errorMessage}`, {
                            duration: 5000,
                          });
                        }
                      }
                    }}
                    className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-success-600 hover:bg-success-700 text-white rounded-lg font-medium transition-colors"
                  >
                    <ArrowUp className="h-4 w-4" />
                    <span>Apply Changes</span>
                  </button>
                  <button
                    onClick={() => setSimulationModal({ isOpen: false, data: null, recommendation: null })}
                    className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-slate-600 hover:bg-slate-700 text-white rounded-lg font-medium transition-colors"
                  >
                    <span>Close</span>
                  </button>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      )}

      {/* Quick Action Results Modal */}
      {quickActionModal.isOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-slate-800 border border-slate-600 rounded-xl p-6 max-w-md w-full"
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${
                  quickActionModal.success 
                    ? 'bg-success-600' 
                    : 'bg-danger-600'
                }`}>
                  {quickActionModal.success ? (
                    <CheckCircle className="h-5 w-5 text-white" />
                  ) : (
                    <AlertTriangle className="h-5 w-5 text-white" />
                  )}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">
                    {quickActionModal.success ? 'Quick Action Applied' : 'Quick Action Failed'}
                  </h3>
                  <p className="text-sm text-slate-300">
                    {quickActionModal.recommendation?.title}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setQuickActionModal({ isOpen: false, recommendation: null, success: false, message: '' })}
                className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
              >
                <svg className="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Content */}
            <div className="space-y-4">
              {/* Action Details */}
              {quickActionModal.recommendation && (
                <div className="bg-slate-700/50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-slate-300 mb-3">Action Details</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-slate-400">Parameter:</span>
                      <span className="text-sm font-medium text-white">
                        {quickActionModal.recommendation.parameter}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-slate-400">Current Value:</span>
                      <span className="text-sm font-medium text-white">
                        {quickActionModal.recommendation.currentValue}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-slate-400">Suggested Value:</span>
                      <span className="text-sm font-medium text-primary-400">
                        {quickActionModal.recommendation.suggestedValue}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-slate-400">Action Type:</span>
                      <span className={`text-sm font-medium capitalize ${
                        quickActionModal.recommendation.actionType === 'increase' 
                          ? 'text-success-400'
                          : quickActionModal.recommendation.actionType === 'decrease'
                          ? 'text-warning-400'
                          : 'text-primary-400'
                      }`}>
                        {quickActionModal.recommendation.actionType}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Message */}
              <div className={`p-4 rounded-lg ${
                quickActionModal.success 
                  ? 'bg-success-900/20 border border-success-600/30' 
                  : 'bg-danger-900/20 border border-danger-600/30'
              }`}>
                <div className="flex items-start space-x-3">
                  {quickActionModal.success ? (
                    <CheckCircle className="h-5 w-5 text-success-400 mt-0.5 flex-shrink-0" />
                  ) : (
                    <AlertTriangle className="h-5 w-5 text-danger-400 mt-0.5 flex-shrink-0" />
                  )}
                  <div>
                    <p className={`text-sm font-medium ${
                      quickActionModal.success ? 'text-success-400' : 'text-danger-400'
                    }`}>
                      {quickActionModal.success ? 'Success!' : 'Action Failed'}
                    </p>
                    <p className="text-sm text-white mt-1">
                      {quickActionModal.message}
                    </p>
                  </div>
                </div>
              </div>

              {/* Expected Outcome */}
              {quickActionModal.recommendation && quickActionModal.success && (
                <div className="bg-slate-700/50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-slate-300 mb-2">Expected Outcome</h4>
                  <p className="text-sm text-white">
                    {quickActionModal.recommendation.expectedOutcome}
                  </p>
                  <div className="flex items-center space-x-2 mt-2">
                    <span className="text-xs text-slate-400">Time Horizon:</span>
                    <span className="text-xs font-medium text-white">
                      {quickActionModal.recommendation.timeHorizon}
                    </span>
                    <span className="text-xs text-slate-400">•</span>
                    <span className="text-xs text-slate-400">Confidence:</span>
                    <span className="text-xs font-medium text-white">
                      {((quickActionModal.recommendation.confidence || 0.8) * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              )}

              {/* Action Button */}
              <div className="flex justify-end pt-4">
                <button
                  onClick={() => setQuickActionModal({ isOpen: false, recommendation: null, success: false, message: '' })}
                  className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                    quickActionModal.success
                      ? 'bg-success-600 hover:bg-success-700 text-white'
                      : 'bg-slate-600 hover:bg-slate-700 text-white'
                  }`}
                >
                  {quickActionModal.success ? 'Continue' : 'Close'}
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default PredictiveRecommendations;
