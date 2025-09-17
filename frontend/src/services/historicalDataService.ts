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

  async getHistoricalDataByDateRange(startDate: string, endDate: string, limit: number = 1000): Promise<HistoricalDataResponse> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/database/sensor-data`, {
        params: { 
          limit,
          start_date: startDate,
          end_date: endDate
        }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch historical data by date range:', error);
      throw error;
    }
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
    const alerts: any[] = [];
    
    // Process-specific alert detection instead of statistical anomalies
    data.forEach((point, index) => {
      const timestamp = new Date(point.timestamp || Date.now() - (data.length - index) * 60000);
      const value = point[metric] as number;
      if (value == null) return;

      let alert = null;

      // Pb Concentrate alerts
      if (metric === 'Actual_Pb_Concentrate') {
        if (value < 10) {
          alert = {
            time: timestamp,
            value: value.toFixed(2),
            description: `Low Pb Concentrate: ${value.toFixed(2)}% (Target: 15-35%)`,
            severity: 'high',
            type: 'Low Concentrate',
            recommendation: 'Check reagent rates and flotation conditions'
          };
        } else if (value > 40) {
          alert = {
            time: timestamp,
            value: value.toFixed(2),
            description: `High Pb Concentrate: ${value.toFixed(2)}% (Target: 15-35%)`,
            severity: 'high',
            type: 'High Concentrate',
            recommendation: 'Reduce collector dosage or check feed grade'
          };
        } else if (value < 12 || value > 30) {
          alert = {
            time: timestamp,
            value: value.toFixed(2),
            description: `Pb Concentrate outside optimal range: ${value.toFixed(2)}%`,
            severity: 'medium',
            type: 'Suboptimal Concentrate',
            recommendation: 'Adjust KEX or SIPX rates'
          };
        }
      }

      // Pb Recovery alerts
      if (metric === 'Actual_Pb_Recovery') {
        const recoveryPercent = value * 100;
        if (recoveryPercent < 60) {
          alert = {
            time: timestamp,
            value: recoveryPercent.toFixed(1),
            description: `Low Pb Recovery: ${recoveryPercent.toFixed(1)}% (Target: >70%)`,
            severity: 'high',
            type: 'Low Recovery',
            recommendation: 'Check flotation conditions and reagent effectiveness'
          };
        } else if (recoveryPercent > 95) {
          alert = {
            time: timestamp,
            value: recoveryPercent.toFixed(1),
            description: `Very High Pb Recovery: ${recoveryPercent.toFixed(1)}%`,
            severity: 'medium',
            type: 'High Recovery',
            recommendation: 'Monitor concentrate grade quality'
          };
        } else if (recoveryPercent < 65) {
          alert = {
            time: timestamp,
            value: recoveryPercent.toFixed(1),
            description: `Pb Recovery below target: ${recoveryPercent.toFixed(1)}%`,
            severity: 'medium',
            type: 'Suboptimal Recovery',
            recommendation: 'Optimize flotation parameters'
          };
        }
      }

      // Feed Grade alerts
      if (metric === 'Feed_Pb') {
        if (value < 0.5) {
          alert = {
            time: timestamp,
            value: value.toFixed(2),
            description: `Low Feed Grade: ${value.toFixed(2)}%`,
            severity: 'high',
            type: 'Low Feed Grade',
            recommendation: 'Check upstream processing and ore quality'
          };
        } else if (value > 3.0) {
          alert = {
            time: timestamp,
            value: value.toFixed(2),
            description: `High Feed Grade: ${value.toFixed(2)}%`,
            severity: 'medium',
            type: 'High Feed Grade',
            recommendation: 'Adjust flotation parameters for high-grade feed'
          };
        }
      }

      // Flow rate alerts
      if (metric === 'Pb_Conditioner_KEX_Flowrate') {
        if (value < 20) {
          alert = {
            time: timestamp,
            value: value.toFixed(1),
            description: `Low KEX Flow Rate: ${value.toFixed(1)} L/min`,
            severity: 'high',
            type: 'Low KEX Flow',
            recommendation: 'Check KEX pump and dosing system'
          };
        } else if (value > 100) {
          alert = {
            time: timestamp,
            value: value.toFixed(1),
            description: `High KEX Flow Rate: ${value.toFixed(1)} L/min`,
            severity: 'medium',
            type: 'High KEX Flow',
            recommendation: 'Verify KEX dosing accuracy'
          };
        }
      }

      if (metric === 'Pb_Rougher1_SIPX_Flowrate') {
        if (value < 10) {
          alert = {
            time: timestamp,
            value: value.toFixed(1),
            description: `Low SIPX Flow Rate: ${value.toFixed(1)} L/min`,
            severity: 'high',
            type: 'Low SIPX Flow',
            recommendation: 'Check SIPX pump and dosing system'
          };
        } else if (value > 80) {
          alert = {
            time: timestamp,
            value: value.toFixed(1),
            description: `High SIPX Flow Rate: ${value.toFixed(1)} L/min`,
            severity: 'medium',
            type: 'High SIPX Flow',
            recommendation: 'Verify SIPX dosing accuracy'
          };
        }
      }

      if (alert) {
        alerts.push(alert);
      }
    });

    return alerts;
  }
};
