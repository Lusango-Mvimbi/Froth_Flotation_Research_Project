/**
 * Authentication Service Implementation
 * ====================================
 * 
 * Concrete implementation of the authentication service following SOLID principles.
 */

import { IAuthService, ILoginCredentials, ILoginResponse, IUser } from '../interfaces';
import { ApiService } from './ApiService';

export class AuthService implements IAuthService {
  private apiService: ApiService;
  private currentUser: IUser | null = null;
  private token: string | null = null;

  constructor(apiService: ApiService) {
    this.apiService = apiService;
    // Clear any stored authentication data and require fresh login
    this.clearStoredAuth();
  }

  async login(credentials: ILoginCredentials): Promise<ILoginResponse> {
    try {
      const response = await this.apiService.post<ILoginResponse>('/login', credentials);
      
      if (response.success && response.token && response.user) {
        this.token = response.token;
        this.currentUser = response.user;
        this.storeAuth();
        this.apiService.setAuthToken(response.token);
      }
      
      return response;
    } catch (error) {
      console.error('Login failed:', error);
      return {
        success: false,
        message: 'Login failed. Please check your credentials.',
        status_code: 500
      };
    }
  }

  async logout(): Promise<boolean> {
    try {
      if (this.token) {
        await this.apiService.get('/logout');
      }
    } catch (error) {
      console.error('Logout request failed:', error);
    } finally {
      this.clearAuth();
      return true;
    }
  }

  async verifyToken(token: string): Promise<boolean> {
    try {
      this.apiService.setAuthToken(token);
      const response = await this.apiService.get<{ success: boolean; user?: IUser }>('/verify');
      
      if (response.success && response.user) {
        this.currentUser = response.user;
        this.token = token;
        this.storeAuth();
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Token verification failed:', error);
      return false;
    }
  }

  getCurrentUser(): IUser | null {
    // Don't return stored user - require fresh login
    return null;
  }

  isAuthenticated(): boolean {
    // Don't automatically authenticate from stored data - require fresh login
    return false; // Always require fresh login
  }

  private storeAuth(): void {
    if (this.token && this.currentUser) {
      localStorage.setItem('auth_token', this.token);
      localStorage.setItem('current_user', JSON.stringify(this.currentUser));
    }
  }

  private loadStoredAuth(): void {
    const token = localStorage.getItem('auth_token');
    const userStr = localStorage.getItem('current_user');
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr) as IUser;
        this.token = token;
        this.currentUser = user;
        this.apiService.setAuthToken(token);
      } catch (error) {
        console.error('Failed to load stored auth:', error);
        this.clearAuth();
      }
    }
  }

  private clearAuth(): void {
    this.token = null;
    this.currentUser = null;
    this.apiService.removeAuthToken();
    localStorage.removeItem('auth_token');
    localStorage.removeItem('current_user');
  }

  private clearStoredAuth(): void {
    // Clear all possible authentication data from localStorage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('current_user');
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    console.log('🧹 Cleared stored authentication data');
  }
}
