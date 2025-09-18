import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Activity,
  AlertTriangle,
  CheckCircle,
  Calendar
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { historicalDataService, TIME_RANGES, TrendAnalysis } from '../services/historicalDataService';
import { FlotationData } from '../types';
import { useError } from '../contexts/ErrorContext';
import LoadingSkeleton from './LoadingSkeleton';

interface HistoricalAnalysisProps {
  className?: string;
}

const METRICS = [
  { key: 'Actual_Pb_Concentrate', label: 'Pb Concentrate', unit: '%', color: '#3b82f6' },
  { key: 'Actual_Pb_Recovery', label: 'Pb Recovery', unit: '%', color: '#10b981' },
  { key: 'Feed_Pb', label: 'Feed Pb', unit: '%', color: '#f59e0b' },
  { key: 'Pb_Conditioner_KEX_Flowrate', label: 'KEX Flowrate', unit: 'L/min', color: '#8b5cf6' },
  { key: 'Pb_Rougher1_SIPX_Flowrate', label: 'SIPX Flowrate', unit: 'L/min', color: '#06b6d4' },
  { key: 'Pb_Rougher1_AirFlow', label: 'Air Flow', unit: 'm³/min', color: '#84cc16' },
  { key: 'Pb_Rougher1_Level', label: 'Cell Level', unit: '%', color: '#f97316' }
] as const;

