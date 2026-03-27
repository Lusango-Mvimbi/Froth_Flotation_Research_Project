import { ErrorDetails } from '../components/EnhancedErrorMessage';

export const createError = (
  type: ErrorDetails['type'],
  message: string,
  options: {
    code?: string;
    recoverable?: boolean;
    suggestions?: string[];
  } = {}
): Omit<ErrorDetails, 'timestamp'> => {
  return {
    type,
    message,
    code: options.code,
    recoverable: options.recoverable ?? true,
    suggestions: options.suggestions
  };
};

export const createConnectionError = (message: string = 'Unable to connect to the server') => {
  return createError('connection', message, {
    code: 'CONN_001',
    suggestions: [
      'Check your internet connection',
      'Verify the backend server is running on port 8000',
      'Try refreshing the page',
      'Contact IT support if the issue persists'
    ]
  });
};

export const createServerError = (message: string = 'Server is temporarily unavailable') => {
  return createError('server', message, {
    code: 'SRV_001',
    suggestions: [
      'The server may be temporarily unavailable',
      'Try again in a few moments',
      'Check server status with your administrator',
      'Report this issue if it continues'
    ]
  });
};

export const createDataError = (message: string = 'Unable to fetch data') => {
  return createError('data', message, {
    code: 'DATA_001',
    suggestions: [
      'Data may be temporarily unavailable',
      'Try refreshing the data',
      'Check if the data source is accessible',
      'Contact the data administrator'
    ]
  });
};

export const createValidationError = (message: string = 'Invalid input data') => {
  return createError('validation', message, {
    code: 'VAL_001',
    suggestions: [
      'Please check your input values',
      'Ensure all required fields are filled',
      'Verify the data format is correct',
      'Try again with valid data'
    ]
  });
};

export const createMLModelError = (message: string = 'ML model prediction failed') => {
  return createError('server', message, {
    code: 'ML_001',
    suggestions: [
      'ML model may be temporarily unavailable',
      'Try refreshing the predictions',
      'Check if the model files are accessible',
      'Contact the ML administrator'
    ]
  });
};

export const createControlError = (message: string = 'Control update failed') => {
  return createError('validation', message, {
    code: 'CTRL_001',
    suggestions: [
      'Check if the control values are within valid ranges',
      'Ensure the control system is online',
      'Try again with different values',
      'Contact the control system administrator'
    ]
  });
};

// Error classification utility
export const classifyError = (error: any): ErrorDetails['type'] => {
  if (error?.message?.includes('fetch') || error?.message?.includes('network')) {
    return 'connection';
  }
  
  if (error?.status >= 500) {
    return 'server';
  }
  
  if (error?.status >= 400 && error?.status < 500) {
    return 'validation';
  }
  
  if (error?.message?.includes('data') || error?.message?.includes('model')) {
    return 'data';
  }
  
  return 'unknown';
};

// Error message extraction
export const extractErrorMessage = (error: any): string => {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error?.response?.data?.detail) {
    return error.response.data.detail;
  }
  
  if (error?.response?.data?.message) {
    return error.response.data.message;
  }
  
  if (error?.message) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
};
