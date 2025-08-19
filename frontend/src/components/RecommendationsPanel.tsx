import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  AlertTriangle, 
  CheckCircle, 
  Info, 
  ChevronDown, 
  ChevronUp,
  Bell,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import { Recommendation, Prediction, FlotationData } from '../types';

interface RecommendationsPanelProps {
  recommendations: Recommendation[];
  predictions: Prediction | null;
  currentData: FlotationData | null;
}

const RecommendationsPanel: React.FC<RecommendationsPanelProps> = ({
  recommendations,
  predictions,
  currentData
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Use ML-generated recommendations if available, otherwise generate based on data
  const generatedRecommendations = useMemo(() => {
    const recs: Recommendation[] = [];

    // If we have ML-generated recommendations from the backend, use those
    if (currentData && currentData.Recommendations && Array.isArray(currentData.Recommendations)) {
      currentData.Recommendations.forEach((rec, index) => {
        recs.push({
          id: `ml-rec-${index}`,
          type: rec.includes('⚠️') ? 'danger' : rec.includes('💡') ? 'warning' : 'success',
          message: rec,
          parameter: 'ML Generated',
          current_value: 0,
          optimal_range: 'Dynamic',
          timestamp: new Date().toISOString()
        });
      });
      return recs;
    }

    // Fallback to generated recommendations if no ML recommendations
    if (!predictions || !currentData) return recs;

    // Check Pb Concentrate performance
    if (currentData.Pb_Concentrate < 15) {
      recs.push({
        id: 'pb-low',
        type: 'danger',
        message: 'Pb Concentrate is below optimal range. Consider increasing KEX flow rate or adjusting pH levels.',
        parameter: 'Pb Concentrate',
        current_value: currentData.Pb_Concentrate,
        optimal_range: '15-25%',
        timestamp: new Date().toISOString()
      });
    } else if (currentData.Pb_Concentrate >= 25) {
      recs.push({
        id: 'pb-high',
        type: 'warning',
        message: 'Pb Concentrate is above optimal range. Consider reducing KEX flow rate or adjusting feed grade.',
        parameter: 'Pb Concentrate',
        current_value: currentData.Pb_Concentrate,
        optimal_range: '15-25%',
        timestamp: new Date().toISOString()
      });
    }

    // Check Recovery Rate performance
    const recoveryPct = currentData.Pb_Recovery * 100;
    if (recoveryPct < 75) {
      recs.push({
        id: 'recovery-low',
        type: 'danger',
        message: 'Recovery efficiency is below target. Optimize air flow rate and impeller speed.',
        parameter: 'Recovery Rate',
        current_value: recoveryPct,
        optimal_range: '75-95%',
        timestamp: new Date().toISOString()
      });
    } else if (recoveryPct >= 95) {
      recs.push({
        id: 'recovery-high',
        type: 'warning',
        message: 'Recovery efficiency is above optimal range. Consider reducing air flow to prevent over-frothing.',
        parameter: 'Recovery Rate',
        current_value: recoveryPct,
        optimal_range: '75-95%',
        timestamp: new Date().toISOString()
      });
    }

    // Check process parameters
    if (currentData.pH < 9.5 || currentData.pH > 11.5) {
      recs.push({
        id: 'ph-range',
        type: 'warning',
        message: 'pH level is outside optimal range (9.5-11.5). Adjust pH control system.',
        parameter: 'pH Level',
        current_value: currentData.pH,
        optimal_range: '9.5-11.5',
        timestamp: new Date().toISOString()
      });
    }

    if (currentData.Pb_Rougher1_AirFlow < 120 || currentData.Pb_Rougher1_AirFlow > 180) {
      recs.push({
        id: 'air-flow',
        type: 'warning',
        message: 'Air flow rate is outside optimal range (120-180 L/min). Adjust air injection.',
        parameter: 'Air Flow',
        current_value: currentData.Pb_Rougher1_AirFlow,
        optimal_range: '120-180 L/min',
        timestamp: new Date().toISOString()
      });
    }

    // Add success message if everything is optimal
    if (recs.length === 0) {
      recs.push({
        id: 'optimal',
        type: 'success',
        message: 'All process parameters are within optimal ranges. Process is running efficiently.',
        timestamp: new Date().toISOString()
      });
    }

    return recs;
  }, [predictions, currentData]);

  // Combine API recommendations with generated ones
  const allRecommendations = [...recommendations, ...generatedRecommendations];

  const getIcon = (type: string) => {
    switch (type) {
      case 'danger':
        return <AlertTriangle className="h-5 w-5 text-danger-400" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-warning-400" />;
      case 'success':
        return <CheckCircle className="h-5 w-5 text-success-400" />;
      default:
        return <Info className="h-5 w-5 text-primary-400" />;
    }
  };

  const getAlertStyle = (type: string) => {
    switch (type) {
      case 'danger':
        return 'bg-danger-900/20 border-danger-700 text-danger-300';
      case 'warning':
        return 'bg-warning-900/20 border-warning-700 text-warning-300';
      case 'success':
        return 'bg-success-900/20 border-success-700 text-success-300';
      default:
        return 'bg-primary-900/20 border-primary-700 text-primary-300';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-xl p-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary-600 rounded-lg">
            <Bell className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Recommendations</h2>
            <p className="text-sm text-dark-300">Process optimization alerts</p>
          </div>
        </div>
        
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center space-x-2 px-3 py-2 bg-dark-700 hover:bg-dark-600 rounded-lg transition-colors duration-200"
        >
          <span className="text-sm text-white">
            {allRecommendations.length} {allRecommendations.length === 1 ? 'Alert' : 'Alerts'}
          </span>
          {isExpanded ? (
            <ChevronUp className="h-4 w-4 text-dark-300" />
          ) : (
            <ChevronDown className="h-4 w-4 text-dark-300" />
          )}
        </button>
      </div>

      {/* Recommendations List */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-3"
          >
            {allRecommendations.length === 0 ? (
              <div className="text-center py-8">
                <CheckCircle className="h-12 w-12 text-success-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">No Alerts</h3>
                <p className="text-dark-300">All systems are operating normally</p>
              </div>
            ) : (
              allRecommendations.map((rec, index) => (
                <motion.div
                  key={rec.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`p-4 rounded-lg border ${getAlertStyle(rec.type)}`}
                >
                  <div className="flex items-start space-x-3">
                    {getIcon(rec.type)}
                    <div className="flex-1">
                      <p className="text-sm font-medium mb-1">{rec.message}</p>
                      {rec.parameter && rec.current_value && rec.optimal_range && (
                        <div className="flex items-center space-x-4 text-xs mt-2">
                          <span className="text-dark-400">
                            {rec.parameter}: {rec.current_value.toFixed(2)}
                          </span>
                          <span className="text-dark-400">
                            Target: {rec.optimal_range}
                          </span>
                        </div>
                      )}
                      <div className="flex items-center space-x-2 mt-2">
                        <span className="text-xs text-dark-400">
                          {new Date(rec.timestamp).toLocaleTimeString()}
                        </span>
                        {rec.type === 'danger' && (
                          <span className="px-2 py-1 bg-danger-600 text-white text-xs rounded-full">
                            Critical
                          </span>
                        )}
                        {rec.type === 'warning' && (
                          <span className="px-2 py-1 bg-warning-600 text-white text-xs rounded-full">
                            Warning
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Summary when collapsed */}
      {!isExpanded && allRecommendations.length > 0 && (
        <div className="space-y-2">
          {allRecommendations.slice(0, 2).map((rec) => (
            <div key={rec.id} className="flex items-center space-x-2 text-sm">
              {getIcon(rec.type)}
              <span className="text-dark-300 truncate">{rec.message}</span>
            </div>
          ))}
          {allRecommendations.length > 2 && (
            <div className="text-xs text-dark-400">
              +{allRecommendations.length - 2} more alerts
            </div>
          )}
        </div>
      )}

      {/* Performance Summary */}
      {predictions && (
        <div className="mt-6 p-4 bg-dark-700/50 rounded-lg border border-dark-600">
          <div className="flex items-center space-x-2 mb-3">
            <TrendingUp className="h-4 w-4 text-primary-400" />
            <h4 className="text-sm font-semibold text-white">Performance Summary</h4>
          </div>
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <span className="text-dark-400">Pb Concentrate:</span>
              <span className={`ml-2 font-medium ${
                predictions.predicted_pb >= 15 && predictions.predicted_pb < 25 
                  ? 'text-success-400' 
                  : 'text-danger-400'
              }`}>
                {predictions.predicted_pb.toFixed(2)}%
              </span>
            </div>
            <div>
              <span className="text-dark-400">Recovery Rate:</span>
              <span className={`ml-2 font-medium ${
                predictions.recovery_efficiency >= 75 && predictions.recovery_efficiency < 95 
                  ? 'text-success-400' 
                  : 'text-danger-400'
              }`}>
                {predictions.recovery_efficiency.toFixed(1)}%
              </span>
            </div>
            <div>
              <span className="text-dark-400">Model Confidence:</span>
              <span className="ml-2 font-medium text-primary-400">
                {predictions.confidence.toFixed(1)}%
              </span>
            </div>
            <div>
              <span className="text-dark-400">Status:</span>
              <span className={`ml-2 font-medium ${
                predictions.status === 'Good' ? 'text-success-400' : 'text-danger-400'
              }`}>
                {predictions.status}
              </span>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default RecommendationsPanel;
