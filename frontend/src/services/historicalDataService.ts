import axios from 'axios';
import { FlotationData } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export interface HistoricalDataResponse {
  data: FlotationData[];
  count: number;
  timestamp: string;
}

export interface TrendAnalysis {
  metric: string;
  trend: 'increasing' | 'decreasing' | 'stable';
  changePercent: number;
  average: number;
  min: number;
  max: number;
  volatility: number;
}

export interface TimeRange {
  label: string;
  hours: number;
  limit: number;
}

export const TIME_RANGES: TimeRange[] = [
  { label: 'Last Hour', hours: 1, limit: 60 },
  { label: 'Last 6 Hours', hours: 6, limit: 360 },
  { label: 'Last 24 Hours', hours: 24, limit: 1440 },
  { label: 'Last Week', hours: 168, limit: 10080 },
  { label: 'Last Month', hours: 720, limit: 43200 }
];

export const historicalDataService = {
  async getHistoricalData(limit: number = 100): Promise<HistoricalDataResponse> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/database/sensor-data`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch historical data:', error);
      throw error;
    }
  },

  async getHistoricalDataByTimeRange(timeRange: TimeRange): Promise<HistoricalDataResponse> {
    return this.getHistoricalData(timeRange.limit);
  },

  analyzeTrends(data: FlotationData[], metric: keyof FlotationData): TrendAnalysis {
    if (data.length < 2) {
      return {
        metric: metric as string,
        trend: 'stable',
        changePercent: 0,
        average: 0,
        min: 0,
        max: 0,
        volatility: 0
      };
    }

    const values = data.map(d => d[metric] as number).filter(v => v != null);
    if (values.length < 2) {
      return {
        metric: metric as string,
        trend: 'stable',
        changePercent: 0,
        average: 0,
        min: 0,
        max: 0,
        volatility: 0
      };
    }

    const firstValue = values[0];
    const lastValue = values[values.length - 1];
    const changePercent = ((lastValue - firstValue) / firstValue) * 100;
    
    const average = values.reduce((sum, val) => sum + val, 0) / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);
    
    // Calculate volatility (standard deviation)
    const variance = values.reduce((sum, val) => sum + Math.pow(val - average, 2), 0) / values.length;
    const volatility = Math.sqrt(variance);

    let trend: 'increasing' | 'decreasing' | 'stable' = 'stable';
    if (changePercent > 5) trend = 'increasing';
    else if (changePercent < -5) trend = 'decreasing';

    return {
      metric: metric as string,
      trend,
      changePercent,
      average,
      min,
      max,
      volatility
    };
  },

  generateTimeSeriesData(data: FlotationData[], metric: keyof FlotationData) {
    return data.map((point, index) => ({
      time: new Date(point.timestamp || Date.now() - (data.length - index) * 60000),
      value: point[metric] as number,
      index
    })).filter(point => point.value != null);
  },

  calculateMovingAverage(data: FlotationData[], metric: keyof FlotationData, windowSize: number = 10) {
    const values = data.map(d => d[metric] as number).filter(v => v != null);
    const movingAverages = [];
    
    for (let i = windowSize - 1; i < values.length; i++) {
      const window = values.slice(i - windowSize + 1, i + 1);
      const average = window.reduce((sum, val) => sum + val, 0) / window.length;
      movingAverages.push({
        time: new Date(data[i].timestamp || Date.now() - (data.length - i) * 60000),
        value: average,
        index: i
      });
    }
    
    return movingAverages;
  },

  detectAnomalies(data: FlotationData[], metric: keyof FlotationData, threshold: number = 2) {
    const values = data.map(d => d[metric] as number).filter(v => v != null);
    if (values.length < 3) return [];

    const average = values.reduce((sum, val) => sum + val, 0) / values.length;
    const variance = values.reduce((sum, val) => sum + Math.pow(val - average, 2), 0) / values.length;
    const standardDeviation = Math.sqrt(variance);

    return data.map((point, index) => {
      const value = point[metric] as number;
      if (value == null) return null;
      
      const zScore = Math.abs((value - average) / standardDeviation);
      return zScore > threshold ? {
        time: new Date(point.timestamp || Date.now() - (data.length - index) * 60000),
        value,
        zScore,
        severity: zScore > 3 ? 'high' : 'medium',
        index
      } : null;
    }).filter(anomaly => anomaly !== null);
  }
};