const HistoricalAnalysis: React.FC<HistoricalAnalysisProps> = ({ className = '' }) => {
  const [data, setData] = useState<FlotationData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState(TIME_RANGES[2]); // 24 hours
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([
    'Actual_Pb_Concentrate',
    'Actual_Pb_Recovery'
  ]);
  const [viewMode, setViewMode] = useState<'trends' | 'analysis' | 'anomalies'>('trends');
  const [useDateRange, setUseDateRange] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const { addError, showToast } = useError();

  const fetchHistoricalData = useCallback(async () => {
    console.log('HistoricalAnalysis: fetchHistoricalData called', {
      useDateRange,
      startDate,
      endDate,
      selectedTimeRange: selectedTimeRange?.label
    });
    
    try {
      setLoading(true);
      let response;
      
      if (useDateRange && startDate && endDate) {
        // Use date range filtering
        console.log('HistoricalAnalysis: Using date range filtering', { startDate, endDate });
        response = await historicalDataService.getHistoricalDataByDateRange(startDate, endDate);
      } else {
        // Use time range filtering
        console.log('HistoricalAnalysis: Using time range filtering', { selectedTimeRange: selectedTimeRange?.label });
        response = await historicalDataService.getHistoricalDataByTimeRange(selectedTimeRange);
      }
      
      setData(response.data);
      showToast(`Loaded ${response.data.length} data points`, 'success');
    } catch (error) {
      console.error('HistoricalAnalysis: Error fetching data', error);
      addError({
        type: 'data',
        message: 'Failed to fetch historical data',
        recoverable: true,
        suggestions: [
          'Check if the backend server is running',
          'Try refreshing the data',
          'Contact the data administrator'
        ]
      });
    } finally {
      setLoading(false);
    }
  }, [selectedTimeRange, useDateRange, startDate, endDate, addError, showToast]);

  useEffect(() => {
    fetchHistoricalData();
  }, [fetchHistoricalData]);

  const trendAnalysis = useMemo(() => {
    return METRICS.map(metric => {
      const analysis = historicalDataService.analyzeTrends(data, metric.key as keyof FlotationData);
      
      // Convert recovery values from decimal to percentage for display
      if (metric.key === 'Actual_Pb_Recovery') {
        return {
          ...analysis,
          average: analysis.average * 100,
          min: analysis.min * 100,
          max: analysis.max * 100,
          volatility: analysis.volatility * 100
        };
      }
      
      return analysis;
    });
  }, [data]);

  const timeSeriesData = useMemo(() => {
    // Reverse the data array so oldest points appear on the left
    const reversedData = [...data].reverse();
    
    // Debug: Log the first and last timestamps to verify order
    if (reversedData.length > 0) {
      console.log('HistoricalAnalysis: Time series data order:', {
        oldest: reversedData[0]?.timestamp,
        newest: reversedData[reversedData.length - 1]?.timestamp,
        totalPoints: reversedData.length
      });
    }
    
    return reversedData.map((point, index) => ({
      time: new Date(point.timestamp || Date.now() - (reversedData.length - index) * 60000),
      timestamp: point.timestamp || new Date(Date.now() - (reversedData.length - index) * 60000).toISOString(),
      ...selectedMetrics.reduce((acc, metricKey) => {
        const metric = METRICS.find(m => m.key === metricKey);
        if (metric) {
          let value = point[metric.key as keyof FlotationData] as number;
          
          // Convert recovery from decimal to percentage for display
          if (metricKey === 'Actual_Pb_Recovery') {
            value = (value || 0) * 100;
          }
          
          acc[metric.label] = value;
        }
        return acc;
      }, {} as Record<string, number>)
    }));
  }, [data, selectedMetrics]);

  const anomalyData = useMemo(() => {
    return METRICS.map(metric => {
      const anomalies = historicalDataService.detectAnomalies(data, metric.key as keyof FlotationData);
      
      // Convert recovery anomaly values from decimal to percentage for display
      if (metric.key === 'Actual_Pb_Recovery') {
        return {
          metric: metric.label,
          anomalies: anomalies.map(anomaly => ({
            ...anomaly,
            value: (anomaly?.value || 0) * 100
          }))
        };
      }
      
      return {
        metric: metric.label,
        anomalies
      };
    });
  }, [data]);

  const formatTime = (time: Date) => {
    return time.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };


  const getTrendIcon = (trend: TrendAnalysis['trend']) => {
    switch (trend) {
      case 'increasing':
        return <TrendingUp className="h-4 w-4 text-success-400" />;
      case 'decreasing':
        return <TrendingDown className="h-4 w-4 text-danger-400" />;
      default:
        return <Activity className="h-4 w-4 text-slate-400" />;
    }
  };

  const getTrendColor = (trend: TrendAnalysis['trend']) => {
    switch (trend) {
      case 'increasing':
        return 'text-success-400';
      case 'decreasing':
        return 'text-danger-400';
      default:
        return 'text-slate-400';
    }
  };

  if (loading) {
    return (
      <div className={`bg-slate-800 border border-slate-600 rounded-xl p-6 shadow-sm ${className}`}>
        <LoadingSkeleton />
      </div>
    );
  }

  return (
    <div className={`bg-slate-800 border border-slate-600 rounded-xl p-6 shadow-sm ${className}`}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 space-y-4 sm:space-y-0">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary-600 rounded-lg">
            <BarChart3 className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Historical Analysis</h2>
            <p className="text-sm text-slate-300">Trend analysis and data insights</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Date Range Toggle */}
          <button
            onClick={() => {
              console.log('HistoricalAnalysis: Date range toggle clicked', { currentUseDateRange: useDateRange });
              setUseDateRange(!useDateRange);
            }}
            className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              useDateRange 
                ? 'bg-primary-600 text-white' 
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            <Calendar className="h-4 w-4" />
            <span>Date Range</span>
          </button>

          {useDateRange ? (
            <>
              {/* Start Date */}
              <input
                type="date"
                value={startDate}
                onChange={(e) => {
                  console.log('HistoricalAnalysis: Start date changed', { startDate: e.target.value });
                  setStartDate(e.target.value);
                }}
                className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Start Date"
              />
              
              {/* End Date */}
              <input
                type="date"
                value={endDate}
                onChange={(e) => {
                  console.log('HistoricalAnalysis: End date changed', { endDate: e.target.value });
                  setEndDate(e.target.value);
                }}
                className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="End Date"
              />
            </>
          ) : (
            /* Time Range Selector */
            <select
              value={selectedTimeRange.label}
              onChange={(e) => {
                const range = TIME_RANGES.find(r => r.label === e.target.value);
                if (range) setSelectedTimeRange(range);
              }}
              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {TIME_RANGES.map(range => (
                <option key={range.label} value={range.label}>
                  {range.label}
                </option>
              ))}
            </select>
          )}

          {/* Refresh Button */}
          <button
            onClick={fetchHistoricalData}
            className="p-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
          >
            <Activity className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* View Mode Tabs */}
      <div className="flex space-x-1 bg-slate-700 rounded-lg p-1 mb-6">
        {[
          { key: 'trends', label: 'Trends', icon: TrendingUp },
          { key: 'analysis', label: 'Analysis', icon: BarChart3 },
          { key: 'anomalies', label: 'Anomalies', icon: AlertTriangle }
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setViewMode(key as any)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
              viewMode === key
                ? 'bg-primary-600 text-white shadow-lg'
                : 'text-slate-300 hover:text-white hover:bg-slate-600'
            }`}
          >
            <Icon className="h-4 w-4" />
            <span>{label}</span>
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {viewMode === 'trends' && (
          <motion.div
            key="trends"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Metric Selection */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {METRICS.map(metric => (
                <button
                  key={metric.key}
                  onClick={() => {
                    setSelectedMetrics(prev => 
                      prev.includes(metric.key)
                        ? prev.filter(m => m !== metric.key)
                        : [...prev, metric.key]
                    );
                  }}
                  className={`p-3 rounded-lg border text-sm font-medium transition-all ${
                    selectedMetrics.includes(metric.key)
                      ? 'bg-primary-600 border-primary-500 text-white'
                      : 'bg-slate-700 border-slate-600 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  {metric.label}
                </button>
              ))}
            </div>

            {/* Time Series Chart */}
            <div className="bg-slate-700/50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-4">Time Series Trends</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={timeSeriesData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                    <XAxis 
                      dataKey="time" 
                      tickFormatter={formatTime}
                      stroke="#94a3b8"
                      fontSize={12}
                    />
                    <YAxis stroke="#94a3b8" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1e293b',
                        border: '1px solid #475569',
                        borderRadius: '8px',
                        color: '#e2e8f0'
                      }}
                      labelFormatter={(value) => new Date(value).toLocaleString()}
                    />
                    {selectedMetrics.map((metricKey, index) => {
                      const metric = METRICS.find(m => m.key === metricKey);
                      if (!metric) return null;
                      return (
                        <Line
                          key={metric.key}
                          type="monotone"
                          dataKey={metric.label}
                          stroke={metric.color}
                          strokeWidth={2}
                          dot={false}
                          activeDot={{ r: 4, fill: metric.color }}
                        />
                      );
                    })}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </motion.div>
        )}

        {viewMode === 'analysis' && (
          <motion.div
            key="analysis"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Trend Analysis Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {trendAnalysis.map((trend, index) => {
                const metric = METRICS[index];
                if (!metric) return null;
                
                return (
                  <motion.div
                    key={metric.key}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-slate-700/50 rounded-lg p-4 border border-slate-600"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-semibold text-white">{metric.label}</h4>
                      {getTrendIcon(trend.trend)}
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">Trend:</span>
                        <span className={getTrendColor(trend.trend)}>
                          {trend.trend.charAt(0).toUpperCase() + trend.trend.slice(1)}
                        </span>
                      </div>
                      
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">Change:</span>
                        <span className={trend.changePercent >= 0 ? 'text-success-400' : 'text-danger-400'}>
                          {trend.changePercent >= 0 ? '+' : ''}{trend.changePercent.toFixed(1)}%
                        </span>
                      </div>
                      
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">Average:</span>
                        <span className="text-white">{trend.average.toFixed(2)} {metric.unit}</span>
                      </div>
                      
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">Range:</span>
                        <span className="text-white">
                          {trend.min.toFixed(1)} - {trend.max.toFixed(1)} {metric.unit}
                        </span>
                      </div>
                      
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">Volatility:</span>
                        <span className="text-white">{trend.volatility.toFixed(2)}</span>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}

        {viewMode === 'anomalies' && (
          <motion.div
            key="anomalies"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Anomaly Detection Results */}
            {anomalyData.filter(({ anomalies }) => anomalies.length > 0).length > 0 ? (
              <div className="space-y-4">
                {anomalyData.filter(({ anomalies }) => anomalies.length > 0).map(({ metric, anomalies }) => (
                <div key={metric} className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-white">{metric}</h4>
                    <div className="flex items-center space-x-2">
                      <AlertTriangle className="h-4 w-4 text-warning-400" />
                      <span className="text-sm text-slate-300">{anomalies.length} process alerts</span>
                    </div>
                  </div>
                  
                  {anomalies.length > 0 ? (
                    <div className="space-y-3">
                      {anomalies.slice(0, 5).map((anomaly, index) => {
                        if (!anomaly) return null;
                        return (
                          <div key={index} className="p-3 bg-slate-600/50 rounded-lg border-l-4 border-l-warning-400">
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex items-center space-x-2">
                                <div className={`w-2 h-2 rounded-full ${
                                  anomaly.severity === 'high' ? 'bg-danger-400' : 'bg-warning-400'
                                }`} />
                                <span className="text-sm font-medium text-white">
                                  {anomaly.type || 'Process Alert'}
                                </span>
                                <span className={`px-2 py-1 rounded text-xs ${
                                  anomaly.severity === 'high' 
                                    ? 'bg-danger-400/20 text-danger-300' 
                                    : 'bg-warning-400/20 text-warning-300'
                                }`}>
                                  {anomaly.severity?.toUpperCase()}
                                </span>
                              </div>
                              <span className="text-sm text-slate-400">
                                {anomaly.time?.toLocaleString() || 'Unknown time'}
                              </span>
                            </div>
                            <div className="text-sm text-white mb-2">
                              {anomaly.description}
                            </div>
                            <div className="text-xs text-slate-300 bg-slate-700/50 p-2 rounded">
                              <strong>Recommendation:</strong> {anomaly.recommendation}
                            </div>
                          </div>
                        );
                      })}
                      {anomalies.length > 5 && (
                        <p className="text-xs text-slate-400 text-center">
                          ... and {anomalies.length - 5} more alerts
                        </p>
                      )}
                    </div>
                  ) : (
                    <div className="flex items-center justify-center py-4">
                      <div className="flex items-center space-x-2 text-slate-400">
                        <CheckCircle className="h-4 w-4" />
                        <span className="text-sm">No process alerts - all parameters within normal ranges</span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              </div>
            ) : (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <CheckCircle className="h-12 w-12 text-green-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-white mb-2">No Process Alerts</h3>
                  <p className="text-slate-400">All process parameters are within normal operating ranges</p>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default HistoricalAnalysis;
