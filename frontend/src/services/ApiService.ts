/**
 * API Service Implementation
 * =========================
 * 
 * Concrete implementation of the API service.
 */

import { IApiService } from '../interfaces';

export class ApiService implements IApiService {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await this.makeRequest<T>(endpoint, {
      method: 'GET',
    });
    return response;
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await this.makeRequest<T>(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response;
  }

  async put<T>(endpoint: string, data: any): Promise<T> {
    const response = await this.makeRequest<T>(endpoint, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response;
  }

  async delete<T>(endpoint: string): Promise<T> {
    const response = await this.makeRequest<T>(endpoint, {
      method: 'DELETE',
    });
    return response;
  }

  setAuthToken(token: string): void {
    this.authToken = token;
  }

  removeAuthToken(): void {
    this.authToken = null;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const headers: HeadersInit = {
      ...options.headers,
    };

    if (this.authToken) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.authToken}`;
    }

    const config: RequestInit = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data as T;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }
}
