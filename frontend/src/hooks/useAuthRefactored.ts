/**
 * Refactored Authentication Hook
 * =============================
 * 
 * React hook for authentication following SOLID principles.
 */

import React, { useState, useEffect, useCallback, createContext, useContext, useMemo } from 'react';
import { IAuthContext, ILoginCredentials, ILoginResponse, IUser } from '../interfaces';
import { AuthService } from '../services/AuthService';
import { ApiService } from '../services/ApiService';

// Create the auth context
const AuthContext = createContext<IAuthContext | undefined>(undefined);

// Hook to use the auth context
export const useAuth = (): IAuthContext => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Auth Provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<IUser | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | undefined>(undefined);

  // Initialize auth service with useMemo to prevent recreation
  const authService = useMemo(() => {
    const apiService = new ApiService('http://localhost:8051'); // Authentication service runs on port 8051
    return new AuthService(apiService);
  }, []);

  // Check authentication status on mount - require fresh login
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Always start with no authentication - require fresh login
        setUser(null);
        setIsAuthenticated(false);
        console.log('🔒 Authentication check: Requiring fresh login');
        
        // Clear any stored auth data to prevent conflicts
        localStorage.removeItem('auth_token');
        localStorage.removeItem('current_user');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        
      } catch (error) {
        console.error('🔒 Auth check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []); // Remove authService dependency since it's memoized

  // Login function
  const login = useCallback(async (credentials: ILoginCredentials): Promise<ILoginResponse> => {
    setLoading(true);
    setError(undefined);
    try {
      console.log('🔐 useAuth: Starting login process');
      const response = await authService.login(credentials);
      
      console.log('🔐 useAuth: Login response:', response);
      
      if (response.success && response.user) {
        setUser(response.user);
        setIsAuthenticated(true);
        console.log('🔐 useAuth: Login successful, user authenticated');
      } else {
        const errorMsg = response.error || response.message || 'Login failed';
        setError(errorMsg);
        console.log('🔐 useAuth: Login failed:', errorMsg);
      }
      
      return response;
    } catch (error) {
      console.error('🔐 useAuth: Login error:', error);
      
      // Handle message channel closed errors
      if (error instanceof Error && error.message.includes('message channel closed')) {
        const errorMessage = 'Login failed due to browser communication issue. Please try again or disable browser extensions.';
        setError(errorMessage);
        return {
          success: false,
          message: errorMessage,
          error: errorMessage,
          status_code: 500
        };
      }
      
      const errorMessage = 'Login failed. Please try again.';
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage,
        error: errorMessage,
        status_code: 500
      };
    } finally {
      setLoading(false);
    }
  }, []); // Remove authService dependency since it's memoized

  // Debug function to set authentication state
  const debugSetAuth = useCallback((auth: boolean) => {
    setIsAuthenticated(auth);
    if (!auth) {
      setUser(null);
    }
  }, []);

  // Logout function
  const logout = useCallback(async (): Promise<void> => {
    setLoading(true);
    try {
      await authService.logout();
      setUser(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setLoading(false);
    }
  }, []); // Remove authService dependency since it's memoized

  const contextValue: IAuthContext = {
    user,
    isAuthenticated,
    login,
    logout,
    loading,
    error,
    debugSetAuth,
  };

  return React.createElement(
    AuthContext.Provider,
    { value: contextValue },
    children
  );
};
