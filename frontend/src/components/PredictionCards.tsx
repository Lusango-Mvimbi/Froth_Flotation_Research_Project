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
import { Prediction, FlotationData, PerformanceState, TargetRanges } from '../types';

interface PredictionCardsProps {
  predictions: Prediction | null;
  currentData: FlotationData | null;
  targetRanges: TargetRanges | null;
}

const PredictionCards: React.FC<PredictionCardsProps> = ({ predictions, currentData, targetRanges }) => {
  // Performance state calculation
  const getPerformanceState = (value: number, metric: 'pb' | 'recovery' | 'feed_grade'): PerformanceState => {
    if (!targetRanges) {
      // Fallback to hardcoded values if target ranges not available
      if (metric === 'pb') {
        if (value < 15) return { state: 'below_min', color: 'text-danger-400', backgroundColor: 'bg-danger-900/20' };
        if (value >= 25) return { state: 'above_max', color: 'text-warning-400', backgroundColor: 'bg-warning-900/20' };
        return { state: 'within_range', color: 'text-success-400', backgroundColor: 'bg-success-900/20' };
      } else if (metric === 'recovery') {
        if (value < 75) return { state: 'below_min', color: 'text-danger-400', backgroundColor: 'bg-danger-900/20' };
        if (value >= 95) return { state: 'above_max', color: 'text-warning-400', backgroundColor: 'bg-warning-900/20' };
        return { state: 'within_range', color: 'text-success-400', backgroundColor: 'bg-success-900/20' };
      } else { // feed_grade
        if (value < 2.0) return { state: 'below_min', color: 'text-danger-400', backgroundColor: 'bg-danger-900/20' };
        if (value >= 4.0) return { state: 'above_max', color: 'text-warning-400', backgroundColor: 'bg-warning-900/20' };
        return { state: 'within_range', color: 'text-success-400', backgroundColor: 'bg-success-900/20' };
      }
    }

    // Use dynamic target ranges from backend
    if (metric === 'pb') {
      const { min, max } = targetRanges.pb_concentrate;
      if (value < min) return { state: 'below_min', color: 'text-danger-400', backgroundColor: 'bg-danger-900/20' };
      if (value >= max) return { state: 'above_max', color: 'text-warning-400', backgroundColor: 'bg-warning-900/20' };
      return { state: 'within_range', color: 'text-success-400', backgroundColor: 'bg-success-900/20' };
    } else if (metric === 'recovery') {
      const { min, max } = targetRanges.recovery;
      if (value < min) return { state: 'below_min', color: 'text-danger-400', backgroundColor: 'bg-danger-900/20' };
      if (value >= max) return { state: 'above_max', color: 'text-warning-400', backgroundColor: 'bg-warning-900/20' };
      return { state: 'within_range', color: 'text-success-400', backgroundColor: 'bg-success-900/20' };
    } else { // feed_grade
      const { min, max } = targetRanges.feed_grade;
      if (value < min) return { state: 'below_min', color: 'text-danger-400', backgroundColor: 'bg-danger-900/20' };
      if (value >= max) return { state: 'above_max', color: 'text-warning-400', backgroundColor: 'bg-warning-900/20' };
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
  const feedGradePerformance = getPerformanceState(currentData.Feed_Pb || 0, 'feed_grade');

  // Helper function to get target range string
  const getTargetRange = (metric: 'pb' | 'recovery' | 'feed_grade') => {
    if (!targetRanges) {
      // Fallback to hardcoded values
      switch (metric) {
        case 'pb': return '15-25%';
        case 'recovery': return '75-95%';
        case 'feed_grade': return '2.0-4.0%';
        default: return '';
      }
    }
    
    const ranges = {
      pb: targetRanges.pb_concentrate,
      recovery: targetRanges.recovery,
      feed_grade: targetRanges.feed_grade
    };
    
    const range = ranges[metric];
    return `${range.min}-${range.max}${range.unit}`;
  };

  const cards = [
    {
      title: 'Predicted Pb',
      value: `${predictions.predicted_pb.toFixed(2)}%`,
      trend: getTrendDirection(predictions.predicted_pb, targetRanges?.pb_concentrate?.optimal || 20),
      performance: pbPerformance,
      icon: Activity,
      method: 'ML Model',
      target: getTargetRange('pb'),
    },
    {
      title: 'Actual Pb',
      value: `${currentData.Actual_Pb_Concentrate?.toFixed(2) || 'N/A'}%`,
      trend: currentData.Actual_Pb_Concentrate ? getTrendDirection(currentData.Actual_Pb_Concentrate, targetRanges?.pb_concentrate?.optimal || 20) : 'stable',
      performance: currentData.Actual_Pb_Concentrate ? getPerformanceState(currentData.Actual_Pb_Concentrate, 'pb') : { state: 'unknown', color: 'text-dark-400', backgroundColor: 'bg-dark-700/20' },
      icon: Activity,
      target: getTargetRange('pb'),
    },
    {
      title: 'Predicted Recovery',
      value: `${predictions.recovery_efficiency.toFixed(1)}%`,
      trend: getTrendDirection(predictions.recovery_efficiency, targetRanges?.recovery?.optimal || 85),
      performance: recoveryPerformance,
      icon: TrendingUp,
      method: 'ML Model',
      target: getTargetRange('recovery'),
    },
    {
      title: 'Actual Recovery',
      value: `${currentData.Actual_Pb_Recovery ? (currentData.Actual_Pb_Recovery * 100).toFixed(1) : 'N/A'}%`,
      trend: currentData.Actual_Pb_Recovery ? getTrendDirection(currentData.Actual_Pb_Recovery * 100, targetRanges?.recovery?.optimal || 85) : 'stable',
      performance: currentData.Actual_Pb_Recovery ? getPerformanceState(currentData.Actual_Pb_Recovery * 100, 'recovery') : { state: 'unknown', color: 'text-dark-400', backgroundColor: 'bg-dark-700/20' },
      icon: TrendingUp,
      target: getTargetRange('recovery'),
    },
    {
      title: 'Process Status',
      value: predictions.status,
      trend: predictions.status === 'optimal' ? 'up' : predictions.status === 'warning' ? 'stable' : 'down',
      performance: { 
        state: predictions.status === 'optimal' ? 'within_range' : predictions.status === 'warning' ? 'warning' : 'critical',
        color: predictions.status === 'optimal' ? 'text-success-400' : predictions.status === 'warning' ? 'text-warning-400' : 'text-danger-400',
        backgroundColor: predictions.status === 'optimal' ? 'bg-success-900/20' : predictions.status === 'warning' ? 'bg-warning-900/20' : 'bg-danger-900/20'
      },
      icon: CheckCircle,
      target: 'Optimal',
    },
    {
      title: 'Feed Grade',
      value: `${currentData.Feed_Pb?.toFixed(2) || 'N/A'}%`,
      trend: 'stable',
      performance: feedGradePerformance,
      icon: TrendingDown,
      target: getTargetRange('feed_grade'),
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 sm:gap-6">
      {cards.map((card, index) => (
        <motion.div
          key={card.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          whileHover={{ scale: 1.02, y: -2 }}
          className={`relative overflow-hidden bg-dark-800/50 backdrop-blur-sm border border-dark-600 rounded-xl p-6 sm:p-8 transition-all duration-300 ${card.performance.backgroundColor}`}
        >
          {/* Performance indicator bar */}
          <div className={`absolute top-0 left-0 right-0 h-1 ${card.performance.color.replace('text-', 'bg-')}`} />
          
                              {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center space-x-2 flex-1 min-w-0">
              <card.icon className={`h-4 w-4 ${card.method ? 'text-primary-400' : card.performance.color} flex-shrink-0`} />
              <h3 className="text-xs font-medium text-dark-300 uppercase tracking-wide leading-tight">
                {card.title}
              </h3>
            </div>
 
          </div>

          {/* Value */}
          <div className="mb-3">
            <div className={`text-2xl font-bold ${card.performance.color} mb-1`}>
              {card.value}
            </div>
            <div className="flex items-center space-x-2">
              {card.trend === 'up' ? (
                <TrendingUp className="h-3 w-3 text-success-400" />
              ) : card.trend === 'down' ? (
                <TrendingDown className="h-3 w-3 text-danger-400" />
              ) : (
                <div className="h-3 w-3 text-dark-400">—</div>
              )}
              <span className="text-xs text-dark-400 font-medium">
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
