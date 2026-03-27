import React, { Component, ErrorInfo, ReactNode } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ error, errorInfo });
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  handleGoHome = () => {
    window.location.href = '/dashboard';
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-slate-800 border border-slate-600 rounded-xl p-8 max-w-2xl w-full shadow-lg"
          >
            <div className="text-center">
              <div className="flex justify-center mb-6">
                <div className="p-4 bg-danger-600/20 rounded-full">
                  <AlertTriangle className="h-12 w-12 text-danger-400" />
                </div>
              </div>
              
              <h1 className="text-2xl font-bold text-white mb-4">
                System Error
              </h1>
              
              <p className="text-slate-300 mb-6">
                An unexpected error occurred in the flotation monitoring system. 
                This has been logged for investigation.
              </p>

              {this.state.error && (
                <div className="bg-slate-700/50 rounded-lg p-4 mb-6 text-left">
                  <h3 className="text-sm font-medium text-slate-200 mb-2">Error Details:</h3>
                  <p className="text-sm text-slate-400 font-mono break-all">
                    {this.state.error.message}
                  </p>
                </div>
              )}

              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={this.handleRetry}
                  className="flex items-center justify-center space-x-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
                >
                  <RefreshCw className="h-4 w-4" />
                  <span>Retry</span>
                </button>
                
                <button
                  onClick={this.handleGoHome}
                  className="flex items-center justify-center space-x-2 px-6 py-3 bg-slate-600 hover:bg-slate-700 text-white rounded-lg transition-colors"
                >
                  <Home className="h-4 w-4" />
                  <span>Go to Dashboard</span>
                </button>
              </div>

              <div className="mt-6 pt-6 border-t border-slate-600">
                <p className="text-xs text-slate-400">
                  If this error persists, please contact the system administrator.
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
