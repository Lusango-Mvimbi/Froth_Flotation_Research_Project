import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { toast } from 'react-hot-toast';
import { ErrorDetails } from '../components/EnhancedErrorMessage';

interface ErrorContextType {
  errors: ErrorDetails[];
  addError: (error: Omit<ErrorDetails, 'timestamp'>) => void;
  removeError: (index: number) => void;
  clearErrors: () => void;
  showToast: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
}

const ErrorContext = createContext<ErrorContextType | undefined>(undefined);

export const useError = () => {
  const context = useContext(ErrorContext);
  if (!context) {
    throw new Error('useError must be used within an ErrorProvider');
  }
  return context;
};

interface ErrorProviderProps {
  children: ReactNode;
}

export const ErrorProvider: React.FC<ErrorProviderProps> = ({ children }) => {
  const [errors, setErrors] = useState<ErrorDetails[]>([]);

  const addError = useCallback((error: Omit<ErrorDetails, 'timestamp'>) => {
    const errorWithTimestamp: ErrorDetails = {
      ...error,
      timestamp: new Date()
    };
    
    setErrors(prev => [...prev, errorWithTimestamp]);
    
    // Show toast notification
    const toastMessage = error.message;
    switch (error.type) {
      case 'connection':
        toast.error(`Connection Error: ${toastMessage}`, { duration: 5000 });
        break;
      case 'server':
        toast.error(`Server Error: ${toastMessage}`, { duration: 5000 });
        break;
      case 'data':
        toast.error(`Data Error: ${toastMessage}`, { duration: 4000 });
        break;
      case 'validation':
        toast.error(`Validation Error: ${toastMessage}`, { duration: 4000 });
        break;
      default:
        toast.error(`Error: ${toastMessage}`, { duration: 4000 });
    }
  }, []);

  const removeError = useCallback((index: number) => {
    setErrors(prev => prev.filter((_, i) => i !== index));
  }, []);

  const clearErrors = useCallback(() => {
    setErrors([]);
  }, []);

  const showToast = useCallback((message: string, type: 'success' | 'error' | 'warning' | 'info') => {
    switch (type) {
      case 'success':
        toast.success(message, { duration: 3000 });
        break;
      case 'error':
        toast.error(message, { duration: 4000 });
        break;
      case 'warning':
        toast(message, { 
          icon: '⚠️',
          style: {
            background: '#f59e0b',
            color: '#fff',
          },
          duration: 4000
        });
        break;
      case 'info':
        toast(message, { 
          icon: 'ℹ️',
          style: {
            background: '#3b82f6',
            color: '#fff',
          },
          duration: 3000
        });
        break;
    }
  }, []);

  const value: ErrorContextType = {
    errors,
    addError,
    removeError,
    clearErrors,
    showToast
  };

  return (
    <ErrorContext.Provider value={value}>
      {children}
    </ErrorContext.Provider>
  );
};
