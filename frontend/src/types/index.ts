// Flotation Data Types - ONLY parameters from training data
export interface FlotationData {
  timestamp: string;
  // ONLY parameters that were actually in the training data
  Feed_Pb: number;
  Feed_Zn: number;
  Pb_Conditioner_KEX_Flowrate: number;
  Pb_Rougher1_SIPX_Flowrate: number;
  Pb_Rougher1_AirFlow: number;
  Pb_Rougher1_Level: number;
  // ML predictions and calculated values
  Pb_Concentrate: number;  // Legacy - same as Predicted_Pb_Concentrate
  Pb_Recovery: number;     // Legacy - same as Predicted_Pb_Recovery
  // New predicted and actual values
  Predicted_Pb_Concentrate?: number;
  Predicted_Pb_Recovery?: number;
  Actual_Pb_Concentrate?: number;
  Actual_Pb_Recovery?: number;
  Process_Status?: string;
  Pb_Concentrate_Status?: 'critical' | 'optimal' | 'warning';
  Recovery_Status?: 'critical' | 'optimal' | 'warning';
  Recommendations?: string[];
  optimization_recommendations?: string[];
  timestamp_display?: string;
}

export interface ProcessControls {
  kex: number;
  sipx: number;
}

export interface Prediction {
  predicted_pb: number;
  recovery_efficiency: number;
  status: string;
  prediction_method: 'ML Model' | 'Engineering-Based';
}

export interface Recommendation {
  id: string;
  type: 'danger' | 'warning' | 'success' | 'info';
  message: string;
  parameter?: string;
  current_value?: number;
  optimal_range?: string;
  timestamp: string;
}

export interface PerformanceState {
  state: 'below_min' | 'within_range' | 'above_max';
  color: string;
  backgroundColor: string;
}

export interface OptimalRanges {
  kex: { 
    min: number; 
    max: number; 
    optimal: number; 
    optimal_min: number; 
    optimal_max: number; 
    unit: string; 
    description: string 
  };
  sipx: { 
    min: number; 
    max: number; 
    optimal: number; 
    optimal_min: number; 
    optimal_max: number; 
    unit: string; 
    description: string 
  };
}

export interface TargetRanges {
  pb_concentrate: {
    min: number;
    max: number;
    optimal: number;
    unit: string;
  };
  recovery: {
    min: number;
    max: number;
    optimal: number;
    unit: string;
  };
  feed_grade: {
    min: number;
    max: number;
    optimal: number;
    unit: string;
  };
  status: {
    good: string[];
    warning: string[];
    critical: string[];
  };
}

export interface User {
  id: number;
  username: string;
  full_name?: string;
  role: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
  error: string | null;
}

export interface DashboardState {
  data: FlotationData[];
  currentData: FlotationData | null;
  controls: ProcessControls;
  predictions: Prediction | null;
  recommendations: Recommendation[];
  optimalRanges: OptimalRanges | null;
  targetRanges: TargetRanges | null;
  loading: boolean;
  error: string | null;
  serverConnected: boolean;
}
