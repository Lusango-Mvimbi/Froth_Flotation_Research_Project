import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
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
import { FlotationData, FuturePredictionResponse, ProcessControls } from '../types';
import { flotationAPI } from '../services/api';

interface PredictiveRecommendationsProps {
  currentData: FlotationData | null;
  targetRanges: any;
  onControlChange?: (controls: ProcessControls) => void;
  currentControls?: ProcessControls;
}

interface Recommendation {
  id: string;
  type: 'improvement' | 'risk' | 'optimization' | 'info';
  title: string;
  description: string;
  parameter: string;
  currentValue: number;
  suggestedValue: number;
  expectedOutcome: string;
  timeHorizon: string;
  confidence: number;
  impact: 'high' | 'medium' | 'low';
  actionType: 'increase' | 'decrease' | 'maintain';
}

const PredictiveRecommendations: React.FC<PredictiveRecommendationsProps> = ({ 
  currentData, 
  targetRanges,
  onControlChange,
  currentControls 
}) => {
  const [futurePredictions, setFuturePredictions] = useState<FuturePredictionResponse | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
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
      // Only show loading on initial load, not on subsequent updates
      const isInitialLoad = !futurePredictions;
      fetchFuturePredictions(isInitialLoad);
    }
  }, [currentData]);

  // Generate recommendations when predictions change
  useEffect(() => {
    if (futurePredictions && currentData) {
      generateRecommendations();
    }
  }, [futurePredictions, currentData]);

  const fetchFuturePredictions = async (isInitialLoad = false) => {
    if (!currentData) return;
    
    // Only show full loading state on initial load
    if (isInitialLoad) {
      setLoading(true);
    } else {
      setRefreshing(true);
    }
    
    try {
      const inputData = {
        Feed_Pb: currentData.Feed_Pb,
        Feed_Zn: currentData.Feed_Zn,
        Pb_Conditioner_KEX_Flowrate: currentData.Pb_Conditioner_KEX_Flowrate,
        Pb_Rougher1_SIPX_Flowrate: currentData.Pb_Rougher1_SIPX_Flowrate,
        Pb_Rougher1_AirFlow: currentData.Pb_Rougher1_AirFlow,
        Pb_Rougher1_Level: currentData.Pb_Rougher1_Level,
      };
      
      const futureData = await flotationAPI.getFuturePredictions(inputData);
      setFuturePredictions(futureData);
    } catch (error) {
      console.error('Failed to fetch future predictions:', error);
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      } else {
        setRefreshing(false);
      }
    }
  };

  const generateRecommendations = () => {
    if (!futurePredictions || !currentData) return;

    const newRecommendations: Recommendation[] = [];
    const currentPb = currentData.Actual_Pb_Concentrate || currentData.Predicted_Pb_Concentrate || 0;
    const targetPb = targetRanges?.pb_concentrate?.optimal || 20;

    // Analyze 5-minute predictions
    const pred5min = futurePredictions.future_predictions['5min'];
    if (pred5min) {
      const change5min = pred5min.prediction - currentPb;
      
      if (change5min > 2) {
        // Significant improvement expected
        newRecommendations.push({
          id: '5min-improvement',
          type: 'improvement',
          title: 'Strong Performance Expected',
          description: `Pb concentrate is predicted to increase by ${change5min.toFixed(2)}% in 5 minutes`,
          parameter: 'Pb_Concentrate',
          currentValue: currentPb,
          suggestedValue: pred5min.prediction,
          expectedOutcome: `Expected to reach ${pred5min.prediction.toFixed(2)}% Pb concentrate`,
          timeHorizon: '5 minutes',
          confidence: pred5min.model_performance.r2_score,
          impact: 'high',
          actionType: 'maintain'
        });
      } else if (change5min < -2) {
        // Potential decline
        newRecommendations.push({
          id: '5min-risk',
          type: 'risk',
          title: 'Performance Decline Warning',
          description: `Pb concentrate is predicted to decrease by ${Math.abs(change5min).toFixed(2)}% in 5 minutes`,
          parameter: 'Pb_Concentrate',
          currentValue: currentPb,
          suggestedValue: pred5min.prediction,
          expectedOutcome: `May drop to ${pred5min.prediction.toFixed(2)}% Pb concentrate`,
          timeHorizon: '5 minutes',
          confidence: pred5min.model_performance.r2_score,
          impact: 'high',
          actionType: 'increase'
        });
      }
    }

    // Analyze 60-minute predictions
    const pred60min = futurePredictions.future_predictions['60min'];
    if (pred60min) {
      const change60min = pred60min.prediction - currentPb;
      
      if (change60min > 3) {
        newRecommendations.push({
          id: '60min-optimization',
          type: 'optimization',
          title: 'Long-term Optimization Opportunity',
          description: `Significant improvement expected: +${change60min.toFixed(2)}% in 60 minutes`,
          parameter: 'Pb_Concentrate',
          currentValue: currentPb,
          suggestedValue: pred60min.prediction,
          expectedOutcome: `Could reach ${pred60min.prediction.toFixed(2)}% Pb concentrate`,
          timeHorizon: '60 minutes',
          confidence: pred60min.model_performance.r2_score,
          impact: 'medium',
          actionType: 'maintain'
        });
      } else if (change60min < -3) {
        newRecommendations.push({
          id: '60min-risk-long',
          type: 'risk',
          title: 'Long-term Performance Risk',
          description: `Sustained decline predicted: -${Math.abs(change60min).toFixed(2)}% in 60 minutes`,
          parameter: 'Pb_Concentrate',
          currentValue: currentPb,
          suggestedValue: pred60min.prediction,
          expectedOutcome: `May decline to ${pred60min.prediction.toFixed(2)}% Pb concentrate`,
          timeHorizon: '60 minutes',
          confidence: pred60min.model_performance.r2_score,
          impact: 'high',
          actionType: 'increase'
        });
      }
    }

    // Parameter-specific recommendations
    if (currentData.Pb_Conditioner_KEX_Flowrate < 50) {
      newRecommendations.push({
        id: 'kex-increase',
        type: 'optimization',
        title: 'Increase KEX Flowrate',
        description: 'Current KEX flowrate is below optimal range',
        parameter: 'Pb_Conditioner_KEX_Flowrate',
        currentValue: currentData.Pb_Conditioner_KEX_Flowrate,
        suggestedValue: Math.min(currentData.Pb_Conditioner_KEX_Flowrate + 10, 80),
        expectedOutcome: 'Expected to improve Pb concentrate by 1-2%',
        timeHorizon: '15-30 minutes',
        confidence: 0.75,
        impact: 'medium',
        actionType: 'increase'
      });
    }

    // Air flow optimization (decrease scenarios)
    if (currentData.Pb_Rougher1_AirFlow > 15) {
      newRecommendations.push({
        id: 'airflow-decrease',
        type: 'optimization',
        title: 'Reduce Air Flow',
        description: 'Air flow is above optimal range',
        parameter: 'Pb_Rougher1_AirFlow',
        currentValue: currentData.Pb_Rougher1_AirFlow,
        suggestedValue: Math.max(currentData.Pb_Rougher1_AirFlow - 2, 8),
        expectedOutcome: 'Expected to stabilize Pb concentrate',
        timeHorizon: '10-20 minutes',
        confidence: 0.70,
        impact: 'low',
        actionType: 'decrease'
      });
    }

    // SIPX flow rate optimization (decrease scenarios)
    if (currentData.Pb_Rougher1_SIPX_Flowrate > 35) {
      newRecommendations.push({
        id: 'sipx-decrease',
        type: 'optimization',
        title: 'Reduce SIPX Flow Rate',
        description: 'SIPX flow rate is above optimal range',
        parameter: 'Pb_Rougher1_SIPX_Flowrate',
        currentValue: currentData.Pb_Rougher1_SIPX_Flowrate,
        suggestedValue: Math.max(currentData.Pb_Rougher1_SIPX_Flowrate - 5, 20),
        expectedOutcome: 'Expected to reduce reagent waste and improve efficiency',
        timeHorizon: '15-30 minutes',
        confidence: 0.75,
        impact: 'medium',
        actionType: 'decrease'
      });
    }

    // KEX flow rate optimization (decrease scenarios)
    if (currentData.Pb_Conditioner_KEX_Flowrate > 70) {
      newRecommendations.push({
        id: 'kex-decrease',
        type: 'optimization',
        title: 'Reduce KEX Flow Rate',
        description: 'KEX flow rate is above optimal range',
        parameter: 'Pb_Conditioner_KEX_Flowrate',
        currentValue: currentData.Pb_Conditioner_KEX_Flowrate,
        suggestedValue: Math.max(currentData.Pb_Conditioner_KEX_Flowrate - 8, 50),
        expectedOutcome: 'Expected to reduce reagent consumption while maintaining performance',
        timeHorizon: '20-40 minutes',
        confidence: 0.80,
        impact: 'medium',
        actionType: 'decrease'
      });
    }

    // Model confidence recommendations
    if (pred5min && pred5min.model_performance.r2_score < 0.7) {
      newRecommendations.push({
        id: 'low-confidence',
        type: 'info',
        title: 'Low Prediction Confidence',
        description: 'Model confidence is below 70%',
        parameter: 'Model_Confidence',
        currentValue: pred5min.model_performance.r2_score * 100,
        suggestedValue: 80,
        expectedOutcome: 'Consider manual verification of predictions',
        timeHorizon: 'Immediate',
        confidence: pred5min.model_performance.r2_score,
        impact: 'low',
        actionType: 'maintain'
      });
    }

    setRecommendations(newRecommendations);
  };

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
        return <Info className="h-5 w-5 text-dark-400" />;
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'text-danger-400 bg-danger-900/20';
      case 'medium':
        return 'text-warning-400 bg-warning-900/20';
      case 'low':
        return 'text-info-400 bg-info-900/20';
      default:
        return 'text-dark-400 bg-dark-700/20';
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
      console.log('Quick action triggered:', recommendation);
      
      // Map recommendation parameters to control settings
      let controlSettings: { kex?: number; sipx?: number } = {};
      
      console.log('Mapping recommendation parameter:', recommendation.parameter, 'to control settings');
      
      if (recommendation.parameter === 'Pb_Conditioner_KEX_Flowrate') {
        controlSettings.kex = recommendation.suggestedValue;
        console.log('Setting KEX to:', recommendation.suggestedValue);
      } else if (recommendation.parameter === 'Pb_Rougher1_SIPX_Flowrate') {
        controlSettings.sipx = recommendation.suggestedValue;
        console.log('Setting SIPX to:', recommendation.suggestedValue);
      } else if (recommendation.parameter === 'Pb_Rougher1_AirFlow') {
        // Air flow is not directly controllable via KEX/SIPX, but we can adjust them as a proxy
        const currentKex = currentControls?.kex || currentData?.Pb_Conditioner_KEX_Flowrate || 0;
        const currentSipx = currentControls?.sipx || currentData?.Pb_Rougher1_SIPX_Flowrate || 0;
        
        if (recommendation.actionType === 'decrease') {
          // Reduce KEX and SIPX to compensate for high air flow
          controlSettings.kex = Math.max(currentKex - 3, 30);
          controlSettings.sipx = Math.max(currentSipx - 2, 15);
          console.log('Adjusting KEX/SIPX due to high air flow');
        }
      } else if (recommendation.parameter === 'Pb_Concentrate') {
        // For Pb concentrate recommendations, we need to adjust KEX and SIPX
        // This is a simplified approach - in reality, you'd use optimization algorithms
        const currentKex = currentControls?.kex || currentData?.Pb_Conditioner_KEX_Flowrate || 0;
        const currentSipx = currentControls?.sipx || currentData?.Pb_Rougher1_SIPX_Flowrate || 0;
        
        if (recommendation.actionType === 'increase') {
          controlSettings.kex = Math.min(currentKex + 5, 80);
          controlSettings.sipx = Math.min(currentSipx + 3, 50);
          console.log('Increasing KEX/SIPX for better Pb concentrate');
        } else if (recommendation.actionType === 'decrease') {
          controlSettings.kex = Math.max(currentKex - 5, 0);
          controlSettings.sipx = Math.max(currentSipx - 3, 0);
          console.log('Decreasing KEX/SIPX for better Pb concentrate');
        }
      }
      
      // Only proceed if we have valid control settings
      if (Object.keys(controlSettings).length > 0) {
        console.log('Control settings to apply:', controlSettings);
        
        // Get current settings to ensure we have both kex and sipx
        const apiControls = await flotationAPI.getControlSettings();
        console.log('Current controls from API:', apiControls);
        
        const fullControlSettings: ProcessControls = {
          kex: controlSettings.kex ?? apiControls.kex,
          sipx: controlSettings.sipx ?? apiControls.sipx
        };
        
        console.log('Full control settings to send:', fullControlSettings);
        
        // Update control settings via API
        await flotationAPI.updateControls(fullControlSettings);
        console.log('API update completed');
        
        // Update the parent component's controls state to refresh the UI
        if (onControlChange) {
          console.log('Calling onControlChange with:', fullControlSettings);
          onControlChange(fullControlSettings);
          console.log('onControlChange called successfully');
        } else {
          console.warn('onControlChange callback is not available');
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
          fetchFuturePredictions(false);
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
        const currentKex = currentControls?.kex || currentData?.Pb_Conditioner_KEX_Flowrate || 0;
        const currentSipx = currentControls?.sipx || currentData?.Pb_Rougher1_SIPX_Flowrate || 0;
        
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
      
      // Display simulation results in modal
      const currentRecovery = simulationResult.current_simulation?.recovery_rates?.[0] || 0;
      const optimalRecovery = simulationResult.optimal_simulation?.recovery_rates?.[0] || 0;
      const currentConcentrate = simulationResult.current_simulation?.pb_concentrates?.[0] || 0;
      const optimalConcentrate = simulationResult.optimal_simulation?.pb_concentrates?.[0] || 0;
      
      setSimulationModal({
        isOpen: true,
        data: {
          currentRecovery,
          optimalRecovery,
          currentConcentrate,
          optimalConcentrate,
          simulationParams: fullSimulationParams
        },
        recommendation
      });
      
    } catch (error) {
      console.error('Simulation failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      alert(`❌ Simulation failed: ${recommendation.title}\n\nError: ${errorMessage}`);
    }
  };

  return (
    <div className="bg-dark-800/50 backdrop-blur-sm border border-dark-600 rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Brain className="h-6 w-6 text-primary-400" />
          <div>
            <h3 className="text-lg font-semibold text-white">Predictive Recommendations</h3>
            <p className="text-sm text-dark-300">AI-powered insights and action suggestions</p>
          </div>
        </div>
        
        <button
          onClick={() => fetchFuturePredictions(false)}
          disabled={loading || refreshing}
          className="flex items-center space-x-2 px-3 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium transition-all duration-200 hover:bg-primary-700 disabled:opacity-50"
        >
          <RotateCcw className={`h-4 w-4 ${(loading || refreshing) ? 'animate-spin' : ''}`} />
          <span>{refreshing ? 'Refreshing...' : 'Refresh'}</span>
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-400 mx-auto mb-4"></div>
          <p className="text-dark-300">Analyzing predictions...</p>
        </div>
      )}

      {/* Recommendations Grid */}
      {!loading && recommendations.length > 0 && (
        <div className="relative">
          {/* Subtle refreshing overlay */}
          {refreshing && (
            <div className="absolute top-0 right-0 z-10 flex items-center space-x-2 px-3 py-1 bg-primary-600/90 text-white rounded-lg text-xs font-medium">
              <RotateCcw className="h-3 w-3 animate-spin" />
              <span>Updating...</span>
            </div>
          )}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {recommendations.map((recommendation) => (
            <motion.div
              key={recommendation.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`bg-dark-700/50 rounded-lg p-4 border border-dark-600 hover:border-primary-500/50 transition-all duration-200 ${
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
                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(recommendation.impact)}`}>
                      {recommendation.impact.toUpperCase()} IMPACT
                    </span>
                  </div>
                </div>
                <div className="flex items-center space-x-1 text-xs text-dark-400">
                  <Clock className="h-3 w-3" />
                  <span>{recommendation.timeHorizon}</span>
                </div>
              </div>

              {/* Description */}
              <p className="text-sm text-dark-300 mb-3">{recommendation.description}</p>

              {/* Parameter Details */}
              <div className="bg-dark-600/50 rounded-lg p-3 mb-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-dark-400">Parameter</span>
                  <span className="text-xs text-dark-400">Current → Suggested</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-white">{recommendation.parameter}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-dark-300">{recommendation.currentValue}</span>
                    <ArrowUp className="h-3 w-3 text-primary-400" />
                    <span className="text-sm font-medium text-primary-400">{recommendation.suggestedValue}</span>
                  </div>
                </div>
              </div>

              {/* Expected Outcome */}
              <div className="mb-3">
                <span className="text-xs text-dark-400">Expected Outcome:</span>
                <p className="text-sm text-white font-medium">{recommendation.expectedOutcome}</p>
              </div>

              {/* Confidence */}
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs text-dark-400">Model Confidence</span>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-dark-600 rounded-full h-2">
                    <div 
                      className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${recommendation.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-white">{(recommendation.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>

              {/* Action Buttons */}
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
                  {getActionIcon(recommendation.actionType)}
                  <span>Quick Action</span>
                </button>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSimulateScenario(recommendation);
                  }}
                  className="flex items-center space-x-1 px-3 py-2 bg-dark-600 text-dark-300 hover:text-white rounded-lg text-xs font-medium transition-all duration-200"
                >
                  <Zap className="h-3 w-3" />
                  <span>Simulate</span>
                </button>
              </div>
            </motion.div>
          ))}
          </div>
        </div>
      )}

      {/* No Recommendations */}
      {!loading && recommendations.length === 0 && (
        <div className="text-center py-8">
          <CheckCircle className="h-12 w-12 text-success-400 mx-auto mb-4" />
          <h4 className="text-lg font-semibold text-white mb-2">All Systems Optimal</h4>
          <p className="text-dark-300">No immediate recommendations at this time</p>
        </div>
      )}

      {/* Future Predictions Summary */}
      {futurePredictions && (
        <div className="mt-6 p-4 bg-dark-700/30 rounded-lg">
          <h4 className="text-sm font-medium text-dark-300 mb-3">Prediction Summary</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(futurePredictions.future_predictions).map(([horizon, prediction]) => {
              const currentValue = currentData?.Actual_Pb_Concentrate || currentData?.Predicted_Pb_Concentrate || 0;
              const change = prediction.prediction - currentValue;
              
              return (
                <div key={horizon} className="flex items-center justify-between">
                  <span className="text-sm text-dark-300">{horizon} Forecast</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-white">
                      {prediction.prediction.toFixed(2)}%
                    </span>
                    {change > 0 ? (
                      <TrendingUp className="h-4 w-4 text-success-400" />
                    ) : change < 0 ? (
                      <TrendingDown className="h-4 w-4 text-danger-400" />
                    ) : (
                      <div className="h-4 w-4 text-dark-400">—</div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Simulation Results Modal */}
      {simulationModal.isOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-dark-800 border border-dark-600 rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-primary-600 rounded-lg">
                  <Zap className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Simulation Results</h3>
                  <p className="text-sm text-dark-300">{simulationModal.recommendation?.title}</p>
                </div>
              </div>
              <button
                onClick={() => setSimulationModal({ isOpen: false, data: null, recommendation: null })}
                className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
              >
                <svg className="h-5 w-5 text-dark-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Simulation Data */}
            {simulationModal.data && (
              <div className="space-y-6">
                {/* Current vs Expected Comparison */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Current Settings */}
                  <div className="bg-dark-700/50 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-dark-300 mb-3">Current Settings</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-dark-400">KEX Flowrate:</span>
                        <span className="text-sm font-medium text-white">{simulationModal.data.simulationParams.kex}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-dark-400">SIPX Flowrate:</span>
                        <span className="text-sm font-medium text-white">{simulationModal.data.simulationParams.sipx}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-dark-400">Pb Concentrate:</span>
                        <span className="text-sm font-medium text-white">{simulationModal.data.currentConcentrate.toFixed(2)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-dark-400">Recovery Rate:</span>
                        <span className="text-sm font-medium text-white">{(simulationModal.data.currentRecovery * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>

                  {/* Expected Outcome */}
                  <div className="bg-dark-700/50 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-dark-300 mb-3">Expected Outcome</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-dark-400">KEX Flowrate:</span>
                        <span className="text-sm font-medium text-primary-400">{simulationModal.data.simulationParams.kex}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-dark-400">SIPX Flowrate:</span>
                        <span className="text-sm font-medium text-primary-400">{simulationModal.data.simulationParams.sipx}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-dark-400">Pb Concentrate:</span>
                        <span className="text-sm font-medium text-primary-400">{simulationModal.data.optimalConcentrate.toFixed(2)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-dark-400">Recovery Rate:</span>
                        <span className="text-sm font-medium text-primary-400">{(simulationModal.data.optimalRecovery * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Performance Impact */}
                <div className="bg-dark-700/50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-dark-300 mb-3">Performance Impact</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-white mb-1">
                        {((simulationModal.data.optimalConcentrate - simulationModal.data.currentConcentrate) / simulationModal.data.currentConcentrate * 100).toFixed(1)}%
                      </div>
                      <div className="text-xs text-dark-400">Pb Concentrate Change</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-white mb-1">
                        {((simulationModal.data.optimalRecovery - simulationModal.data.currentRecovery) / simulationModal.data.currentRecovery * 100).toFixed(1)}%
                      </div>
                      <div className="text-xs text-dark-400">Recovery Rate Change</div>
                    </div>
                  </div>
                </div>

                {/* Recommendation Details */}
                {simulationModal.recommendation && (
                  <div className="bg-dark-700/50 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-dark-300 mb-3">Recommendation Details</h4>
                    <div className="space-y-2">
                      <p className="text-sm text-white">{simulationModal.recommendation.description}</p>
                      <p className="text-sm text-dark-300">{simulationModal.recommendation.expectedOutcome}</p>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-dark-400">Time Horizon:</span>
                        <span className="text-xs font-medium text-white">{simulationModal.recommendation.timeHorizon}</span>
                        <span className="text-xs text-dark-400">•</span>
                        <span className="text-xs text-dark-400">Confidence:</span>
                        <span className="text-xs font-medium text-white">{(simulationModal.recommendation.confidence * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex space-x-3 pt-4">
                  <button
                    onClick={() => {
                      if (simulationModal.recommendation) {
                        handleQuickAction(simulationModal.recommendation);
                        setSimulationModal({ isOpen: false, data: null, recommendation: null });
                      }
                    }}
                    className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-success-600 hover:bg-success-700 text-white rounded-lg font-medium transition-colors"
                  >
                    <ArrowUp className="h-4 w-4" />
                    <span>Apply Changes</span>
                  </button>
                  <button
                    onClick={() => setSimulationModal({ isOpen: false, data: null, recommendation: null })}
                    className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-dark-600 hover:bg-dark-700 text-white rounded-lg font-medium transition-colors"
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
            className="bg-dark-800 border border-dark-600 rounded-xl p-6 max-w-md w-full"
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
                  <p className="text-sm text-dark-300">
                    {quickActionModal.recommendation?.title}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setQuickActionModal({ isOpen: false, recommendation: null, success: false, message: '' })}
                className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
              >
                <svg className="h-5 w-5 text-dark-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Content */}
            <div className="space-y-4">
              {/* Action Details */}
              {quickActionModal.recommendation && (
                <div className="bg-dark-700/50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-dark-300 mb-3">Action Details</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-dark-400">Parameter:</span>
                      <span className="text-sm font-medium text-white">
                        {quickActionModal.recommendation.parameter}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-dark-400">Current Value:</span>
                      <span className="text-sm font-medium text-white">
                        {quickActionModal.recommendation.currentValue}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-dark-400">Suggested Value:</span>
                      <span className="text-sm font-medium text-primary-400">
                        {quickActionModal.recommendation.suggestedValue}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-dark-400">Action Type:</span>
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
                <div className="bg-dark-700/50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-dark-300 mb-2">Expected Outcome</h4>
                  <p className="text-sm text-white">
                    {quickActionModal.recommendation.expectedOutcome}
                  </p>
                  <div className="flex items-center space-x-2 mt-2">
                    <span className="text-xs text-dark-400">Time Horizon:</span>
                    <span className="text-xs font-medium text-white">
                      {quickActionModal.recommendation.timeHorizon}
                    </span>
                    <span className="text-xs text-dark-400">•</span>
                    <span className="text-xs text-dark-400">Confidence:</span>
                    <span className="text-xs font-medium text-white">
                      {(quickActionModal.recommendation.confidence * 100).toFixed(0)}%
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
                      : 'bg-dark-600 hover:bg-dark-700 text-white'
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
