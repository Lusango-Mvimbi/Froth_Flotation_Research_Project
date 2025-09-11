import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  Area,
  ComposedChart
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  Clock, 
  Target, 
  Play,
  Pause
} from 'lucide-react';
import { FlotationData, FuturePredictionResponse } from '../types';
import { ChartSkeleton } from './LoadingSkeleton';

interface FuturePredictionChartProps {
  currentData: FlotationData | null;
  historicalData: FlotationData[];
  futurePredictions: FuturePredictionResponse | null;
  loading: boolean;
}

interface ChartDataPoint {
  timestamp: string;
  current: number | null;
  predicted_5min?: number;
  predicted_15min?: number;
  predicted_30min?: number;
  predicted_60min?: number;
  confidence_lower_5min?: number;
  confidence_upper_5min?: number;
  confidence_lower_15min?: number;
  confidence_upper_15min?: number;
  confidence_lower_30min?: number;
  confidence_upper_30min?: number;
  confidence_lower_60min?: number;
  confidence_upper_60min?: number;
  [key: string]: any; // Allow dynamic property access
}

const FuturePredictionChart: React.FC<FuturePredictionChartProps> = ({ 
  currentData, 
  historicalData,
  futurePredictions,
  loading
}) => {
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedHorizons, setSelectedHorizons] = useState<Set<string>>(new Set(['5min', '15min', '30min', '60min']));
  const [showConfidenceIntervals, setShowConfidenceIntervals] = useState(true);
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h'>('1h');

  const getDataLimit = useCallback(() => {
    switch (timeRange) {
      case '1h': return 60; // 60 data points for 1 hour
      case '6h': return 360; // 360 data points for 6 hours
      case '24h': return 1440; // 1440 data points for 24 hours
      default: return 60;
    }
  }, [timeRange]);

  const updateChartData = useCallback(() => {
    if (!currentData) return;

    // Get current value with proper scaling
    let currentValue = 0;
    
    if (currentData.Actual_Pb_Concentrate !== undefined && currentData.Actual_Pb_Concentrate !== null) {
      currentValue = currentData.Actual_Pb_Concentrate;
    } else if (currentData.Predicted_Pb_Concentrate !== undefined && currentData.Predicted_Pb_Concentrate !== null) {
      currentValue = currentData.Predicted_Pb_Concentrate;
    } else if (currentData.Pb_Concentrate !== undefined && currentData.Pb_Concentrate !== null) {
      currentValue = currentData.Pb_Concentrate;
    }
    
    // Ensure the value is in the correct range (should be 0-50% for Pb concentrate)
    // If the value is very small (like 0.02), it might be in decimal form and needs to be converted to percentage
    if (currentValue > 0 && currentValue < 1) {
      currentValue = currentValue * 100; // Convert decimal to percentage
    }
    
    // Clamp to reasonable range
    currentValue = Math.max(0, Math.min(50, currentValue));
    
    // Use only the actual timestamp from the current data - no fallback
    if (!currentData.timestamp) {
      console.error('No timestamp in current data - cannot create chart data point');
      return;
    }
    const dataTimestamp = new Date(currentData.timestamp);
    
    // Create base data point for current time
    const basePoint: ChartDataPoint = {
      timestamp: dataTimestamp.toISOString(),
      current: currentValue,
    };

    // Add future predictions to the current point
    if (futurePredictions) {
      const horizons = ['5min', '15min', '30min', '60min'] as const;
      
      for (const horizon of horizons) {
        const prediction = futurePredictions.future_predictions[horizon];
        if (prediction && selectedHorizons.has(horizon)) {
          (basePoint as any)[`predicted_${horizon}`] = prediction.prediction;
          (basePoint as any)[`confidence_lower_${horizon}`] = prediction.confidence_interval.lower;
          (basePoint as any)[`confidence_upper_${horizon}`] = prediction.confidence_interval.upper;
        }
      }
    }

    // Create future data points for each prediction horizon
    const futurePoints: ChartDataPoint[] = [];
    if (futurePredictions) {
      const horizons = ['5min', '15min', '30min', '60min'] as const;
      
      for (const horizon of horizons) {
        const prediction = futurePredictions.future_predictions[horizon];
        if (prediction && selectedHorizons.has(horizon)) {
          // Create a future timestamp based on the horizon with slight offset to avoid duplicates
          const horizonMinutes = parseInt(horizon);
          const offsetSeconds = horizons.indexOf(horizon) * 10; // 10 second offset per horizon
          const futureTime = new Date(dataTimestamp.getTime() + (horizonMinutes * 60 * 1000) + (offsetSeconds * 1000));
          
          const futurePoint: ChartDataPoint = {
            timestamp: futureTime.toISOString(),
            current: null, // No current value for future points
          };
          
          // Add the prediction for this horizon
          (futurePoint as any)[`predicted_${horizon}`] = prediction.prediction;
          (futurePoint as any)[`confidence_lower_${horizon}`] = prediction.confidence_interval.lower;
          (futurePoint as any)[`confidence_upper_${horizon}`] = prediction.confidence_interval.upper;
          
          futurePoints.push(futurePoint);
        }
      }
    }

    // Create historical data points with proper scaling
    const historicalPoints: ChartDataPoint[] = historicalData
      .slice(-getDataLimit())
      .map(data => {
        // Get the Pb concentrate value, ensuring it's in the correct scale
        let pbValue = 0;
        
        // Try different possible field names and ensure proper scaling
        if (data.Actual_Pb_Concentrate !== undefined && data.Actual_Pb_Concentrate !== null) {
          pbValue = data.Actual_Pb_Concentrate;
        } else if (data.Predicted_Pb_Concentrate !== undefined && data.Predicted_Pb_Concentrate !== null) {
          pbValue = data.Predicted_Pb_Concentrate;
        } else if (data.Pb_Concentrate !== undefined && data.Pb_Concentrate !== null) {
          pbValue = data.Pb_Concentrate;
        }
        
        // Ensure the value is in the correct range (should be 0-50% for Pb concentrate)
        // If the value is very small (like 0.02), it might be in decimal form and needs to be converted to percentage
        if (pbValue > 0 && pbValue < 1) {
          pbValue = pbValue * 100; // Convert decimal to percentage
        }
        
        // Clamp to reasonable range
        pbValue = Math.max(0, Math.min(50, pbValue));
        
        return {
          timestamp: data.timestamp,
          current: pbValue,
        };
      });

    // Combine historical, current, and future data
    const allData = [...historicalPoints, basePoint, ...futurePoints];
    
    
    setChartData(allData);
  }, [currentData, futurePredictions, historicalData, selectedHorizons, getDataLimit]);

  // No longer fetching predictions here - they come from Dashboard as props

  // Update chart data when predictions or historical data changes
  useEffect(() => {
    updateChartData();
  }, [futurePredictions, historicalData, currentData, updateChartData]);

  const toggleHorizon = (horizon: string) => {
    const newSelected = new Set(selectedHorizons);
    if (newSelected.has(horizon)) {
      newSelected.delete(horizon);
    } else {
      newSelected.add(horizon);
    }
    setSelectedHorizons(newSelected);
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit',
      hour12: false 
    });
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0]?.payload;
      
      return (
        <div className="bg-slate-800 border border-slate-600 rounded-lg p-3 shadow-sm">
          <p className="text-slate-300 text-sm mb-2">
            {formatTimestamp(label)}
          </p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center space-x-2 mb-1">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-sm font-medium text-white">
                {entry.name}: {entry.value?.toFixed(2)}%
              </span>
            </div>
          ))}
          
          {/* Show confidence intervals if available */}
          {showConfidenceIntervals && data && (
            <div className="mt-2 pt-2 border-t border-slate-600">
              <p className="text-xs text-slate-400 mb-1">Confidence Intervals:</p>
              {['5min', '15min', '30min', '60min'].map(horizon => {
                const lower = data[`confidence_lower_${horizon}`];
                const upper = data[`confidence_upper_${horizon}`];
                if (lower !== undefined && upper !== undefined) {
                  return (
                    <div key={horizon} className="text-xs text-slate-400">
                      {horizon}: {lower?.toFixed(2)}% - {upper?.toFixed(2)}%
                    </div>
                  );
                }
                return null;
              })}
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  const getTrendIcon = (current: number, predicted: number) => {
    if (predicted > current) {
      return <TrendingUp className="h-4 w-4 text-success-400" />;
    } else if (predicted < current) {
      return <TrendingDown className="h-4 w-4 text-danger-400" />;
    }
    return <div className="h-4 w-4 text-slate-400">—</div>;
  };

  return (
    <div className="bg-slate-800 border border-slate-600 rounded-xl p-4 sm:p-6 shadow-sm">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 sm:mb-6 space-y-3 sm:space-y-0">
        <div className="flex items-center space-x-3">
          <Target className="h-6 w-6 text-primary-400" />
          <div>
            <h3 className="text-lg font-semibold text-white">Future Predictions</h3>
            <p className="text-sm text-slate-300">Time-series analysis with ML predictions</p>
          </div>
        </div>
        
        {/* Controls */}
        <div className="flex items-center space-x-3">
          {/* Auto-refresh toggle */}
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
              autoRefresh 
                ? 'bg-primary-600 text-white' 
                : 'bg-slate-700 text-slate-300 hover:text-white'
            }`}
          >
            {autoRefresh ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            <span>{autoRefresh ? 'Auto' : 'Manual'}</span>
          </button>

        </div>
      </div>

      {/* Controls Panel */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Horizon Selection */}
        <div className="bg-slate-700/50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-slate-300 mb-3">Prediction Horizons</h4>
                     <div className="space-y-2">
             {['5min', '15min', '30min', '60min'].map((horizon) => (
               <label key={horizon} className="flex items-center space-x-2 cursor-pointer">
                 <input
                   type="checkbox"
                   checked={selectedHorizons.has(horizon)}
                   onChange={() => toggleHorizon(horizon)}
                   className="rounded border-slate-500 text-primary-600 focus:ring-primary-500"
                 />
                 <span className="text-sm text-white">{horizon}</span>
               </label>
             ))}
           </div>
        </div>

        {/* Time Range */}
        <div className="bg-slate-700/50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-slate-300 mb-3">Time Range</h4>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as any)}
            className="w-full bg-slate-600 border border-slate-500 rounded-lg px-3 py-2 text-sm text-white focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="1h">Last Hour</option>
            <option value="6h">Last 6 Hours</option>
            <option value="24h">Last 24 Hours</option>
          </select>
        </div>

        {/* Display Options */}
        <div className="bg-slate-700/50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-slate-300 mb-3">Display Options</h4>
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showConfidenceIntervals}
              onChange={(e) => setShowConfidenceIntervals(e.target.checked)}
              className="rounded border-slate-500 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-white">Show Confidence Intervals</span>
          </label>
        </div>
      </div>

      {/* Chart */}
      <div className="h-96 mb-6">
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="2 2" stroke="#4B5563" strokeOpacity={0.3} />
              <XAxis 
                dataKey="timestamp" 
                tickFormatter={formatTimestamp}
                stroke="#9CA3AF"
                fontSize={12}
                interval="preserveStartEnd"
                tick={{ fontSize: 10 }}
              />
              <YAxis 
                stroke="#9CA3AF"
                fontSize={12}
                label={{ value: 'Pb Concentrate (%)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#9CA3AF' } }}
                domain={[0, 50]} // Fixed range for Pb concentrate (0-50%)
                tickCount={11} // Show 11 ticks: 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50
                tick={{ fontSize: 10 }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              
              {/* Confidence Interval Areas (render first so they appear behind the lines) */}
              {showConfidenceIntervals && (() => {
                const horizonColors: Record<string, string> = {
                  '5min': '#10B981',   // Green
                  '15min': '#F59E0B',  // Orange
                  '30min': '#8B5CF6',  // Purple
                  '60min': '#3B82F6'   // Blue
                };
                
                return ['5min', '15min', '30min', '60min'].map(horizon => {
                  if (!selectedHorizons.has(horizon)) {
                    return null;
                  }
                  
                  const color = horizonColors[horizon];
                  const upperKey = `confidence_upper_${horizon}`;
                  
                  return (
                    <Area
                      key={`${horizon}-confidence`}
                      type="monotone"
                      dataKey={upperKey}
                      stroke="none"
                      fill={color}
                      fillOpacity={0.1}
                      connectNulls={true}
                      name={`${horizon} Confidence`}
                    />
                  );
                });
              })()}
              
              {/* Current values */}
              <Line
                type="monotone"
                dataKey="current"
                stroke="#EF4444"
                strokeWidth={3}
                dot={{ fill: '#EF4444', strokeWidth: 2, r: 4 }}
                connectNulls={true}
                name="Current Pb"
              />

              {/* Dynamic horizon predictions */}
              {(() => {
                const horizonColors: Record<string, string> = {
                  '5min': '#10B981',   // Green
                  '15min': '#F59E0B',  // Orange
                  '30min': '#8B5CF6',  // Purple
                  '60min': '#3B82F6'   // Blue (changed from red to avoid conflict with current Pb)
                };
                
                console.log('Rendering prediction lines for horizons:', Array.from(selectedHorizons));
                
                return ['5min', '15min', '30min', '60min'].map(horizon => {
                  if (!selectedHorizons.has(horizon)) {
                    console.log(`Skipping ${horizon} - not selected`);
                    return null;
                  }
                  
                  const color = horizonColors[horizon];
                  const dataKey = `predicted_${horizon}`;
                  
                  console.log(`Creating Line component for ${horizon} with dataKey: ${dataKey}, color: ${color}`);
                  
                  return (
                    <React.Fragment key={horizon}>
                      <Line
                        type="monotone"
                        dataKey={dataKey}
                        stroke={color}
                        strokeWidth={3}
                        strokeDasharray="8 4" // More visible dashed line for predictions
                        dot={{ fill: color, strokeWidth: 2, r: 4 }}
                        connectNulls={true}
                        name={`${horizon} Prediction`}
                      />
                    </React.Fragment>
                  );
                });
              })()}
            </ComposedChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Clock className="h-12 w-12 text-slate-400 mx-auto mb-4" />
              <p className="text-slate-300">No data available</p>
            </div>
          </div>
        )}
      </div>

      {/* Prediction Summary */}
      {futurePredictions && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(futurePredictions.future_predictions).map(([horizon, prediction]) => {
            const currentValue = currentData?.Actual_Pb_Concentrate || 0;
            const trendIcon = getTrendIcon(currentValue, prediction.prediction);
            
            return (
              <motion.div
                key={horizon}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-slate-700/50 rounded-lg p-4 border border-slate-600"
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-medium text-slate-300">{horizon} Prediction</h4>
                  {trendIcon}
                </div>
                <div className="text-2xl font-bold text-white mb-1">
                  {prediction.prediction.toFixed(2)}%
                </div>
                <div className="text-xs text-slate-400 mb-2">
                  Confidence: {(prediction.model_performance.r2_score * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-slate-400">
                  {prediction.confidence_interval.lower.toFixed(2)}% - {prediction.confidence_interval.upper.toFixed(2)}%
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="absolute inset-0 bg-slate-800/50 backdrop-blur-sm flex items-center justify-center rounded-xl">
          <ChartSkeleton />
        </div>
      )}
    </div>
  );
};

export default FuturePredictionChart;
