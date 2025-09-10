/**
 * Frontend Interfaces following SOLID Principles
 * =============================================
 * 
 * This module defines interfaces for the React frontend components
 * and services, ensuring proper separation of concerns and testability.
 */

// ============================================================================
// AUTHENTICATION INTERFACES
// ============================================================================

export interface IUser {
  id: number;
  username: string;
  full_name: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface ILoginCredentials {
  username: string;
  password: string;
}

export interface ILoginResponse {
  success: boolean;
  message: string;
  token?: string;
  user?: IUser;
  status_code: number;
  error?: string;
}

export interface IAuthService {
  login(credentials: ILoginCredentials): Promise<ILoginResponse>;
  logout(): Promise<boolean>;
  verifyToken(token: string): Promise<boolean>;
  getCurrentUser(): IUser | null;
  isAuthenticated(): boolean;
}

export interface IAuthContext {
  user: IUser | null;
  isAuthenticated: boolean;
  login: (credentials: ILoginCredentials) => Promise<ILoginResponse>;
  logout: () => Promise<void>;
  loading: boolean;
  error?: string;
  debugSetAuth?: (auth: boolean) => void;
}

// ============================================================================
// API SERVICE INTERFACES
// ============================================================================

export interface IApiService {
  get<T>(endpoint: string): Promise<T>;
  post<T>(endpoint: string, data: any): Promise<T>;
  put<T>(endpoint: string, data: any): Promise<T>;
  delete<T>(endpoint: string): Promise<T>;
  setAuthToken(token: string): void;
  removeAuthToken(): void;
}

export interface IWebSocketService {
  connect(url: string): Promise<void>;
  disconnect(): void;
  send(message: any): void;
  onMessage(callback: (data: any) => void): void;
  onConnect(callback: () => void): void;
  onDisconnect(callback: () => void): void;
  isConnected(): boolean;
}

// ============================================================================
// DATA INTERFACES
// ============================================================================

export interface IFloationData {
  timestamp: string;
  pH: number;
  Temperature: number;
  Pulp_Density: number;
  Feed_Pb: number;
  Feed_Zn: number;
  Pb_Conditioner_KEX_Flowrate: number;
  Pb_Rougher1_SIPX_Flowrate: number;
  Pb_Rougher1_AirFlow: number;
  Pb_Rougher1_Level: number;
  Impeller_Speed: number;
  Froth_Height: number;
  pb_concentrate: number;
  recovery_rate: number;
  process_status: 'optimal' | 'warning' | 'critical' | 'error';
  recommendations: string[];
  model_info: IModelInfo;
}

export interface IModelInfo {
  model_name: string;
  model_type: string;
  test_r2: number;
  test_rmse: number;
  test_mae: number;
  test_pred_10_percent: number;
  training_date: string;
  status: string;
}

export interface IParameterRanges {
  [key: string]: [number, number];
}

export interface IDataService {
  getCurrentData(): Promise<IFloationData>;
  getParameterRanges(): Promise<IParameterRanges>;
  validateParameters(parameters: Record<string, number>): Promise<boolean>;
  subscribeToRealTimeData(callback: (data: IFloationData) => void): () => void;
}

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

export interface IComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface IChartData {
  labels: string[];
  datasets: IChartDataset[];
}

export interface IChartDataset {
  label: string;
  data: number[];
  borderColor: string;
  backgroundColor: string;
  tension: number;
}

export interface IChartService {
  createLineChartData(data: IFloationData[], parameter: string): IChartData;
  createMultiParameterChart(data: IFloationData[], parameters: string[]): IChartData;
  getChartOptions(title: string): any;
}

// ============================================================================
// STORAGE INTERFACES
// ============================================================================

export interface IStorageService {
  get<T>(key: string): T | null;
  set<T>(key: string, value: T): void;
  remove(key: string): void;
  clear(): void;
}

// ============================================================================
// VALIDATION INTERFACES
// ============================================================================

export interface IValidationRule {
  validate(value: any): boolean;
  message: string;
}

export interface IValidator {
  addRule(rule: IValidationRule): void;
  validate(data: any): IValidationResult;
}

export interface IValidationResult {
  isValid: boolean;
  errors: string[];
}

// ============================================================================
// EVENT INTERFACES
// ============================================================================

export interface IEventEmitter {
  on(event: string, callback: (...args: any[]) => void): void;
  off(event: string, callback: (...args: any[]) => void): void;
  emit(event: string, ...args: any[]): void;
}

// ============================================================================
// CONFIGURATION INTERFACES
// ============================================================================

export interface IAppConfig {
  apiBaseUrl: string;
  wsUrl: string;
  authUrl: string;
  refreshInterval: number;
  maxDataPoints: number;
  chartColors: string[];
}

export interface IConfigService {
  getConfig(): IAppConfig;
  updateConfig(config: Partial<IAppConfig>): void;
}

// ============================================================================
// LOGGING INTERFACES
// ============================================================================

export interface ILogger {
  info(message: string, data?: any): void;
  warn(message: string, data?: any): void;
  error(message: string, error?: Error): void;
  debug(message: string, data?: any): void;
}

// ============================================================================
// UTILITY INTERFACES
// ============================================================================

export interface IFormatter {
  formatNumber(value: number, decimals?: number): string;
  formatPercentage(value: number): string;
  formatDateTime(date: string | Date): string;
  formatStatus(status: string): string;
}

export interface IColorService {
  getStatusColor(status: string): string;
  getParameterColor(parameter: string): string;
  getGradientColors(baseColor: string, steps: number): string[];
}
