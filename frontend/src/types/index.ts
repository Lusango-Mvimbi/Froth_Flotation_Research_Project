// Flotation Data Types
export interface FlotationData {
  timestamp: string;
  Pb_Concentrate: number;
  Pb_Recovery: number;
  pH: number;
  Pb_Rougher1_AirFlow: number;
  Pb_Conditioner_KEX_Flowrate: number;
  Pb_Rougher1_SIPX_Flowrate: number;
  Feed_Pb: number;
  Impeller_Speed: number;
  Temperature?: number;
  Pulp_Density?: number;
  Pb_Conditioner_Nigrosine_Flowrate_Min?: number;
  Pb_Conditioner_Nigrosine_Flowrate_Max?: number;
  Cell_Level?: number;
  Froth_Height?: number;
  timestamp_display?: string;
  // ML Model fields
  Model_Confidence?: number;
  Process_Status?: string;
  Pb_Concentrate_Status?: 'critical' | 'optimal' | 'warning';
  Recovery_Status?: 'critical' | 'optimal' | 'warning';
  Recommendations?: string[];
  Feed_Zn?: number;
}

export interface ProcessControls {
  kex: number;
  sipx: number;
  feed_grade: number;
  impeller_speed: number;
  air: number;
  ph: number;
}

export interface Prediction {
  predicted_pb: number;
  recovery_efficiency: number;
  confidence: number;
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
  kex: { min: number; max: number };
  sipx: { min: number; max: number };
  feed_grade: { min: number; max: number };
  impeller_speed: { min: number; max: number };
  air: { min: number; max: number };
  ph: { min: number; max: number };
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
  loading: boolean;
  error: string | null;
  serverConnected: boolean;
}
