/**
 * WebSocket Service Unit Tests
 * ===========================
 * 
 * Unit tests for the WebSocketService following SOLID principles.
 */

import { WebSocketService } from '../../services/WebSocketService';

// Mock WebSocket
class MockWebSocket {
  public readyState: number = WebSocket.CONNECTING;
  public onopen: ((event: any) => void) | null = null;
  public onmessage: ((event: any) => void) | null = null;
  public onclose: ((event: any) => void) | null = null;
  public onerror: ((event: any) => void) | null = null;
  public url: string;

  constructor(url: string) {
    this.url = url;
    // Simulate connection after a short delay
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      if (this.onopen) {
        this.onopen({});
      }
    }, 10);
  }

  send(data: string): void {
    // Mock send functionality
  }

  close(): void {
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) {
      this.onclose({});
    }
  }
}

// Mock WebSocket globally
global.WebSocket = MockWebSocket as any;

describe('WebSocketService', () => {
  let wsService: WebSocketService;

  beforeEach(() => {
    wsService = new WebSocketService();
  });

  describe('constructor', () => {
    it('should initialize WebSocket service', () => {
      expect(wsService).toBeInstanceOf(WebSocketService);
      expect(wsService.isConnected()).toBe(false);
    });
  });

  describe('connect', () => {
    it('should connect to WebSocket successfully', async () => {
      const connectPromise = wsService.connect('ws://localhost:8000/ws');
      
      // Wait for the mock connection to establish
      await new Promise(resolve => setTimeout(resolve, 20));
      
      await connectPromise;
      expect(wsService.isConnected()).toBe(true);
    });

    it('should handle connection errors', async () => {
      // Mock WebSocket to throw error
      const originalWebSocket = global.WebSocket;
      global.WebSocket = jest.fn().mockImplementation(() => {
        throw new Error('Connection failed');
      }) as any;

      await expect(wsService.connect('ws://invalid-url')).rejects.toThrow('Connection failed');

      // Restore original WebSocket
      global.WebSocket = originalWebSocket;
    });
  });

  describe('disconnect', () => {
    it('should disconnect WebSocket', async () => {
      await wsService.connect('ws://localhost:8000/ws');
      await new Promise(resolve => setTimeout(resolve, 20));
      
      expect(wsService.isConnected()).toBe(true);
      
      wsService.disconnect();
      expect(wsService.isConnected()).toBe(false);
    });

    it('should handle disconnect when not connected', () => {
      expect(() => wsService.disconnect()).not.toThrow();
    });
  });

  describe('send', () => {
    it('should send message when connected', async () => {
      const mockSend = jest.fn();
      const originalWebSocket = global.WebSocket;
      
      global.WebSocket = jest.fn().mockImplementation((url: string) => {
        const mockWs = new MockWebSocket(url);
        mockWs.send = mockSend;
        return mockWs;
      }) as any;

      await wsService.connect('ws://localhost:8000/ws');
      await new Promise(resolve => setTimeout(resolve, 20));
      
      const message = { type: 'test', data: 'test-data' };
      wsService.send(message);
      
      expect(mockSend).toHaveBeenCalledWith(JSON.stringify(message));

      global.WebSocket = originalWebSocket;
    });

    it('should warn when sending message without connection', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      
      wsService.send({ type: 'test' });
      
      expect(consoleSpy).toHaveBeenCalledWith('WebSocket is not connected');
      
      consoleSpy.mockRestore();
    });
  });

  describe('event callbacks', () => {
    it('should register and trigger message callbacks', async () => {
      const messageCallback = jest.fn();
      wsService.onMessage(messageCallback);
      
      await wsService.connect('ws://localhost:8000/ws');
      await new Promise(resolve => setTimeout(resolve, 20));
      
      // Simulate receiving a message
      const mockEvent = { data: JSON.stringify({ type: 'test', data: 'test-data' }) };
      (wsService as any).socket.onmessage(mockEvent);
      
      expect(messageCallback).toHaveBeenCalledWith({ type: 'test', data: 'test-data' });
    });

    it('should register and trigger connect callbacks', async () => {
      const connectCallback = jest.fn();
      wsService.onConnect(connectCallback);
      
      await wsService.connect('ws://localhost:8000/ws');
      await new Promise(resolve => setTimeout(resolve, 20));
      
      expect(connectCallback).toHaveBeenCalled();
    });

    it('should register and trigger disconnect callbacks', async () => {
      const disconnectCallback = jest.fn();
      wsService.onDisconnect(disconnectCallback);
      
      await wsService.connect('ws://localhost:8000/ws');
      await new Promise(resolve => setTimeout(resolve, 20));
      
      wsService.disconnect();
      
      expect(disconnectCallback).toHaveBeenCalled();
    });
  });

  describe('isConnected', () => {
    it('should return false when not connected', () => {
      expect(wsService.isConnected()).toBe(false);
    });

    it('should return true when connected', async () => {
      await wsService.connect('ws://localhost:8000/ws');
      await new Promise(resolve => setTimeout(resolve, 20));
      
      expect(wsService.isConnected()).toBe(true);
    });
  });

  describe('callback management', () => {
    it('should remove message callback', () => {
      const callback = jest.fn();
      wsService.onMessage(callback);
      wsService.removeMessageCallback(callback);
      
      // Should not throw when trying to remove non-existent callback
      expect(() => wsService.removeMessageCallback(callback)).not.toThrow();
    });

    it('should remove connect callback', () => {
      const callback = jest.fn();
      wsService.onConnect(callback);
      wsService.removeConnectCallback(callback);
      
      expect(() => wsService.removeConnectCallback(callback)).not.toThrow();
    });

    it('should remove disconnect callback', () => {
      const callback = jest.fn();
      wsService.onDisconnect(callback);
      wsService.removeDisconnectCallback(callback);
      
      expect(() => wsService.removeDisconnectCallback(callback)).not.toThrow();
    });
  });

  describe('error handling', () => {
    it('should handle JSON parsing errors in messages', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      await wsService.connect('ws://localhost:8000/ws');
      await new Promise(resolve => setTimeout(resolve, 20));
      
      // Simulate receiving invalid JSON
      const mockEvent = { data: 'invalid-json' };
      (wsService as any).socket.onmessage(mockEvent);
      
      expect(consoleSpy).toHaveBeenCalledWith('Failed to parse WebSocket message:', expect.any(Error));
      
      consoleSpy.mockRestore();
    });
  });
});
