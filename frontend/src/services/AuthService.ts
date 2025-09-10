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
    // Load stored authentication data if available
    this.loadStoredAuth();
  }

  async login(credentials: ILoginCredentials): Promise<ILoginResponse> {
    try {
      console.log('🔐 Attempting login for user:', credentials.username);
      
      // Clear any existing auth data first
      this.clearAuth();
      
      const response = await this.apiService.post<ILoginResponse>('/login', credentials);
      
      console.log('🔐 Login response received:', response);
      
      if (response.success && response.token && response.user) {
        this.token = response.token;
        this.currentUser = response.user;
        this.storeAuth();
        this.apiService.setAuthToken(response.token);
        console.log('🔐 Login successful for user:', response.user.username);
      } else {
        console.log('🔐 Login failed:', response.message);
      }
      
      return response;
    } catch (error) {
      console.error('🔐 Login failed with error:', error);
      
      // Handle specific error types
      if (error instanceof Error) {
        if (error.message.includes('message channel closed')) {
          console.warn('🔐 Message channel closed error detected - this may be caused by browser extensions');
          return {
            success: false,
            message: 'Login failed due to browser communication issue. Please try again or disable browser extensions.',
            status_code: 500
          };
        }
      }
      
      return {
        success: false,
        message: 'Login failed. Please check your credentials and try again.',
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
    // Return the current user if authenticated
    return this.currentUser;
  }

  isAuthenticated(): boolean {
    // Check if we have a valid token and user
    return !!(this.token && this.currentUser);
  }

  private storeAuth(): void {
    if (this.token && this.currentUser) {
      localStorage.setItem('auth_token', this.token);
      localStorage.setItem('current_user', JSON.stringify(this.currentUser));
      // Also store with the keys that the ApiService expects
      localStorage.setItem('authToken', this.token);
      localStorage.setItem('userData', JSON.stringify(this.currentUser));
    }
  }

  private loadStoredAuth(): void {
    // Try to load from multiple possible storage keys
    const token = localStorage.getItem('auth_token');
    const userStr = localStorage.getItem('current_user');
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr) as IUser;
        this.token = token;
        this.currentUser = user;
        this.apiService.setAuthToken(token);
        console.log('🔑 Loaded stored authentication for user:', user.username);
      } catch (error) {
        console.error('Failed to load stored auth:', error);
        this.clearAuth();
      }
    } else {
      console.log('🔑 No stored authentication found');
    }
  }

  private clearAuth(): void {
    this.token = null;
    this.currentUser = null;
    this.apiService.removeAuthToken();
    localStorage.removeItem('auth_token');
    localStorage.removeItem('current_user');
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
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
