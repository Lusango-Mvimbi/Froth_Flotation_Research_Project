/**
 * WebSocket Service Implementation
 * ===============================
 * 
 * Concrete implementation of the WebSocket service following SOLID principles.
 */

import { IWebSocketService } from '../interfaces';

export class WebSocketService implements IWebSocketService {
  private socket: WebSocket | null = null;
  private messageCallbacks: ((data: any) => void)[] = [];
  private connectCallbacks: (() => void)[] = [];
  private disconnectCallbacks: (() => void)[] = [];

  async connect(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.socket = new WebSocket(url);

        this.socket.onopen = () => {
          console.log('WebSocket connected');
          this.connectCallbacks.forEach(callback => callback());
          resolve();
        };

        this.socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.messageCallbacks.forEach(callback => callback(data));
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.socket.onclose = () => {
          console.log('WebSocket disconnected');
          this.disconnectCallbacks.forEach(callback => callback());
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  send(message: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  onMessage(callback: (data: any) => void): void {
    this.messageCallbacks.push(callback);
  }

  onConnect(callback: () => void): void {
    this.connectCallbacks.push(callback);
  }

  onDisconnect(callback: () => void): void {
    this.disconnectCallbacks.push(callback);
  }

  isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
  }

  // Cleanup method to remove callbacks
  removeMessageCallback(callback: (data: any) => void): void {
    const index = this.messageCallbacks.indexOf(callback);
    if (index > -1) {
      this.messageCallbacks.splice(index, 1);
    }
  }

  removeConnectCallback(callback: () => void): void {
    const index = this.connectCallbacks.indexOf(callback);
    if (index > -1) {
      this.connectCallbacks.splice(index, 1);
    }
  }

  removeDisconnectCallback(callback: () => void): void {
    const index = this.disconnectCallbacks.indexOf(callback);
    if (index > -1) {
      this.disconnectCallbacks.splice(index, 1);
    }
  }
}
