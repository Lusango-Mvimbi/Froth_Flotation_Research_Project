import React, { useState, useEffect } from 'react';
import {
  Settings
} from 'lucide-react';
import Dashboard from './Dashboard';
import ControlPanel from './ControlPanel';
import { flotationAPI } from '../services/api';
import { ProcessControls, OptimalRanges } from '../types';
import { useError } from '../contexts/ErrorContext';

interface TabbedDashboardProps {
  className?: string;
}

const TabbedDashboard: React.FC<TabbedDashboardProps> = ({ className = '' }) => {
  const [controls, setControls] = useState<ProcessControls>({ kex: 0, sipx: 0 });
  const [optimalRanges, setOptimalRanges] = useState<OptimalRanges | null>(null);
  const [loading, setLoading] = useState(true);
  const { addError } = useError();

  // Fetch initial control settings and optimal ranges
  useEffect(() => {
    const initializeControls = async () => {
      try {
        setLoading(true);
        
        // Fetch current control settings
        const currentControls = await flotationAPI.getControlSettings();
        setControls(currentControls);
        
        // Fetch optimal ranges
        const ranges = await flotationAPI.getOptimalRanges();
        setOptimalRanges(ranges);
        
      } catch (error) {
        console.error('Failed to initialize controls:', error);
        addError({
          type: 'data',
          message: 'Failed to load control settings',
          recoverable: true,
          suggestions: [
            'Check if the backend server is running',
            'Try refreshing the page',
            'Contact the system administrator'
          ]
        });
      } finally {
        setLoading(false);
      }
    };

    initializeControls();
  }, [addError]);

  // Add periodic refresh to keep controls in sync
  useEffect(() => {
    const interval = setInterval(() => {
      refreshControls();
    }, 10000); // Refresh every 10 seconds

    return () => clearInterval(interval);
  }, []);

  const handleControlChange = async (newControls: ProcessControls) => {
    try {
      await flotationAPI.updateControls(newControls);
      setControls(newControls);
      
      // Refresh control settings from backend to ensure sync
      setTimeout(async () => {
        try {
          const updatedControls = await flotationAPI.getControlSettings();
          setControls(updatedControls);
        } catch (error) {
          console.warn('Failed to refresh controls after update:', error);
        }
      }, 1000);
    } catch (error) {
      console.error('Failed to update controls:', error);
      addError({
        type: 'data',
        message: 'Failed to update control settings',
        recoverable: true,
        suggestions: [
          'Check your connection',
          'Try again in a moment',
          'Contact the system administrator'
        ]
      });
    }
  };

  // Add a refresh function to sync with backend
  const refreshControls = async () => {
    try {
      const currentControls = await flotationAPI.getControlSettings();
      setControls(currentControls);
    } catch (error) {
      console.warn('Failed to refresh controls:', error);
    }
  };

  return (
    <div className={`bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700 min-h-screen ${className}`}>
      {/* Main Content with Sidebar */}
      <div className="flex h-screen">
        {/* Left Sidebar - Controls */}
        <div className="w-80 bg-slate-800 border-r border-slate-600 flex-shrink-0">
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-bold text-white">Reagent Controls</h3>
              </div>
              <button
                onClick={refreshControls}
                className="p-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
                title="Refresh controls from backend"
              >
                <Settings className="h-4 w-4" />
              </button>
            </div>
            
            {loading ? (
              <div className="space-y-4">
                <div className="h-4 bg-slate-700 rounded animate-pulse"></div>
                <div className="h-4 bg-slate-700 rounded animate-pulse"></div>
                <div className="h-4 bg-slate-700 rounded animate-pulse"></div>
              </div>
            ) : (
              <ControlPanel
                controls={controls}
                optimalRanges={optimalRanges}
                onControlChange={handleControlChange}
              />
            )}
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 overflow-y-auto">
          <Dashboard 
            controls={controls}
            onControlChange={handleControlChange}
          />
        </div>
      </div>
    </div>
  );
};

export default TabbedDashboard;
