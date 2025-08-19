import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import { useAuth } from './hooks/useAuthRefactored';
import './index.css';

// Authentication wrapper component
const AuthWrapper: React.FC = () => {
  const { isAuthenticated, loading, debugSetAuth } = useAuth();
  
  console.log('🔍 AuthWrapper render:', {
    isAuthenticated,
    loading,
    currentPath: window.location.pathname,
    localStorageToken: localStorage.getItem('authToken') ? 'present' : 'missing',
    localStorageUser: localStorage.getItem('userData') ? 'present' : 'missing'
  });

  // Show loading spinner while checking authentication
  if (loading) {
    console.log('⏳ AuthWrapper: Showing loading spinner');
    return (
      <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-700 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mb-4"></div>
          <p className="text-dark-300">Initializing...</p>
        </div>
      </div>
    );
  }

  console.log('🎯 AuthWrapper: Rendering routes with auth state:', { isAuthenticated });

  // Debug function to check authentication state
  const debugAuth = () => {
    console.log('🔍 Debug Authentication State:');
    console.log('- isAuthenticated:', isAuthenticated);
    console.log('- loading:', loading);
    console.log('- localStorage authToken:', localStorage.getItem('authToken'));
    console.log('- localStorage userData:', localStorage.getItem('userData'));
    console.log('- current path:', window.location.pathname);
  };

  return (
    <Routes>
      <Route 
        path="/login" 
        element={
          isAuthenticated ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <Login />
          )
        } 
      />
      <Route 
        path="/dashboard" 
        element={
          isAuthenticated ? (
            <Dashboard />
          ) : (
            <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-700 flex items-center justify-center">
                           <div className="text-center">
               <h1 className="text-2xl font-bold text-white mb-4">Authentication Required</h1>
               <p className="text-dark-300 mb-6">Please log in to access the dashboard</p>
               <div className="space-y-4">
                 <a 
                   href="/login" 
                   className="btn-primary px-6 py-3 text-lg font-semibold block"
                 >
                   Go to Login
                 </a>
                 <button 
                   onClick={debugAuth}
                   className="btn-secondary px-6 py-3 text-lg font-semibold block"
                 >
                   Debug Auth State
                 </button>
                 <button 
                   onClick={() => debugSetAuth?.(true)}
                   className="btn-secondary px-4 py-2 text-sm font-semibold block"
                 >
                   Force Authenticated
                 </button>
               </div>
             </div>
            </div>
          )
        } 
      />
      <Route 
        path="/" 
        element={
          isAuthenticated ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <Navigate to="/login" replace />
          )
        } 
      />
      <Route 
        path="*" 
        element={
          isAuthenticated ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <Navigate to="/login" replace />
          )
        } 
      />
    </Routes>
  );
};

const App: React.FC = () => {
  console.log('🚀 App component rendering');
  
  return (
    <Router
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}
    >
      <div className="App">
        <AuthWrapper />
        
        {/* Toast notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1e293b',
              color: '#e2e8f0',
              border: '1px solid #475569',
            },
            success: {
              iconTheme: {
                primary: '#22c55e',
                secondary: '#e2e8f0',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#e2e8f0',
              },
            },
          }}
        />
      </div>
    </Router>
  );
};

export default App;
