/**
 * Chart Service Implementation
 * ===========================
 * 
 * Concrete implementation of the chart service following SOLID principles.
 */

import { IChartService, IChartData, IChartDataset, IFloationData } from '../interfaces';

export class ChartService implements IChartService {
  private defaultColors = [
    '#3B82F6', // Blue
    '#EF4444', // Red
    '#10B981', // Green
    '#F59E0B', // Yellow
    '#8B5CF6', // Purple
    '#06B6D4', // Cyan
    '#F97316', // Orange
    '#84CC16', // Lime
  ];

  createLineChartData(data: IFloationData[], parameter: string): IChartData {
    const labels = data.map(item => this.formatTime(item.timestamp));
    const values = data.map(item => (item as any)[parameter] || 0);
    
    const dataset: IChartDataset = {
      label: parameter,
      data: values,
      borderColor: this.getParameterColor(parameter),
      backgroundColor: this.getParameterColor(parameter) + '20',
      tension: 0.4,
    };

    return {
      labels,
      datasets: [dataset],
    };
  }

  createMultiParameterChart(data: IFloationData[], parameters: string[]): IChartData {
    const labels = data.map(item => this.formatTime(item.timestamp));
    const datasets: IChartDataset[] = parameters.map((parameter, index) => {
      const values = data.map(item => (item as any)[parameter] || 0);
      
      return {
        label: parameter,
        data: values,
        borderColor: this.getParameterColor(parameter),
        backgroundColor: this.getParameterColor(parameter) + '20',
        tension: 0.4,
      };
    });

    return {
      labels,
      datasets,
    };
  }

  getChartOptions(title: string): any {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: title || 'Froth Flotation Data',
          font: {
            size: 16,
            weight: 'bold',
          },
        },
        legend: {
          display: true,
          position: 'top' as const,
        },
        tooltip: {
          mode: 'index' as const,
          intersect: false,
        },
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'Time',
          },
        },
        y: {
          display: true,
          title: {
            display: true,
            text: 'Value',
          },
        },
      },
      interaction: {
        mode: 'nearest' as const,
        axis: 'x' as const,
        intersect: false,
      },
    };
  }

  createProcessStatusChart(data: IFloationData[]): IChartData {
    const labels = data.map(item => this.formatTime(item.timestamp));
    const statusValues = data.map(item => {
      switch (item.process_status) {
        case 'optimal': return 1;
        case 'warning': return 1;
        case 'critical': return 0;
        case 'error': return 0;
        default: return 0;
      }
    });

    const dataset: IChartDataset = {
      label: 'Process Status',
      data: statusValues,
      borderColor: '#10B981',
      backgroundColor: '#10B98120',
      tension: 0.4,
    };

    return {
      labels,
      datasets: [dataset],
    };
  }

  createRecoveryRateChart(data: IFloationData[]): IChartData {
    const labels = data.map(item => this.formatTime(item.timestamp));
    const recoveryValues = data.map(item => item.recovery_rate);

    const dataset: IChartDataset = {
      label: 'Recovery Rate (%)',
      data: recoveryValues,
      borderColor: '#22C55E',
      backgroundColor: '#22C55E20',
      tension: 0.4,
    };

    return {
      labels,
      datasets: [dataset],
    };
  }

  private formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  }

  private getParameterColor(parameter: string): string {
    const colorMap: Record<string, string> = {
      pH: '#3B82F6',
      Temperature: '#EF4444',
      Pulp_Density: '#10B981',
      Feed_Pb: '#F59E0B',
      Feed_Zn: '#8B5CF6',
      Pb_Conditioner_KEX_Flowrate: '#06B6D4',
      Pb_Rougher1_SIPX_Flowrate: '#F97316',
      Pb_Rougher1_AirFlow: '#84CC16',
      Pb_Rougher1_Level: '#EC4899',
      Impeller_Speed: '#6366F1',
      Froth_Height: '#14B8A6',
      pb_concentrate: '#F43F5E',
      recovery_rate: '#22C55E',
    };

    return colorMap[parameter] || this.defaultColors[0];
  }
}
