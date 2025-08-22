import React, { useState, useCallback, useRef } from 'react';
import { motion } from 'framer-motion';
import { 
  Settings, 
  Droplets, 
  TrendingUp,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';
import { ProcessControls, OptimalRanges } from '../types';

interface ControlPanelProps {
  controls: ProcessControls;
  optimalRanges: OptimalRanges | null;
  onControlChange: (controls: ProcessControls) => void;
}

const ControlPanel: React.FC<ControlPanelProps> = ({ 
  controls, 
  optimalRanges, 
  onControlChange 
}) => {
  const [localControls, setLocalControls] = useState<ProcessControls>(controls);
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Only sync local controls with backend controls on initial load
  React.useEffect(() => {
    setLocalControls(controls);
  }, []); // Empty dependency array - only run once on mount

  // Cleanup timeout on unmount
  React.useEffect(() => {
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, []);

  // Get performance status for a control
  const getControlStatus = (value: number, min: number, max: number) => {
    if (value < min) return { status: 'below', color: 'text-danger-400', bgColor: 'bg-danger-900/20' };
    if (value > max) return { status: 'above', color: 'text-warning-400', bgColor: 'bg-warning-900/20' };
    return { status: 'optimal', color: 'text-success-400', bgColor: 'bg-success-900/20' };
  };

  // Handle slider change with debouncing
  const handleSliderChange = useCallback((key: keyof ProcessControls, value: number) => {
    const newControls = { ...localControls, [key]: value };
    setLocalControls(newControls);
    
    // Clear existing timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }
    
    // Set new timeout to debounce the API call
    debounceTimeoutRef.current = setTimeout(() => {
      onControlChange(newControls);
    }, 500); // 500ms delay
  }, [localControls, onControlChange]);

  const controlConfigs = [
    {
      key: 'kex' as keyof ProcessControls,
      label: 'KEX Flow Rate',
      unit: 'L/min',
      icon: Droplets,
      min: 0,  // Realistic range
      max: 100,  // Realistic maximum for KEX
      optimal: optimalRanges?.kex?.optimal || 45,
      step: 0.5,
      description: 'Collector reagent flow rate'
    },
    {
      key: 'sipx' as keyof ProcessControls,
      label: 'SIPX Flow Rate',
      unit: 'L/min',
      icon: Droplets,
      min: 0,  // Realistic range
      max: 60,  // Realistic maximum for SIPX
      optimal: optimalRanges?.sipx?.optimal || 25,
      step: 0.5,
      description: 'Frother reagent flow rate'
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="glass rounded-xl p-4 sm:p-6 h-full overflow-y-auto"
    >
      {/* Header */}
      <div className="flex items-center space-x-3 mb-4 sm:mb-6">
        <div className="p-2 bg-primary-600 rounded-lg">
          <Settings className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
        </div>
        <div>
          <h2 className="text-lg sm:text-xl font-bold text-white">Reagent Controls</h2>
          <p className="text-xs sm:text-sm text-dark-300">Adjust reagent flow rates</p>
        </div>
      </div>

      {/* Controls */}
      <div className="space-y-4 sm:space-y-6">
        {controlConfigs.map((config) => {
          const value = localControls[config.key];
          const optimalRange = optimalRanges?.[config.key];
          const status = optimalRange 
            ? getControlStatus(value, optimalRange.optimal_min || optimalRange.min, optimalRange.optimal_max || optimalRange.max)  // Use optimal ranges from backend
            : { status: 'unknown', color: 'text-dark-400', bgColor: 'bg-dark-700/20' };

          return (
            <motion.div
              key={config.key}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`p-3 sm:p-4 rounded-lg border transition-all duration-300 ${status.bgColor} border-dark-600`}
            >
              {/* Control Header */}
              <div className="flex items-center justify-between mb-2 sm:mb-3">
                <div className="flex items-center space-x-2 min-w-0">
                  <config.icon className={`h-3 w-3 sm:h-4 sm:w-4 ${status.color} flex-shrink-0`} />
                  <div className="min-w-0">
                    <h3 className="text-xs sm:text-sm font-semibold text-white truncate">{config.label}</h3>
                    <p className="text-xs text-dark-400 hidden sm:block">{config.description}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-1 flex-shrink-0">
                  {status.status === 'optimal' && <CheckCircle className="h-3 w-3 sm:h-4 sm:w-4 text-success-400" />}
                  {status.status === 'below' && <AlertTriangle className="h-3 w-3 sm:h-4 sm:w-4 text-danger-400" />}
                  {status.status === 'above' && <AlertTriangle className="h-3 w-3 sm:h-4 sm:w-4 text-warning-400" />}
                </div>
              </div>

                             {/* Current Value */}
               <div className="flex items-center justify-between mb-2">
                 <span className="text-base sm:text-lg font-bold text-white">
                   {value.toFixed(1)}
                 </span>
                 <span className="text-xs sm:text-sm text-dark-300">{config.unit}</span>
               </div>

              {/* Slider */}
              <div className="mb-3">
                <input
                  type="range"
                  min={config.min}
                  max={config.max}
                  step={config.step}
                  value={value}
                  onChange={(e) => handleSliderChange(config.key, parseFloat(e.target.value))}
                  className="w-full h-2 bg-dark-600 rounded-lg appearance-none cursor-pointer slider-track"
                  style={{
                    background: `linear-gradient(to right, ${status.color.replace('text-', '')} 0%, ${status.color.replace('text-', '')} ${((value - config.min) / (config.max - config.min)) * 100}%, #475569 ${((value - config.min) / (config.max - config.min)) * 100}%, #475569 100%)`
                  }}
                />
              </div>

              {/* Range Info */}
              <div className="flex items-center justify-between text-xs">
                <span className="text-dark-400">Min: {config.min}</span>
                {optimalRange && (
                  <span className={`font-medium ${status.color} hidden sm:inline`}>
                    Optimal: {optimalRange.optimal_min || optimalRange.min}-{optimalRange.optimal_max || optimalRange.max}
                  </span>
                )}
                <span className="text-dark-400">Max: {config.max}</span>
              </div>

              {/* Status Indicator */}
              <div className="mt-2 flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${status.color.replace('text-', 'bg-')}`} />
                <span className={`text-xs font-medium capitalize ${status.color}`}>
                  {status.status === 'optimal' ? 'Optimal Range' : 
                   status.status === 'below' ? 'Below Optimal' : 
                   status.status === 'above' ? 'Above Optimal' : 'Unknown'}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Summary */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="mt-4 sm:mt-6 p-3 sm:p-4 bg-dark-700/50 rounded-lg border border-dark-600"
      >
        <div className="flex items-center space-x-2 mb-2">
          <TrendingUp className="h-3 w-3 sm:h-4 sm:w-4 text-primary-400" />
          <h4 className="text-xs sm:text-sm font-semibold text-white">Control Summary</h4>
        </div>
        <p className="text-xs text-dark-300">
          Adjust sliders to optimize process performance. Green indicators show optimal ranges.
        </p>
      </motion.div>
    </motion.div>
  );
};

export default ControlPanel;
