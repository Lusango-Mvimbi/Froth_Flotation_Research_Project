import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Brain, 
  CheckCircle, 
  AlertTriangle,
  Zap,
  Clock,
  Target,
  BarChart3
} from 'lucide-react';
import { Prediction, FlotationData, PerformanceState, TargetRanges, FuturePredictionResponse } from '../types';
import { flotationAPI } from '../services/api';
import { useFuturePredictions } from '../hooks/useFuturePredictions';

interface PredictionCardsProps {
  predictions: Prediction | null;
  currentData: FlotationData | null;
  targetRanges: TargetRanges | null;
}

const PredictionCards: React.FC<PredictionCardsProps> = ({ predictions, currentData, targetRanges }) => {
  const { futurePredictions, loading, fetchPredictions } = useFuturePredictions();
  const [activeTab, setActiveTab] = useState<'current' | '5min' | '15min' | '30min' | '60min'>('current');

  // Fetch future predictions when current data changes (with debouncing)
  useEffect(() => {
    if (currentData) {
      // Debounce the fetch to prevent excessive API calls
      const timeoutId = setTimeout(() => {
        fetchPredictions(currentData, !futurePredictions);
      }, 1000); // 1 second delay
      
      return () => clearTimeout(timeoutId);
    }
  }, [currentData]);


  // Performance state calculation
  const getPerformanceState = (value: number, metric: 'pb' | 'recovery' | 'feed_grade'): PerformanceState => {
    if (!targetRanges) {
      // No fallback - return neutral state if no target ranges available
      return { state: 'within_range' as const, color: 'text-dark-400', backgroundColor: 'bg-dark-700/20' };
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

  // Get trend direction for future predictions
  const getFutureTrendDirection = (prediction: number, current: number) => {
    if (prediction > current) return 'up';
    if (prediction < current) return 'down';
    return 'stable';
  };

  // Get confidence level color
  const getConfidenceColor = (r2Score: number) => {
    if (r2Score >= 0.8) return 'text-success-400';
    if (r2Score >= 0.6) return 'text-warning-400';
    return 'text-danger-400';
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
  const feedGradePerformance = getPerformanceState(currentData.Feed_Pb, 'feed_grade');

  // Helper function to get target range string
  const getTargetRange = (metric: 'pb' | 'recovery' | 'feed_grade') => {
    if (!targetRanges) {
      // No fallback - return empty string if no target ranges available
      return 'N/A';
    }
    
    const ranges = {
      pb: targetRanges.pb_concentrate,
      recovery: targetRanges.recovery,
      feed_grade: targetRanges.feed_grade
    };
    
    const range = ranges[metric];
    return `${range.min}-${range.max}${range.unit}`;
  };

  // Tab configuration
  const tabs = [
    { id: 'current', label: 'Current', icon: Activity },
    { id: '5min', label: '5 Min', icon: Clock },
    { id: '15min', label: '15 Min', icon: Clock },
    { id: '30min', label: '30 Min', icon: Clock },
    { id: '60min', label: '60 Min', icon: Target },
  ];

  // Get cards based on active tab
  const getCards = () => {
    console.log('PredictionCards: Getting cards for active tab:', activeTab);
    console.log('PredictionCards: Current data:', currentData);
    console.log('PredictionCards: Predictions:', predictions);
    console.log('PredictionCards: Future predictions:', futurePredictions);
    console.log('PredictionCards: Target ranges:', targetRanges);
    
    if (activeTab === 'current') {
      console.log('PredictionCards: Generating CURRENT tab cards');
      return [
        {
          title: 'Predicted Pb',
          value: `${predictions.predicted_pb.toFixed(2)}%`,
          trend: getTrendDirection(predictions.predicted_pb, targetRanges?.pb_concentrate?.optimal || 10),
          performance: pbPerformance,
          icon: Activity,
          method: 'ML Model',
          target: getTargetRange('pb'),
          confidence: null,
        },
        {
          title: 'Actual Pb',
          value: `${(currentData.Actual_Pb_Concentrate || 0).toFixed(2)}%`,
          trend: getTrendDirection(currentData.Actual_Pb_Concentrate || 0, targetRanges?.pb_concentrate?.optimal || 10),
          performance: getPerformanceState(currentData.Actual_Pb_Concentrate || 0, 'pb'),
          icon: Activity,
          target: getTargetRange('pb'),
          confidence: null,
        },
        {
          title: 'Predicted Recovery',
          value: `${predictions.recovery_efficiency.toFixed(1)}%`,
          trend: getTrendDirection(predictions.recovery_efficiency, targetRanges?.recovery?.optimal || 85),
          performance: recoveryPerformance,
          icon: TrendingUp,
          method: 'ML Model',
          target: getTargetRange('recovery'),
          confidence: null,
        },
        {
          title: 'Actual Recovery',
          value: `${((currentData.Actual_Pb_Recovery || 0) * 100).toFixed(1)}%`,
          trend: getTrendDirection((currentData.Actual_Pb_Recovery || 0) * 100, targetRanges?.recovery?.optimal || 85),
          performance: getPerformanceState((currentData.Actual_Pb_Recovery || 0) * 100, 'recovery'),
          icon: TrendingUp,
          target: getTargetRange('recovery'),
          confidence: null,
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
          confidence: null,
        },
        {
          title: 'Feed Grade',
          value: `${currentData.Feed_Pb.toFixed(2)}%`,
          trend: 'stable',
          performance: feedGradePerformance,
          icon: TrendingDown,
          target: getTargetRange('feed_grade'),
          confidence: null,
        }
      ];
    } else {
      // Future prediction cards
      console.log('PredictionCards: Generating FUTURE tab cards for horizon:', activeTab);
      const horizonKey = activeTab;
      const futurePred = futurePredictions?.future_predictions[horizonKey];
      
      console.log('PredictionCards: Future prediction for horizon', horizonKey, ':', futurePred);
      
      if (!futurePred) {
        console.log('PredictionCards: No future prediction found for horizon:', horizonKey);
        return [];
      }

      const currentPb = currentData.Actual_Pb_Concentrate || predictions.predicted_pb;
      const futureTrend = getFutureTrendDirection(futurePred.prediction, currentPb);
      const futurePerformance = getPerformanceState(futurePred.prediction, 'pb');

      console.log('PredictionCards: Current Pb:', currentPb, 'Future Pb:', futurePred.prediction, 'Trend:', futureTrend);

      return [
        {
          title: `Future Pb (${activeTab})`,
          value: `${futurePred.prediction.toFixed(2)}%`,
          trend: futureTrend,
          performance: futurePerformance,
          icon: Brain,
          method: 'Random Forest',
          target: getTargetRange('pb'),
          confidence: null,
        },
        {
          title: 'Confidence Interval',
          value: `${futurePred.confidence_interval.lower.toFixed(2)} - ${futurePred.confidence_interval.upper.toFixed(2)}%`,
          trend: 'stable',
          performance: { state: 'within_range', color: 'text-cyan-400', backgroundColor: 'bg-cyan-900/20' },
          icon: BarChart3,
          target: '95% Confidence',
          confidence: null,
        },
        {
          title: 'Model Performance',
          value: futurePred.model_performance.r2_score > 0 ? `${(futurePred.model_performance.r2_score * 100).toFixed(1)}%` : 'Loading...',
          trend: futurePred.model_performance.r2_score > 0.8 ? 'up' : 'stable',
          performance: { 
            state: futurePred.model_performance.r2_score > 0.8 ? 'within_range' : 'warning',
            color: getConfidenceColor(futurePred.model_performance.r2_score),
            backgroundColor: futurePred.model_performance.r2_score > 0.8 ? 'bg-success-900/20' : 'bg-warning-900/20'
          },
          icon: Zap,
          target: 'R² Score',
          confidence: null,
        },
        {
          title: 'Prediction Accuracy',
          value: futurePred.model_performance.accuracy_10_percent > 0 ? `${(futurePred.model_performance.accuracy_10_percent * 100).toFixed(1)}%` : 'Loading...',
          trend: futurePred.model_performance.accuracy_10_percent > 0.7 ? 'up' : 'stable',
          performance: { 
            state: futurePred.model_performance.accuracy_10_percent > 0.7 ? 'within_range' : 'warning',
            color: futurePred.model_performance.accuracy_10_percent > 0.7 ? 'text-success-400' : 'text-warning-400',
            backgroundColor: futurePred.model_performance.accuracy_10_percent > 0.7 ? 'bg-success-900/20' : 'bg-warning-900/20'
          },
          icon: Target,
          target: 'Within 10%',
          confidence: null,
        },
        {
          title: 'Current vs Future',
          value: `${currentPb.toFixed(2)} → ${futurePred.prediction.toFixed(2)}%`,
          trend: futureTrend,
          performance: futurePerformance,
          icon: TrendingUp,
          target: 'Change',
          confidence: null,
        },
        {
          title: 'Model Used',
          value: futurePred.model,
          trend: 'stable',
          performance: { state: 'within_range', color: 'text-primary-400', backgroundColor: 'bg-primary-900/20' },
          icon: Brain,
          target: 'Random Forest',
          confidence: null,
        }
      ];
    }
  };

  const cards = getCards();

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-dark-800/50 backdrop-blur-sm border border-dark-600 rounded-lg p-1">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-primary-600 text-white shadow-lg'
                  : 'text-dark-300 hover:text-white hover:bg-dark-700/50'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
              {loading && activeTab === tab.id && (
                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
              )}
            </button>
          );
        })}
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 sm:gap-6">
        {cards.map((card, index) => (
          <motion.div
            key={`${activeTab}-${card.title}`}
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
                <span className="text-xs text-dark-200 font-medium">
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

      {/* Loading State for Future Predictions */}
      {loading && activeTab !== 'current' && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-400 mx-auto mb-4"></div>
          <p className="text-dark-300">Loading future predictions...</p>
        </div>
      )}

      {/* Error State for Future Predictions */}
      {!loading && activeTab !== 'current' && !futurePredictions && (
        <div className="text-center py-8">
          <AlertTriangle className="h-8 w-8 text-warning-400 mx-auto mb-4" />
          <p className="text-dark-300">Unable to load future predictions</p>
        </div>
      )}
    </div>
  );
};

export default PredictionCards;
