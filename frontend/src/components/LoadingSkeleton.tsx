import React from 'react';
import { motion } from 'framer-motion';

interface SkeletonProps {
  className?: string;
  height?: string;
  width?: string;
  rounded?: boolean;
}

const Skeleton: React.FC<SkeletonProps> = ({ 
  className = '', 
  height = 'h-4', 
  width = 'w-full', 
  rounded = true 
}) => {
  return (
    <motion.div
      className={`bg-slate-600 ${height} ${width} ${rounded ? 'rounded' : ''} ${className}`}
      animate={{
        opacity: [0.5, 1, 0.5],
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    />
  );
};

// Card Skeleton Component
export const CardSkeleton: React.FC = () => {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <Skeleton height="h-6" width="w-32" />
        <Skeleton height="h-8" width="w-8" rounded />
      </div>
      <div className="space-y-3">
        <Skeleton height="h-8" width="w-24" />
        <Skeleton height="h-4" width="w-16" />
        <Skeleton height="h-4" width="w-20" />
      </div>
    </div>
  );
};

// Chart Skeleton Component
export const ChartSkeleton: React.FC = () => {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <Skeleton height="h-6" width="w-48" />
        <Skeleton height="h-8" width="w-24" />
      </div>
      <div className="h-64 bg-slate-700 rounded-lg p-4">
        <div className="flex items-end justify-between h-full space-x-2">
          {Array.from({ length: 12 }).map((_, i) => (
            <Skeleton 
              key={i}
              height="h-full" 
              width="w-8" 
              className="opacity-60"
            />
          ))}
        </div>
      </div>
      <div className="mt-4 flex justify-center space-x-4">
        <Skeleton height="h-4" width="w-16" />
        <Skeleton height="h-4" width="w-16" />
        <Skeleton height="h-4" width="w-16" />
      </div>
    </div>
  );
};

// Table Skeleton Component
export const TableSkeleton: React.FC = () => {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 shadow-sm">
      <Skeleton height="h-6" width="w-32" className="mb-4" />
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex space-x-4">
            <Skeleton height="h-4" width="w-24" />
            <Skeleton height="h-4" width="w-16" />
            <Skeleton height="h-4" width="w-20" />
            <Skeleton height="h-4" width="w-12" />
          </div>
        ))}
      </div>
    </div>
  );
};

// Prediction Cards Skeleton
export const PredictionCardsSkeleton: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {Array.from({ length: 4 }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
};

// Recommendations Skeleton
export const RecommendationsSkeleton: React.FC = () => {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 shadow-sm">
      <Skeleton height="h-6" width="w-48" className="mb-6" />
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="bg-slate-700 rounded-lg p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3">
                <Skeleton height="h-6" width="w-6" rounded />
                <Skeleton height="h-5" width="w-40" />
              </div>
              <Skeleton height="h-6" width="w-16" />
            </div>
            <Skeleton height="h-4" width="w-full" className="mb-2" />
            <Skeleton height="h-4" width="w-3/4" className="mb-4" />
            <div className="flex space-x-2">
              <Skeleton height="h-8" width="w-24" />
              <Skeleton height="h-8" width="w-20" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Skeleton;
