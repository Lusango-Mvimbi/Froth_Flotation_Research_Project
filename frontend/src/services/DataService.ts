/**
 * Data Service Implementation
 * ==========================
 * 
 * Concrete implementation of the data service following SOLID principles.
 */

import { IDataService, IFloationData, IParameterRanges } from '../interfaces';
import { ApiService } from './ApiService';
import { WebSocketService } from './WebSocketService';

export class DataService implements IDataService {
  private apiService: ApiService;
  private wsService: WebSocketService;
  private wsUrl: string;
  private dataCallbacks: ((data: IFloationData) => void)[] = [];

  constructor(apiService: ApiService, wsService: WebSocketService, wsUrl: string = 'ws://localhost:8000/ws') {
    this.apiService = apiService;
    this.wsService = wsService;
    this.wsUrl = wsUrl;
    this.setupWebSocket();
  }

  async getCurrentData(): Promise<IFloationData> {
    try {
      const response = await this.apiService.get<{ data_point: IFloationData }>('/generate-data');
      return response.data_point;
    } catch (error) {
      console.error('Failed to get current data:', error);
      throw error;
    }
  }

  async getParameterRanges(): Promise<IParameterRanges> {
    try {
      const response = await this.apiService.get<{ parameter_ranges: IParameterRanges }>('/parameter-ranges');
      return response.parameter_ranges;
    } catch (error) {
      console.error('Failed to get parameter ranges:', error);
      throw error;
    }
  }

  async validateParameters(parameters: Record<string, number>): Promise<boolean> {
    try {
      const response = await this.apiService.post<{ is_valid: boolean }>('/validate-parameters', parameters);
      return response.is_valid;
    } catch (error) {
      console.error('Failed to validate parameters:', error);
      return false;
    }
  }

  subscribeToRealTimeData(callback: (data: IFloationData) => void): () => void {
    this.dataCallbacks.push(callback);
    
    // Return unsubscribe function
    return () => {
      const index = this.dataCallbacks.indexOf(callback);
      if (index > -1) {
        this.dataCallbacks.splice(index, 1);
      }
    };
  }

  private setupWebSocket(): void {
    this.wsService.onMessage((data) => {
      if (data.type === 'data_point' && data.data) {
        const flotationData = data.data as IFloationData;
        this.dataCallbacks.forEach(callback => callback(flotationData));
      }
    });

    this.wsService.onConnect(() => {
      console.log('WebSocket connected for real-time data');
    });

    this.wsService.onDisconnect(() => {
      console.log('WebSocket disconnected from real-time data');
    });

    // Connect to WebSocket
    this.connectWebSocket();
  }

  private async connectWebSocket(): Promise<void> {
    try {
      await this.wsService.connect(this.wsUrl);
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error);
      // Retry connection after 5 seconds
      setTimeout(() => this.connectWebSocket(), 5000);
    }
  }

  // Method to manually request new data
  async requestNewData(): Promise<void> {
    if (this.wsService.isConnected()) {
      this.wsService.send({ type: 'request_data' });
    }
  }

  // Method to get connection status
  isConnected(): boolean {
    return this.wsService.isConnected();
  }

  // Method to disconnect
  disconnect(): void {
    this.wsService.disconnect();
  }
}
