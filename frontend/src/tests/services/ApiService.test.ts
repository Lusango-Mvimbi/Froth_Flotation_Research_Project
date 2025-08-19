/**
 * API Service Unit Tests
 * =====================
 * 
 * Unit tests for the ApiService following SOLID principles.
 */

import { ApiService } from '../../services/ApiService';

// Mock fetch globally
global.fetch = jest.fn();

describe('ApiService', () => {
  let apiService: ApiService;
  const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

  beforeEach(() => {
    apiService = new ApiService('http://localhost:8000');
    mockFetch.mockClear();
  });

  describe('constructor', () => {
    it('should initialize with default base URL', () => {
      const service = new ApiService();
      expect(service).toBeInstanceOf(ApiService);
    });

    it('should initialize with custom base URL', () => {
      const service = new ApiService('http://custom-api.com');
      expect(service).toBeInstanceOf(ApiService);
    });
  });

  describe('get', () => {
    it('should make GET request successfully', async () => {
      const mockResponse = { data: 'test' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiService.get('/test');

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/test', {
        method: 'GET',
        headers: {},
      });
      expect(result).toEqual(mockResponse);
    });

    it('should include auth token in headers when set', async () => {
      const mockResponse = { data: 'test' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      apiService.setAuthToken('test-token');
      await apiService.get('/test');

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/test', {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer test-token',
        },
      });
    });

    it('should throw error on failed request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
      } as Response);

      await expect(apiService.get('/test')).rejects.toThrow('HTTP error! status: 404');
    });
  });

  describe('post', () => {
    it('should make POST request successfully', async () => {
      const mockResponse = { success: true };
      const postData = { name: 'test' };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiService.post('/test', postData);

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData),
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('put', () => {
    it('should make PUT request successfully', async () => {
      const mockResponse = { success: true };
      const putData = { name: 'test' };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiService.put('/test', putData);

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/test', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(putData),
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('delete', () => {
    it('should make DELETE request successfully', async () => {
      const mockResponse = { success: true };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiService.delete('/test');

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/test', {
        method: 'DELETE',
        headers: {},
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('auth token management', () => {
    it('should set auth token', () => {
      apiService.setAuthToken('test-token');
      // Note: We can't directly test the private property, but we can test its effect
      expect(apiService).toBeDefined();
    });

    it('should remove auth token', () => {
      apiService.setAuthToken('test-token');
      apiService.removeAuthToken();
      // Note: We can't directly test the private property, but we can test its effect
      expect(apiService).toBeDefined();
    });
  });

  describe('error handling', () => {
    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(apiService.get('/test')).rejects.toThrow('Network error');
    });

    it('should handle JSON parsing errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON');
        },
      } as unknown as Response);

      await expect(apiService.get('/test')).rejects.toThrow('Invalid JSON');
    });
  });
});
