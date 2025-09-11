import React from 'react';
import { motion } from 'framer-motion';
import { 
  AlertTriangle, 
  WifiOff, 
  Server, 
  Database, 
  RefreshCw, 
  Settings,
  CheckCircle,
  XCircle,
  Info
} from 'lucide-react';

export interface ErrorDetails {
  type: 'connection' | 'server' | 'data' | 'validation' | 'unknown';
  message: string;
  code?: string;
  timestamp: Date;
  recoverable: boolean;
  suggestions?: string[];
}

interface EnhancedErrorMessageProps {
  error: ErrorDetails;
  onRetry?: () => void;
  onDismiss?: () => void;
  onShowDetails?: () => void;
}

const getErrorIcon = (type: ErrorDetails['type']) => {
  switch (type) {
    case 'connection':
      return <WifiOff className="h-5 w-5" />;
    case 'server':
      return <Server className="h-5 w-5" />;
    case 'data':
      return <Database className="h-5 w-5" />;
    case 'validation':
      return <XCircle className="h-5 w-5" />;
    default:
      return <AlertTriangle className="h-5 w-5" />;
  }
};

const getErrorColor = (type: ErrorDetails['type']) => {
  switch (type) {
    case 'connection':
      return 'text-orange-400 bg-orange-900/20 border-orange-700';
    case 'server':
      return 'text-red-400 bg-red-900/20 border-red-700';
    case 'data':
      return 'text-yellow-400 bg-yellow-900/20 border-yellow-700';
    case 'validation':
      return 'text-blue-400 bg-blue-900/20 border-blue-700';
    default:
      return 'text-danger-400 bg-danger-900/20 border-danger-700';
  }
};

const getDefaultSuggestions = (type: ErrorDetails['type']): string[] => {
  switch (type) {
    case 'connection':
      return [
        'Check your internet connection',
        'Verify the backend server is running',
        'Try refreshing the page',
        'Contact IT support if the issue persists'
      ];
    case 'server':
      return [
        'The server may be temporarily unavailable',
        'Try again in a few moments',
        'Check server status with your administrator',
        'Report this issue if it continues'
      ];
    case 'data':
      return [
        'Data may be temporarily unavailable',
        'Try refreshing the data',
        'Check if the data source is accessible',
        'Contact the data administrator'
      ];
    case 'validation':
      return [
        'Please check your input values',
        'Ensure all required fields are filled',
        'Verify the data format is correct',
        'Try again with valid data'
      ];
    default:
      return [
        'An unexpected error occurred',
        'Try refreshing the page',
        'Contact support if the issue persists'
      ];
  }
};

const EnhancedErrorMessage: React.FC<EnhancedErrorMessageProps> = ({
  error,
  onRetry,
  onDismiss,
  onShowDetails
}) => {
  const colorClasses = getErrorColor(error.type);
  const suggestions = error.suggestions || getDefaultSuggestions(error.type);
  const Icon = getErrorIcon(error.type);

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`mb-6 p-4 border rounded-lg ${colorClasses}`}
    >
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 mt-0.5">
          {Icon}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium">
              {error.type.charAt(0).toUpperCase() + error.type.slice(1)} Error
            </h3>
            <div className="flex items-center space-x-2">
              {error.recoverable && onRetry && (
                <button
                  onClick={onRetry}
                  className="flex items-center space-x-1 px-2 py-1 text-xs bg-slate-700 hover:bg-slate-600 text-slate-200 rounded transition-colors"
                >
                  <RefreshCw className="h-3 w-3" />
                  <span>Retry</span>
                </button>
              )}
              {onDismiss && (
                <button
                  onClick={onDismiss}
                  className="text-slate-400 hover:text-slate-200 transition-colors"
                >
                  <XCircle className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
          
          <p className="text-sm mb-3">
            {error.message}
          </p>
          
          {error.code && (
            <p className="text-xs text-slate-400 mb-3 font-mono">
              Error Code: {error.code}
            </p>
          )}
          
          <div className="space-y-2">
            <h4 className="text-xs font-medium text-slate-300">
              Suggested Actions:
            </h4>
            <ul className="space-y-1">
              {suggestions.map((suggestion, index) => (
                <li key={index} className="flex items-start space-x-2 text-xs">
                  <CheckCircle className="h-3 w-3 text-slate-400 mt-0.5 flex-shrink-0" />
                  <span className="text-slate-300">{suggestion}</span>
                </li>
              ))}
            </ul>
          </div>
          
          <div className="mt-3 pt-3 border-t border-slate-600">
            <div className="flex items-center justify-between">
              <p className="text-xs text-slate-400">
                {error.timestamp.toLocaleTimeString()}
              </p>
              {onShowDetails && (
                <button
                  onClick={onShowDetails}
                  className="flex items-center space-x-1 text-xs text-slate-400 hover:text-slate-200 transition-colors"
                >
                  <Info className="h-3 w-3" />
                  <span>Show Details</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default EnhancedErrorMessage;
