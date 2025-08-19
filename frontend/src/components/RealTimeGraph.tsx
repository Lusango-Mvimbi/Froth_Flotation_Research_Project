import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';
import { TrendingUp, Activity, Clock } from 'lucide-react';
import { FlotationData, Prediction, Recommendation } from '../types';
import RecommendationsPanel from './RecommendationsPanel';

interface RealTimeGraphProps {
  data: FlotationData[];
  currentData: FlotationData | null;
  predictions: Prediction | null;
  recommendations?: Recommendation[];
}

const RealTimeGraph: React.FC<RealTimeGraphProps> = ({ 
  data, 
  currentData, 
  predictions,
  recommendations = []
}) => {
  // Transform data for chart
  const chartData = useMemo(() => {
    return data.map((item, index) => ({
      time: index,
      timestamp: new Date(item.timestamp || Date.now()).toLocaleTimeString(),
      'Pb Concentrate': typeof item.Pb_Concentrate === 'number' ? item.Pb_Concentrate : 0,
      'Recovery Rate': typeof item.Pb_Recovery === 'number' ? item.Pb_Recovery : 0,
      'pH Level': typeof item.pH === 'number' ? item.pH : 0,
      'Air Flow': typeof item.Pb_Rougher1_AirFlow === 'number' ? item.Pb_Rougher1_AirFlow : 0,
      'KEX Flow': typeof item.Pb_Conditioner_KEX_Flowrate === 'number' ? item.Pb_Conditioner_KEX_Flowrate : 0,
      'SIPX Flow': typeof item.Pb_Rougher1_SIPX_Flowrate === 'number' ? item.Pb_Rougher1_SIPX_Flowrate : 0,
      'Feed Grade': typeof item.Feed_Pb === 'number' ? item.Feed_Pb : 0,
      'Impeller Speed': typeof item.Impeller_Speed === 'number' ? item.Impeller_Speed : 0,
    }));
  }, [data]);

  // Get performance color for a value based on ML model status
  const getPerformanceColor = (value: number, metric: 'pb' | 'recovery', status?: string) => {
    // Use ML model status if available, otherwise fall back to value-based logic
    if (status) {
      switch (status) {
        case 'critical': return '#ef4444'; // Red
        case 'warning': return '#f59e0b';  // Yellow
        case 'optimal': return '#22c55e';  // Green
        default: break;
      }
    }
    
    // Fallback to value-based logic
    if (metric === 'pb') {
      if (value < 15) return '#ef4444'; // Red
      if (value >= 25) return '#f59e0b'; // Yellow
      return '#22c55e'; // Green
    } else {
      if (value < 75) return '#ef4444'; // Red
      if (value >= 95) return '#f59e0b'; // Yellow
      return '#22c55e'; // Green
    }
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-dark-800 border border-dark-600 rounded-lg p-3 shadow-lg">
          <p className="text-white font-semibold mb-2">
            Time: {payload[0]?.payload?.timestamp || 'N/A'}
          </p>
          {payload.map((entry: any, index: number) => {
            const value = entry.value;
            const displayValue = typeof value === 'number' && !isNaN(value) 
              ? value.toFixed(2) 
              : 'N/A';
            
            return (
              <p key={index} style={{ color: entry.color }} className="text-sm">
                {entry.name}: {displayValue}
              </p>
            );
          })}
        </div>
      );
    }
    return null;
  };

  if (!data.length) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass rounded-xl p-6 h-96 flex items-center justify-center"
      >
        <div className="text-center">
          <Activity className="h-12 w-12 text-dark-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">No Data Available</h3>
          <p className="text-dark-300">Waiting for real-time data...</p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-xl p-6 h-full"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary-600 rounded-lg">
            <TrendingUp className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Real-time Performance</h2>
            <p className="text-sm text-dark-300">Live process monitoring</p>
          </div>
        </div>
        
        {currentData && (
          <div className="flex items-center space-x-2 text-sm text-dark-300">
            <Clock className="h-4 w-4" />
            <span>Last update: {new Date(currentData.timestamp).toLocaleTimeString()}</span>
          </div>
        )}
      </div>

      {/* Main Chart */}
      <div className="h-80 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <defs>
              <linearGradient id="pbGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0.1}/>
              </linearGradient>
              <linearGradient id="recoveryGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            
            <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
            <XAxis 
              dataKey="time" 
              stroke="#94a3b8"
              fontSize={12}
              tickFormatter={(value) => chartData[value]?.timestamp || ''}
            />
            <YAxis 
              stroke="#94a3b8"
              fontSize={12}
              domain={[0, 100]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            
            <Area
              type="monotone"
              dataKey="Pb Concentrate"
              stroke="#22c55e"
              strokeWidth={2}
              fill="url(#pbGradient)"
              dot={{ fill: '#22c55e', strokeWidth: 2, r: 3 }}
              activeDot={{ r: 6, stroke: '#22c55e', strokeWidth: 2 }}
            />
            
            <Area
              type="monotone"
              dataKey="Recovery Rate"
              stroke="#3b82f6"
              strokeWidth={2}
              fill="url(#recoveryGradient)"
              dot={{ fill: '#3b82f6', strokeWidth: 2, r: 3 }}
              activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Performance Indicators */}
      {currentData && predictions && (
        <div className="grid grid-cols-2 gap-4">
          {/* Pb Concentrate Performance */}
          <div className="p-4 bg-dark-700/50 rounded-lg border border-dark-600">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-semibold text-white">Pb Concentrate</h4>
              <div 
                className="w-3 h-3 rounded-full"
                style={{ 
                  backgroundColor: getPerformanceColor(
                    typeof currentData.Pb_Concentrate === 'number' ? currentData.Pb_Concentrate : 0, 
                    'pb', 
                    currentData.Pb_Concentrate_Status
                  ) 
                }}
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold text-white">
                {typeof currentData.Pb_Concentrate === 'number' && !isNaN(currentData.Pb_Concentrate) 
                  ? currentData.Pb_Concentrate.toFixed(2) 
                  : 'N/A'}%
              </span>
              <span className="text-sm text-dark-300">
                Target: 15-25%
              </span>
            </div>
            <div className="mt-2 text-xs text-dark-400">
              Status: {currentData.Pb_Concentrate_Status || 'optimal'}
            </div>
          </div>

          {/* Recovery Rate Performance */}
          <div className="p-4 bg-dark-700/50 rounded-lg border border-dark-600">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-semibold text-white">Recovery Rate</h4>
              <div 
                className="w-3 h-3 rounded-full"
                style={{ 
                  backgroundColor: getPerformanceColor(
                    typeof currentData.Pb_Recovery === 'number' ? currentData.Pb_Recovery * 100 : 0, 
                    'recovery', 
                    currentData.Recovery_Status
                  ) 
                }}
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold text-white">
                {typeof currentData.Pb_Recovery === 'number' && !isNaN(currentData.Pb_Recovery) 
                  ? (currentData.Pb_Recovery * 100).toFixed(1) 
                  : 'N/A'}%
              </span>
              <span className="text-sm text-dark-300">
                Target: 75-95%
              </span>
            </div>
            <div className="mt-2 text-xs text-dark-400">
              Status: {currentData.Recovery_Status || 'optimal'}
            </div>
          </div>
        </div>
      )}

      {/* Process Parameters */}
      {currentData && (
        <div className="mt-6">
          <h4 className="text-sm font-semibold text-white mb-3">Process Parameters</h4>
          <div className="grid grid-cols-3 gap-3 text-xs">
            <div className="p-2 bg-dark-700/30 rounded">
              <span className="text-dark-300">pH:</span>
              <span className="text-white ml-1">
                {typeof currentData.pH === 'number' && !isNaN(currentData.pH) 
                  ? currentData.pH.toFixed(1) 
                  : 'N/A'}
              </span>
            </div>
            <div className="p-2 bg-dark-700/30 rounded">
              <span className="text-dark-300">Air Flow:</span>
              <span className="text-white ml-1">{currentData.Pb_Rougher1_AirFlow || 'N/A'} L/min</span>
            </div>
            <div className="p-2 bg-dark-700/30 rounded">
              <span className="text-dark-300">KEX:</span>
              <span className="text-white ml-1">{currentData.Pb_Conditioner_KEX_Flowrate || 'N/A'} L/min</span>
            </div>
            <div className="p-2 bg-dark-700/30 rounded">
              <span className="text-dark-300">SIPX:</span>
              <span className="text-white ml-1">{currentData.Pb_Rougher1_SIPX_Flowrate || 'N/A'} L/min</span>
            </div>
            <div className="p-2 bg-dark-700/30 rounded">
              <span className="text-dark-300">Feed Grade:</span>
              <span className="text-white ml-1">{currentData.Feed_Pb || 'N/A'}%</span>
            </div>
            <div className="p-2 bg-dark-700/30 rounded">
              <span className="text-dark-300">Impeller:</span>
              <span className="text-white ml-1">{currentData.Impeller_Speed || 'N/A'} RPM</span>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations Panel */}
      <div className="mt-6">
        <RecommendationsPanel
          recommendations={recommendations}
          predictions={predictions}
          currentData={currentData}
        />
      </div>
    </motion.div>
  );
};

export default RealTimeGraph;
