/**
 * Chart Service Unit Tests
 * =======================
 * 
 * Unit tests for the ChartService following SOLID principles.
 */

import { ChartService } from '../../services/ChartService';
import { IFloationData, IModelInfo } from '../../interfaces';

// Mock the Chart.js library
jest.mock('chart.js/auto', () => ({
  Chart: jest.fn(),
  registerables: []
}));

describe('ChartService', () => {
  let chartService: ChartService;

  beforeEach(() => {
    chartService = new ChartService();
  });

  describe('createLineChartData', () => {
    it('should create line chart data for a single parameter', () => {
      const mockData: IFloationData[] = [
        {
          timestamp: '2024-01-01T10:00:00Z',
          pH: 11.0,
          Temperature: 25.0,
          Pulp_Density: 30.0,
          Feed_Pb: 2.5,
          Feed_Zn: 10.0,
          Pb_Conditioner_KEX_Flowrate: 45.0,
          Pb_Rougher1_SIPX_Flowrate: 22.0,
          Pb_Rougher1_AirFlow: 120.0,
          Pb_Rougher1_Level: 70.0,
          Impeller_Speed: 1200,
          Froth_Height: 15.0,
          pb_concentrate: 10.5,
          recovery_rate: 85.0,
          process_status: 'optimal',
          recommendations: ['Process operating within optimal ranges'],
          model_info: {
            model_name: 'GradientBoosting',
            model_type: 'Gradient Boosting',
            test_r2: 0.85,
            test_rmse: 0.5,
            test_mae: 0.3,
            test_pred_10_percent: 0.9,
            training_date: '2024-01-01',
            status: 'loaded'
          }
        },
        {
          timestamp: '2024-01-01T10:01:00Z',
          pH: 11.2,
          Temperature: 25.5,
          Pulp_Density: 30.5,
          Feed_Pb: 2.6,
          Feed_Zn: 10.2,
          Pb_Conditioner_KEX_Flowrate: 46.0,
          Pb_Rougher1_SIPX_Flowrate: 22.5,
          Pb_Rougher1_AirFlow: 121.0,
          Pb_Rougher1_Level: 70.5,
          Impeller_Speed: 1205,
          Froth_Height: 15.2,
          pb_concentrate: 10.8,
          recovery_rate: 86.0,
          process_status: 'optimal',
          recommendations: ['Process operating within optimal ranges'],
          model_info: {
            model_name: 'GradientBoosting',
            model_type: 'Gradient Boosting',
            test_r2: 0.85,
            test_rmse: 0.5,
            test_mae: 0.3,
            test_pred_10_percent: 0.9,
            training_date: '2024-01-01',
            status: 'loaded'
          }
        }
      ];

      const result = chartService.createLineChartData(mockData, 'pH');

      expect(result).toHaveProperty('labels');
      expect(result).toHaveProperty('datasets');
      expect(result.labels).toHaveLength(2);
      expect(result.datasets).toHaveLength(1);
      expect(result.datasets[0].label).toBe('pH');
      expect(result.datasets[0].data).toEqual([11.0, 11.2]);
      expect(result.datasets[0]).toHaveProperty('borderColor');
      expect(result.datasets[0]).toHaveProperty('backgroundColor');
      expect(result.datasets[0]).toHaveProperty('tension');
    });

    it('should handle missing parameter values', () => {
      const mockData: IFloationData[] = [
        {
          timestamp: '2024-01-01T10:00:00Z',
          pH: 11.0,
          Temperature: 25.0,
          Pulp_Density: 30.0,
          Feed_Pb: 2.5,
          Feed_Zn: 10.0,
          Pb_Conditioner_KEX_Flowrate: 45.0,
          Pb_Rougher1_SIPX_Flowrate: 22.0,
          Pb_Rougher1_AirFlow: 120.0,
          Pb_Rougher1_Level: 70.0,
          Impeller_Speed: 1200,
          Froth_Height: 15.0,
          pb_concentrate: 10.5,
          recovery_rate: 85.0,
          process_status: 'optimal',
          recommendations: ['Process operating within optimal ranges'],
          model_info: {
            model_name: 'GradientBoosting',
            model_type: 'Gradient Boosting',
            test_r2: 0.85,
            test_rmse: 0.5,
            test_mae: 0.3,
            test_pred_10_percent: 0.9,
            training_date: '2024-01-01',
            status: 'loaded'
          }
        }
      ];

      const result = chartService.createLineChartData(mockData, 'NonExistentParameter');

      expect(result.datasets[0].data).toEqual([0]);
    });

    it('should handle empty data array', () => {
      const result = chartService.createLineChartData([], 'pH');

      expect(result.labels).toHaveLength(0);
      expect(result.datasets[0].data).toHaveLength(0);
    });
  });

  describe('createMultiParameterChart', () => {
    it('should create multi-parameter chart data', () => {
      const mockData: IFloationData[] = [
        {
          timestamp: '2024-01-01T10:00:00Z',
          pH: 11.0,
          Temperature: 25.0,
          Pulp_Density: 30.0,
          Feed_Pb: 2.5,
          Feed_Zn: 10.0,
          Pb_Conditioner_KEX_Flowrate: 45.0,
          Pb_Rougher1_SIPX_Flowrate: 22.0,
          Pb_Rougher1_AirFlow: 120.0,
          Pb_Rougher1_Level: 70.0,
          Impeller_Speed: 1200,
          Froth_Height: 15.0,
          pb_concentrate: 10.5,
          recovery_rate: 85.0,
          process_status: 'optimal',
          recommendations: ['Process operating within optimal ranges'],
          model_info: {
            model_name: 'GradientBoosting',
            model_type: 'Gradient Boosting',
            test_r2: 0.85,
            test_rmse: 0.5,
            test_mae: 0.3,
            test_pred_10_percent: 0.9,
            training_date: '2024-01-01',
            status: 'loaded'
          }
        },
        {
          timestamp: '2024-01-01T10:01:00Z',
          pH: 11.2,
          Temperature: 25.5,
          Pulp_Density: 30.5,
          Feed_Pb: 2.6,
          Feed_Zn: 10.2,
          Pb_Conditioner_KEX_Flowrate: 46.0,
          Pb_Rougher1_SIPX_Flowrate: 22.5,
          Pb_Rougher1_AirFlow: 121.0,
          Pb_Rougher1_Level: 70.5,
          Impeller_Speed: 1205,
          Froth_Height: 15.2,
          pb_concentrate: 10.8,
          recovery_rate: 86.0,
          process_status: 'optimal',
          recommendations: ['Process operating within optimal ranges'],
          model_info: {
            model_name: 'GradientBoosting',
            model_type: 'Gradient Boosting',
            test_r2: 0.85,
            test_rmse: 0.5,
            test_mae: 0.3,
            test_pred_10_percent: 0.9,
            training_date: '2024-01-01',
            status: 'loaded'
          }
        }
      ];

      const parameters = ['pH', 'Temperature'];
      const result = chartService.createMultiParameterChart(mockData, parameters);

      expect(result).toHaveProperty('labels');
      expect(result).toHaveProperty('datasets');
      expect(result.labels).toHaveLength(2);
      expect(result.datasets).toHaveLength(2);
      expect(result.datasets[0].label).toBe('pH');
      expect(result.datasets[1].label).toBe('Temperature');
      expect(result.datasets[0].data).toEqual([11.0, 11.2]);
      expect(result.datasets[1].data).toEqual([25.0, 25.5]);
    });

    it('should handle missing parameters', () => {
      const mockData: IFloationData[] = [
        {
          timestamp: '2024-01-01T10:00:00Z',
          pH: 11.0,
          Temperature: 25.0,
          Pulp_Density: 30.0,
          Feed_Pb: 2.5,
          Feed_Zn: 10.0,
          Pb_Conditioner_KEX_Flowrate: 45.0,
          Pb_Rougher1_SIPX_Flowrate: 22.0,
          Pb_Rougher1_AirFlow: 120.0,
          Pb_Rougher1_Level: 70.0,
          Impeller_Speed: 1200,
          Froth_Height: 15.0,
          pb_concentrate: 10.5,
          recovery_rate: 85.0,
          process_status: 'optimal',
          recommendations: ['Process operating within optimal ranges'],
          model_info: {
            model_name: 'GradientBoosting',
            model_type: 'Gradient Boosting',
            test_r2: 0.85,
            test_rmse: 0.5,
            test_mae: 0.3,
            test_pred_10_percent: 0.9,
            training_date: '2024-01-01',
            status: 'loaded'
          }
        }
      ];

      const parameters = ['pH', 'NonExistentParameter'];
      const result = chartService.createMultiParameterChart(mockData, parameters);

      expect(result.datasets).toHaveLength(2);
      expect(result.datasets[0].data).toEqual([11.0]);
      expect(result.datasets[1].data).toEqual([0]);
    });

    it('should handle empty data array', () => {
      const result = chartService.createMultiParameterChart([], ['pH', 'Temperature']);

      expect(result.labels).toHaveLength(0);
      expect(result.datasets[0].data).toHaveLength(0);
      expect(result.datasets[1].data).toHaveLength(0);
    });
  });

  describe('getChartOptions', () => {
    it('should return chart options with title', () => {
      const options = chartService.getChartOptions('Test Chart');

      expect(options).toHaveProperty('responsive');
      expect(options).toHaveProperty('plugins');
      expect(options.plugins).toHaveProperty('title');
      expect(options.plugins.title).toHaveProperty('display');
      expect(options.plugins.title).toHaveProperty('text');
      expect(options.plugins.title.text).toBe('Test Chart');
    });

    it('should return chart options with default title', () => {
      const options = chartService.getChartOptions('');

      expect(options.plugins.title.text).toBe('Froth Flotation Data');
    });
  });

  describe('createProcessStatusChart', () => {
    it('should create process status chart data', () => {
      const mockData: IFloationData[] = [
        {
          timestamp: '2024-01-01T10:00:00Z',
          pH: 11.0,
          Temperature: 25.0,
          Pulp_Density: 30.0,
          Feed_Pb: 2.5,
          Feed_Zn: 10.0,
          Pb_Conditioner_KEX_Flowrate: 45.0,
          Pb_Rougher1_SIPX_Flowrate: 22.0,
          Pb_Rougher1_AirFlow: 120.0,
          Pb_Rougher1_Level: 70.0,
          Impeller_Speed: 1200,
          Froth_Height: 15.0,
          pb_concentrate: 10.5,
          recovery_rate: 85.0,
          process_status: 'optimal',
          recommendations: ['Process operating within optimal ranges'],
          model_info: {
            model_name: 'GradientBoosting',
            model_type: 'Gradient Boosting',
            test_r2: 0.85,
            test_rmse: 0.5,
            test_mae: 0.3,
            test_pred_10_percent: 0.9,
            training_date: '2024-01-01',
            status: 'loaded'
          }
        },
        {
          timestamp: '2024-01-01T10:01:00Z',
          pH: 11.2,
          Temperature: 25.5,
          Pulp_Density: 30.5,
          Feed_Pb: 2.6,
          Feed_Zn: 10.2,
          Pb_Conditioner_KEX_Flowrate: 46.0,
          Pb_Rougher1_SIPX_Flowrate: 22.5,
          Pb_Rougher1_AirFlow: 121.0,
          Pb_Rougher1_Level: 70.5,
          Impeller_Speed: 1205,
          Froth_Height: 15.2,
          pb_concentrate: 10.8,
          recovery_rate: 86.0,
          process_status: 'warning',
          recommendations: ['Monitor process parameters'],
          model_info: {
            model_name: 'GradientBoosting',
            model_type: 'Gradient Boosting',
            test_r2: 0.85,
            test_rmse: 0.5,
            test_mae: 0.3,
            test_pred_10_percent: 0.9,
            training_date: '2024-01-01',
            status: 'loaded'
          }
        }
      ];

      const result = chartService.createProcessStatusChart(mockData);

      expect(result).toHaveProperty('labels');
      expect(result).toHaveProperty('datasets');
      expect(result.labels).toHaveLength(2);
      expect(result.datasets).toHaveLength(1);
      expect(result.datasets[0].label).toBe('Process Status');
      expect(result.datasets[0].data).toEqual([1, 1]); // Both optimal and warning count as 1
    });

    it('should handle empty data array', () => {
      const result = chartService.createProcessStatusChart([]);

      expect(result.labels).toHaveLength(0);
      expect(result.datasets[0].data).toHaveLength(0);
    });
  });

  describe('createRecoveryRateChart', () => {
    it('should create recovery rate chart data', () => {
      const mockData: IFloationData[] = [
        {
          timestamp: '2024-01-01T10:00:00Z',
          pH: 11.0,
          Temperature: 25.0,
          Pulp_Density: 30.0,
          Feed_Pb: 2.5,
          Feed_Zn: 10.0,
          Pb_Conditioner_KEX_Flowrate: 45.0,
          Pb_Rougher1_SIPX_Flowrate: 22.0,
          Pb_Rougher1_AirFlow: 120.0,
          Pb_Rougher1_Level: 70.0,
          Impeller_Speed: 1200,
          Froth_Height: 15.0,
          pb_concentrate: 10.5,
          recovery_rate: 85.0,
          process_status: 'optimal',
          recommendations: ['Process operating within optimal ranges'],
          model_info: {
            model_name: 'GradientBoosting',
            model_type: 'Gradient Boosting',
            test_r2: 0.85,
            test_rmse: 0.5,
            test_mae: 0.3,
            test_pred_10_percent: 0.9,
            training_date: '2024-01-01',
            status: 'loaded'
          }
        },
        {
          timestamp: '2024-01-01T10:01:00Z',
          pH: 11.2,
          Temperature: 25.5,
          Pulp_Density: 30.5,
          Feed_Pb: 2.6,
          Feed_Zn: 10.2,
          Pb_Conditioner_KEX_Flowrate: 46.0,
          Pb_Rougher1_SIPX_Flowrate: 22.5,
          Pb_Rougher1_AirFlow: 121.0,
          Pb_Rougher1_Level: 70.5,
          Impeller_Speed: 1205,
          Froth_Height: 15.2,
          pb_concentrate: 10.8,
          recovery_rate: 86.0,
          process_status: 'optimal',
          recommendations: ['Process operating within optimal ranges'],
          model_info: {
            model_name: 'GradientBoosting',
            model_type: 'Gradient Boosting',
            test_r2: 0.85,
            test_rmse: 0.5,
            test_mae: 0.3,
            test_pred_10_percent: 0.9,
            training_date: '2024-01-01',
            status: 'loaded'
          }
        }
      ];

      const result = chartService.createRecoveryRateChart(mockData);

      expect(result).toHaveProperty('labels');
      expect(result).toHaveProperty('datasets');
      expect(result.labels).toHaveLength(2);
      expect(result.datasets).toHaveLength(1);
      expect(result.datasets[0].label).toBe('Recovery Rate (%)');
      expect(result.datasets[0].data).toEqual([85.0, 86.0]);
    });

    it('should handle empty data array', () => {
      const result = chartService.createRecoveryRateChart([]);

      expect(result.labels).toHaveLength(0);
      expect(result.datasets[0].data).toHaveLength(0);
    });
  });
});
