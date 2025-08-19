import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Eye, EyeOff, User, Lock, Activity, AlertCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuthRefactored';

const Login: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const { login, error: authError, isAuthenticated, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  console.log('🔍 Login component render:', {
    isAuthenticated,
    authLoading,
    isLoading
  });

  // Redirect to dashboard if already authenticated (only on initial load)
  useEffect(() => {
    console.log('🔄 Login useEffect triggered:', { isAuthenticated, authLoading });
    
    if (isAuthenticated && !authLoading) {
      console.log('✅ User already authenticated, redirecting to dashboard');
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, authLoading, navigate]); // Include all dependencies

  // Show loading spinner while checking authentication
  if (authLoading) {
    console.log('⏳ Showing auth loading spinner');
    return (
      <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-700 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mb-4"></div>
          <p className="text-dark-300">Checking authentication...</p>
        </div>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.username || !formData.password) {
      toast.error('Please fill in all fields');
      return;
    }

    console.log('🚀 Form submitted, starting login process');
    setIsLoading(true);
    
    try {
      const result = await login({ username: formData.username, password: formData.password });
      console.log('📋 Login result:', result);
      
      if (result.success) {
        console.log('✅ Login successful, showing success toast');
        toast.success('Login successful!');
        // Use React Router navigation instead of page refresh
        console.log('🔄 Navigating to dashboard using React Router');
        navigate('/dashboard', { replace: true });
      } else {
        console.log('❌ Login failed:', result.error);
        toast.error(result.error || 'Login failed');
      }
    } catch (error) {
      console.error('💥 Unexpected error during login:', error);
      toast.error('An unexpected error occurred');
    } finally {
      console.log('🏁 Login process completed, setting loading to false');
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-700 flex items-center justify-center p-2 sm:p-4 lg:p-6">
      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-primary-400 rounded-full animate-pulse"></div>
        <div className="absolute top-3/4 right-1/4 w-1 h-1 bg-primary-300 rounded-full animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 w-3 h-3 bg-primary-500 rounded-full animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="relative z-10 w-full max-w-xs sm:max-w-sm md:max-w-md lg:max-w-lg xl:max-w-xl"
      >
        {/* Login Card */}
        <div className="glass rounded-2xl p-3 sm:p-4 md:p-6 lg:p-8 shadow-2xl">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-center mb-4 sm:mb-6 lg:mb-8"
          >
            <div className="flex justify-center mb-2 sm:mb-3 lg:mb-4">
              <div className="p-1.5 sm:p-2 lg:p-3 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl">
                <Activity className="h-5 w-5 sm:h-6 sm:w-6 lg:h-8 lg:w-8 text-white" />
              </div>
            </div>
            <h1 className="text-lg sm:text-xl md:text-2xl lg:text-3xl font-bold gradient-text mb-1 sm:mb-2">
              Froth Flotation Digital Twin
            </h1>
            <p className="text-dark-300 text-xs sm:text-sm lg:text-base">
              Industrial Process Monitoring Dashboard
            </p>
          </motion.div>

          {/* Error Message */}
          {authError && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mb-4 sm:mb-6 p-3 sm:p-4 bg-danger-900/20 border border-danger-700 rounded-lg flex items-center space-x-2"
            >
              <AlertCircle className="h-4 w-4 sm:h-5 sm:w-5 text-danger-400 flex-shrink-0" />
              <span className="text-danger-400 text-xs sm:text-sm">{authError}</span>
            </motion.div>
          )}

          {/* Login Form */}
          <motion.form
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            onSubmit={handleSubmit}
            className="space-y-3 sm:space-y-4 lg:space-y-6"
          >
            {/* Username Field */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-dark-200 mb-2">
                Username
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-4 w-4 sm:h-5 sm:w-5 text-dark-400" />
                </div>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="input-field w-full pl-8 sm:pl-10 text-sm sm:text-base"
                  placeholder="Enter your username"
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-dark-200 mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-4 w-4 sm:h-5 sm:w-5 text-dark-400" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="input-field w-full pl-8 sm:pl-10 pr-8 sm:pr-10 text-sm sm:text-base"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4 sm:h-5 sm:w-5 text-dark-400 hover:text-dark-300" />
                  ) : (
                    <Eye className="h-4 w-4 sm:h-5 sm:w-5 text-dark-400 hover:text-dark-300" />
                  )}
                </button>
              </div>
            </div>

            {/* Login Button */}
            <motion.button
              type="submit"
              disabled={isLoading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="btn-primary w-full py-2 sm:py-2.5 lg:py-3 text-sm sm:text-base lg:text-lg font-semibold relative overflow-hidden"
            >
              {isLoading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="spinner"></div>
                  <span>Signing In...</span>
                </div>
              ) : (
                'Sign In to Dashboard'
              )}
            </motion.button>
          </motion.form>


        </div>
      </motion.div>
    </div>
  );
};

export default Login;
