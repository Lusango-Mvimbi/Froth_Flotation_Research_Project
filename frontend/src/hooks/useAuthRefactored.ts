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

  // Check authentication status on mount - check for stored authentication
  useEffect(() => {
    const checkAuth = async () => {
      try {
        console.log('🔒 Authentication check: Checking for stored authentication');
        
        // Check if we have stored authentication data
        const token = localStorage.getItem('auth_token') || localStorage.getItem('authToken');
        const userStr = localStorage.getItem('current_user') || localStorage.getItem('userData');
        
        if (token && userStr) {
          try {
            const user = JSON.parse(userStr);
            console.log('🔑 Found stored authentication, verifying token...');
            
            // Verify the token is still valid
            const isValid = await authService.verifyToken(token);
            
            if (isValid) {
              setUser(user);
              setIsAuthenticated(true);
              console.log('✅ Stored authentication is valid, user logged in:', user.username);
            } else {
              console.log('❌ Stored token is invalid, clearing stored data');
              // Clear invalid stored data
              localStorage.removeItem('auth_token');
              localStorage.removeItem('current_user');
              localStorage.removeItem('authToken');
              localStorage.removeItem('userData');
              setUser(null);
              setIsAuthenticated(false);
            }
          } catch (error) {
            console.error('❌ Failed to parse stored user data:', error);
            // Clear corrupted stored data
            localStorage.removeItem('auth_token');
            localStorage.removeItem('current_user');
            localStorage.removeItem('authToken');
            localStorage.removeItem('userData');
            setUser(null);
            setIsAuthenticated(false);
          }
        } else {
          console.log('🔑 No stored authentication found, user needs to login');
          setUser(null);
          setIsAuthenticated(false);
        }
        
      } catch (error) {
        console.error('🔒 Auth check failed:', error);
        setUser(null);
        setIsAuthenticated(false);
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
        const errorMsg = response.error;
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
