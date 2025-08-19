import React from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Brain, 
  CheckCircle, 
  AlertTriangle,
  Zap
} from 'lucide-react';
import { Prediction, FlotationData, PerformanceState } from '../types';

interface PredictionCardsProps {
  predictions: Prediction | null;
  currentData: FlotationData | null;
}

const PredictionCards: React.FC<PredictionCardsProps> = ({ predictions, currentData }) => {
  // Performance state calculation
  const getPerformanceState = (value: number, metric: 'pb' | 'recovery'): PerformanceState => {
    if (metric === 'pb') {
      if (value < 15) return { state: 'below_min', color: 'text-danger-400', backgroundColor: 'bg-danger-900/20' };
      if (value >= 25) return { state: 'above_max', color: 'text-warning-400', backgroundColor: 'bg-warning-900/20' };
      return { state: 'within_range', color: 'text-success-400', backgroundColor: 'bg-success-900/20' };
    } else {
      if (value < 75) return { state: 'below_min', color: 'text-danger-400', backgroundColor: 'bg-danger-900/20' };
      if (value >= 95) return { state: 'above_max', color: 'text-warning-400', backgroundColor: 'bg-warning-900/20' };
      return { state: 'within_range', color: 'text-success-400', backgroundColor: 'bg-success-900/20' };
    }
  };

  // Get trend direction
  const getTrendDirection = (current: number, target: number) => {
    if (current > target) return 'up';
    if (current < target) return 'down';
    return 'stable';
  };

  if (!predictions || !currentData) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.1 }}
            className="bg-dark-800/50 backdrop-blur-sm border border-dark-600 rounded-xl p-6 animate-pulse"
          >
            <div className="h-8 bg-dark-700 rounded mb-4"></div>
            <div className="h-4 bg-dark-700 rounded mb-2"></div>
            <div className="h-4 bg-dark-700 rounded w-2/3"></div>
          </motion.div>
        ))}
      </div>
    );
  }

  const pbPerformance = getPerformanceState(predictions.predicted_pb, 'pb');
  const recoveryPerformance = getPerformanceState(predictions.recovery_efficiency, 'recovery');

  const cards = [
    {
      title: 'Predicted Pb Concentrate',
      value: `${predictions.predicted_pb.toFixed(2)}%`,
      trend: getTrendDirection(predictions.predicted_pb, 20),
      performance: pbPerformance,
      icon: Activity,
      method: predictions.prediction_method,
      target: '15-25%',
    },
    {
      title: 'Recovery Efficiency',
      value: `${predictions.recovery_efficiency.toFixed(1)}%`,
      trend: getTrendDirection(predictions.recovery_efficiency, 85),
      performance: recoveryPerformance,
      icon: TrendingUp,
      target: '75-95%',
    },
    {
      title: 'Model Confidence',
      value: `${predictions.confidence.toFixed(2)}%`,
      trend: 'up',
      performance: { state: 'within_range', color: 'text-primary-400', backgroundColor: 'bg-primary-900/20' },
      icon: Brain,
      target: 'High',
    },
    {
      title: 'Process Status',
      value: predictions.status,
      trend: predictions.status === 'Good' ? 'up' : 'down',
      performance: { 
        state: predictions.status === 'Good' ? 'within_range' : 'below_min',
        color: predictions.status === 'Good' ? 'text-success-400' : 'text-danger-400',
        backgroundColor: predictions.status === 'Good' ? 'bg-success-900/20' : 'bg-danger-900/20'
      },
      icon: CheckCircle,
      target: 'Good',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      {cards.map((card, index) => (
        <motion.div
          key={card.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          whileHover={{ scale: 1.02, y: -2 }}
          className={`relative overflow-hidden bg-dark-800/50 backdrop-blur-sm border border-dark-600 rounded-xl p-4 sm:p-6 transition-all duration-300 ${card.performance.backgroundColor}`}
        >
          {/* Performance indicator bar */}
          <div className={`absolute top-0 left-0 right-0 h-1 ${card.performance.color.replace('text-', 'bg-')}`} />
          
          {/* Header */}
          <div className="flex items-center justify-between mb-3 sm:mb-4">
            <div className="flex items-center space-x-2 min-w-0">
              <card.icon className={`h-4 w-4 sm:h-5 sm:w-5 ${card.performance.color} flex-shrink-0`} />
              <h3 className="text-xs sm:text-sm font-medium text-dark-300 uppercase tracking-wide truncate">
                {card.title}
              </h3>
            </div>
            {card.method && (
              <div className="flex items-center space-x-1 flex-shrink-0">
                <Zap className="h-3 w-3 text-primary-400" />
                <span className="text-xs text-primary-400 font-medium hidden sm:inline">
                  {card.method}
                </span>
              </div>
            )}
          </div>

          {/* Value */}
          <div className="mb-2">
            <div className={`text-2xl sm:text-3xl font-bold ${card.performance.color} mb-1`}>
              {card.value}
            </div>
            <div className="flex items-center space-x-2">
              {card.trend === 'up' ? (
                <TrendingUp className="h-3 w-3 sm:h-4 sm:w-4 text-success-400" />
              ) : card.trend === 'down' ? (
                <TrendingDown className="h-3 w-3 sm:h-4 sm:w-4 text-danger-400" />
              ) : (
                <div className="h-3 w-3 sm:h-4 sm:w-4 text-dark-400">—</div>
              )}
              <span className="text-xs text-dark-400">
                Target: {card.target}
              </span>
            </div>
          </div>

          {/* Performance indicator */}
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${card.performance.color.replace('text-', 'bg-')}`} />
            <span className={`text-xs font-medium capitalize ${card.performance.color}`}>
              {card.performance.state.replace('_', ' ')}
            </span>
          </div>

          {/* Hover effect overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            whileHover={{ opacity: 1 }}
            className="absolute inset-0 bg-gradient-to-br from-transparent to-dark-900/20 pointer-events-none"
          />
        </motion.div>
      ))}
    </div>
  );
};

export default PredictionCards;
