import React from 'react';
import { motion } from 'framer-motion';
import { Wifi, WifiOff, Activity } from 'lucide-react';

interface ConnectionStatusProps {
  connected: boolean;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ connected }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`flex items-center space-x-1 sm:space-x-2 px-2 sm:px-3 py-1 sm:py-2 rounded-lg transition-all duration-300 text-xs sm:text-sm ${
        connected 
          ? 'bg-success-900/20 border border-success-700 text-success-400' 
          : 'bg-danger-900/20 border border-danger-700 text-danger-400'
      }`}
    >
      {connected ? (
        <>
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <Wifi className="h-3 w-3 sm:h-4 sm:w-4" />
          </motion.div>
          <span className="font-medium hidden sm:inline">Connected</span>
        </>
      ) : (
        <>
          <WifiOff className="h-3 w-3 sm:h-4 sm:w-4" />
          <span className="font-medium hidden sm:inline">Disconnected</span>
        </>
      )}
    </motion.div>
  );
};

export default ConnectionStatus;
