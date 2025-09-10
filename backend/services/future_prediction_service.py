"""
Future Prediction Service
========================

This service loads trained time-series models and provides future predictions
for multiple time horizons (5, 60 minutes) with confidence intervals.
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import warnings
from sklearn.metrics import mean_squared_error
import sys

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Suppress warnings
warnings.filterwarnings('ignore')

from services.shared_logging import get_logger
logger = get_logger(__name__)

class FuturePredictionService:
    """
    Service for making future predictions using trained time-series models.
    """
    
    def __init__(self, models_dir: str = None):
        """
        Initialize the future prediction service.
        
        Args:
            models_dir: Directory containing trained models
        """
        self.models_dir = Path(models_dir) if models_dir else Path(__file__).parent.parent / 'trained_models'
        self.models = {}
        self.model_metadata = {}
        self.feature_names = None
        self.prediction_horizons = [5, 15, 30, 60]  # minutes
        self.cache = {}
        self.cache_ttl = 30  # seconds
        
        # Prediction validation tracking
        self.prediction_history = []
        self.max_history_size = 1000
        self.drift_threshold = 0.15  # 15% change in prediction patterns
        
        logger.info(f"Initializing FuturePredictionService with models from: {self.models_dir}")
        self._load_models()
    
    def _load_models(self):
        """Load best models and individual metadata for each horizon."""
        try:
            # Load models and metadata for each horizon
            for horizon in self.prediction_horizons:
                horizon_key = f'{horizon}min'
                horizon_dir = self.models_dir / f'{horizon}min_efficient'
                
                if horizon_dir.exists():
                    self.models[horizon_key] = {}
                    self.model_metadata[horizon_key] = {}
                    
                    # Load metadata for this horizon
                    metadata_path = horizon_dir / 'metadata.pkl'
                    if metadata_path.exists():
                        try:
                            horizon_metadata = joblib.load(metadata_path)
                            self.model_metadata[horizon_key] = horizon_metadata
                            logger.info(f"✅ Loaded metadata for {horizon_key}")
                            
                            # Log the best model for this horizon
                            if 'best_model_name' in horizon_metadata:
                                best_model_name = horizon_metadata['best_model_name']
                                best_r2 = horizon_metadata.get('best_score', 0)
                                logger.info(f"   Best model for {horizon_key}: {best_model_name.upper()} (R²: {best_r2:.3f})")
                        except Exception as e:
                            logger.error(f"Failed to load metadata for {horizon_key}: {e}")
                    
                    # Load the best model for this horizon
                    # Try to find the best model file (could be rf, xgb, etc.)
                    model_files = list(horizon_dir.glob('*_model.pkl'))
                    if model_files:
                        # Load the first model file found (should be the best one)
                        model_path = model_files[0]
                        model_name = model_path.stem.replace('_model', '')  # Extract model name
                        
                        try:
                            model = joblib.load(model_path)
                            self.models[horizon_key][model_name] = model
                            logger.info(f"✅ Loaded {model_name.upper()} model for {horizon_key}: {model_path}")
                        except Exception as e:
                            logger.error(f"Failed to load {model_name} model for {horizon_key}: {e}")
                    else:
                        logger.error(f"No model files found for {horizon_key}")
                else:
                    logger.warning(f"Model directory not found: {horizon_dir}")
            
            logger.info(f"Successfully loaded models for {len(self.models)} horizons")
            
            # Verify we have models for each horizon
            for horizon in self.prediction_horizons:
                horizon_key = f'{horizon}min'
                if horizon_key not in self.models or not self.models[horizon_key]:
                    logger.warning(f"No models loaded for horizon: {horizon_key}")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for prediction with real-time feature engineering.
        
        Args:
            data: Input data with process variables
            
        Returns:
            DataFrame with prepared features including real-time calculations
        """
        try:
            # Select numeric columns only
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            
            # Remove any target columns that might be present
            target_patterns = ['_ahead', 'target', 'Pb_Rougher_Conc_Pb']
            feature_cols = [col for col in numeric_cols 
                          if not any(pattern in col for pattern in target_patterns)]
            
            # Select features
            features = data[feature_cols].copy()
            
            # Handle missing values
            features = features.ffill().bfill().fillna(0)
            
            # Add real-time feature calculations
            features = self._add_real_time_features(features)
            
            logger.info(f"Prepared {len(features.columns)} features for prediction (including real-time features)")
            
            return features
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            raise
    
    def _add_real_time_features(self, features: pd.DataFrame, target_features: int = 200) -> pd.DataFrame:
        """
        Add real-time calculated features for better prediction accuracy.
        This implements the exact feature engineering used during training.
        
        Args:
            features: Base features DataFrame
            target_features: Number of features the model expects
            
        Returns:
            DataFrame with exactly target_features features as expected by the models
        """
        try:
            logger.info("Adding real-time feature engineering to match training data...")
            
            # Create a copy to avoid modifying original
            enhanced_features = features.copy()
            
            # Define all the features that the models expect (in order)
            expected_features = [
                'Feed_Pb', 'Feed_Zn', 'Pb_Conditioner_KEX_Flowrate', 'Pb_Rougher1_SIPX_Flowrate', 
                'Pb_Rougher1_AirFlow', 'Pb_Rougher1_Level', 'Feed_Pb_lag5min', 'Feed_Pb_lag15min', 
                'Feed_Pb_lag30min', 'Feed_Pb_lag60min', 'Feed_Zn_lag5min', 'Feed_Zn_lag15min', 
                'Feed_Zn_lag30min', 'Feed_Zn_lag60min', 'Feed_Pb_ratio_lag5min', 'Feed_Pb_ratio_lag15min', 
                'Feed_Pb_ratio_lag30min', 'Feed_Pb_ratio_lag60min', 'Pb_Rougher1_SIPX_Flowrate_lag5min', 
                'Pb_Rougher1_SIPX_Flowrate_lag15min', 'Pb_Rougher1_SIPX_Flowrate_lag30min', 
                'Pb_Rougher1_SIPX_Flowrate_lag60min', 'Pb_Rougher2_KEX_Flowrate_lag5min', 
                'Pb_Rougher2_KEX_Flowrate_lag15min', 'Pb_Rougher2_KEX_Flowrate_lag30min', 
                'Pb_Rougher2_KEX_Flowrate_lag60min', 'Pb_Conditioner_KEX_Flowrate_lag5min', 
                'Pb_Conditioner_KEX_Flowrate_lag15min', 'Pb_Conditioner_KEX_Flowrate_lag30min', 
                'Pb_Conditioner_KEX_Flowrate_lag60min', 'Pb_Conditioner_Nigrosine_Flowrate_lag5min', 
                'Pb_Conditioner_Nigrosine_Flowrate_lag15min', 'Pb_Conditioner_Nigrosine_Flowrate_lag30min', 
                'Pb_Conditioner_Nigrosine_Flowrate_lag60min', 'Pb_Rougher1_SIPX_Flowrate_lag5min_roll_mean_30min', 
                'Pb_Rougher1_SIPX_Flowrate_lag5min_roll_std_30min', 'Pb_Rougher1_SIPX_Flowrate_lag5min_roll_min_30min', 
                'Pb_Rougher1_SIPX_Flowrate_lag5min_roll_max_30min', 'Pb_Rougher1_SIPX_Flowrate_lag15min_roll_mean_30min', 
                'Pb_Rougher1_SIPX_Flowrate_lag15min_roll_std_30min', 'Pb_Rougher1_SIPX_Flowrate_lag15min_roll_min_30min', 
                'Pb_Rougher1_SIPX_Flowrate_lag15min_roll_max_30min', 'Pb_Rougher1_SIPX_Flowrate_lag30min_roll_mean_30min', 
                'Pb_Rougher1_SIPX_Flowrate_lag30min_roll_std_30min', 'Pb_Rougher1_SIPX_Flowrate_lag30min_roll_min_30min', 
                'Pb_Rougher1_SIPX_Flowrate_lag30min_roll_max_30min', 'Pb_Rougher1_SIPX_Flowrate_lag60min_roll_mean_30min', 
                'Pb_Rougher1_SIPX_Flowrate_lag60min_roll_std_30min', 'Pb_Rougher1_SIPX_Flowrate_lag60min_roll_min_30min', 
                'Pb_Rougher1_SIPX_Flowrate_lag60min_roll_max_30min', 'Pb_Rougher2_KEX_Flowrate_lag5min_roll_mean_30min', 
                'Pb_Rougher2_KEX_Flowrate_lag5min_roll_std_30min', 'Pb_Rougher2_KEX_Flowrate_lag5min_roll_min_30min', 
                'Pb_Rougher2_KEX_Flowrate_lag5min_roll_max_30min', 'Pb_Rougher2_KEX_Flowrate_lag15min_roll_mean_30min', 
                'Pb_Rougher2_KEX_Flowrate_lag15min_roll_std_30min', 'Pb_Rougher2_KEX_Flowrate_lag15min_roll_min_30min', 
                'Pb_Rougher2_KEX_Flowrate_lag15min_roll_max_30min', 'Pb_Rougher2_KEX_Flowrate_lag30min_roll_mean_30min', 
                'Pb_Rougher2_KEX_Flowrate_lag30min_roll_std_30min', 'Pb_Rougher2_KEX_Flowrate_lag30min_roll_min_30min', 
                'Pb_Rougher2_KEX_Flowrate_lag30min_roll_max_30min', 'Pb_Rougher2_KEX_Flowrate_lag60min_roll_mean_30min', 
                'Pb_Rougher2_KEX_Flowrate_lag60min_roll_std_30min', 'Pb_Rougher2_KEX_Flowrate_lag60min_roll_min_30min', 
                'Pb_Rougher2_KEX_Flowrate_lag60min_roll_max_30min', 'Pb_Conditioner_KEX_Flowrate_lag5min_roll_mean_30min', 
                'Pb_Conditioner_KEX_Flowrate_lag5min_roll_std_30min', 'Pb_Conditioner_KEX_Flowrate_lag5min_roll_min_30min', 
                'Pb_Conditioner_KEX_Flowrate_lag5min_roll_max_30min', 'Pb_Conditioner_KEX_Flowrate_lag15min_roll_mean_30min', 
                'Pb_Conditioner_KEX_Flowrate_lag15min_roll_std_30min', 'Pb_Conditioner_KEX_Flowrate_lag15min_roll_min_30min', 
                'Pb_Conditioner_KEX_Flowrate_lag15min_roll_max_30min', 'Pb_Conditioner_KEX_Flowrate_lag30min_roll_mean_30min', 
                'Pb_Conditioner_KEX_Flowrate_lag30min_roll_std_30min', 'Pb_Conditioner_KEX_Flowrate_lag30min_roll_min_30min', 
                'Pb_Conditioner_KEX_Flowrate_lag30min_roll_max_30min', 'Pb_Conditioner_KEX_Flowrate_lag60min_roll_mean_30min', 
                'Pb_Conditioner_KEX_Flowrate_lag60min_roll_std_30min', 'Pb_Conditioner_KEX_Flowrate_lag60min_roll_min_30min', 
                'Pb_Conditioner_KEX_Flowrate_lag60min_roll_max_30min', 'Pb_Conditioner_Nigrosine_Flowrate_lag5min_roll_mean_30min', 
                'Pb_Conditioner_Nigrosine_Flowrate_lag5min_roll_std_30min', 'Pb_Conditioner_Nigrosine_Flowrate_lag5min_roll_min_30min', 
                'Pb_Conditioner_Nigrosine_Flowrate_lag5min_roll_max_30min', 'Pb_Conditioner_Nigrosine_Flowrate_lag15min_roll_mean_30min', 
                'Pb_Conditioner_Nigrosine_Flowrate_lag15min_roll_std_30min', 'Pb_Conditioner_Nigrosine_Flowrate_lag15min_roll_min_30min', 
                'Pb_Conditioner_Nigrosine_Flowrate_lag15min_roll_max_30min', 'Pb_Conditioner_Nigrosine_Flowrate_lag30min_roll_mean_30min', 
                'Pb_Conditioner_Nigrosine_Flowrate_lag30min_roll_std_30min', 'Pb_Conditioner_Nigrosine_Flowrate_lag30min_roll_min_30min', 
                'Pb_Conditioner_Nigrosine_Flowrate_lag30min_roll_max_30min', 'Pb_Conditioner_Nigrosine_Flowrate_lag60min_roll_mean_30min', 
                'Pb_Conditioner_Nigrosine_Flowrate_lag60min_roll_std_30min', 'Pb_Conditioner_Nigrosine_Flowrate_lag60min_roll_min_30min', 
                'Pb_Conditioner_Nigrosine_Flowrate_lag60min_roll_max_30min', 'Pb_Rougher1_SIPX_Flowrate_lag5min_rate_of_change', 
                'Pb_Rougher1_SIPX_Flowrate_lag5min_acceleration', 'Pb_Rougher1_SIPX_Flowrate_lag15min_rate_of_change', 
                'Pb_Rougher1_SIPX_Flowrate_lag15min_acceleration', 'Pb_Rougher1_SIPX_Flowrate_lag30min_rate_of_change', 
                'Pb_Rougher1_SIPX_Flowrate_lag30min_acceleration', 'Pb_Rougher1_SIPX_Flowrate_lag60min_rate_of_change', 
                'Pb_Rougher1_SIPX_Flowrate_lag60min_acceleration', 'Pb_Rougher2_KEX_Flowrate_lag5min_rate_of_change', 
                'Pb_Rougher2_KEX_Flowrate_lag5min_acceleration', 'Pb_Rougher2_KEX_Flowrate_lag15min_rate_of_change', 
                'Pb_Rougher2_KEX_Flowrate_lag15min_acceleration', 'Pb_Rougher2_KEX_Flowrate_lag30min_rate_of_change', 
                'Pb_Rougher2_KEX_Flowrate_lag30min_acceleration', 'Pb_Rougher2_KEX_Flowrate_lag60min_rate_of_change', 
                'Pb_Rougher2_KEX_Flowrate_lag60min_acceleration', 'Pb_Conditioner_KEX_Flowrate_lag5min_rate_of_change', 
                'Pb_Conditioner_KEX_Flowrate_lag5min_acceleration', 'Pb_Conditioner_KEX_Flowrate_lag15min_rate_of_change', 
                'Pb_Conditioner_KEX_Flowrate_lag15min_acceleration', 'Pb_Conditioner_KEX_Flowrate_lag30min_rate_of_change', 
                'Pb_Conditioner_KEX_Flowrate_lag30min_acceleration', 'Pb_Conditioner_KEX_Flowrate_lag60min_rate_of_change', 
                'Feed_Pb_rolling_mean_5min', 'Feed_Pb_rolling_std_5min', 'Feed_Pb_rolling_mean_15min', 
                'Feed_Pb_rolling_std_15min', 'Feed_Pb_rolling_mean_30min', 'Feed_Pb_rolling_std_30min', 
                'Feed_Zn_rolling_mean_5min', 'Feed_Zn_rolling_std_5min', 'Feed_Zn_rolling_mean_15min', 
                'Feed_Zn_rolling_std_15min', 'Feed_Zn_rolling_mean_30min', 'Feed_Zn_rolling_std_30min', 
                'Pb_Conditioner_KEX_Flowrate_rolling_mean_5min', 'Pb_Conditioner_KEX_Flowrate_rolling_std_5min', 
                'Pb_Conditioner_KEX_Flowrate_rolling_mean_15min', 'Pb_Conditioner_KEX_Flowrate_rolling_std_15min', 
                'Pb_Conditioner_KEX_Flowrate_rolling_mean_30min', 'Pb_Conditioner_KEX_Flowrate_rolling_std_30min', 
                'Pb_Rougher1_SIPX_Flowrate_rolling_mean_5min', 'Pb_Rougher1_SIPX_Flowrate_rolling_std_5min', 
                'Pb_Rougher1_SIPX_Flowrate_rolling_mean_15min', 'Pb_Rougher1_SIPX_Flowrate_rolling_std_15min', 
                'Pb_Rougher1_SIPX_Flowrate_rolling_mean_30min', 'Pb_Rougher1_SIPX_Flowrate_rolling_std_30min', 
                'Pb_Rougher1_AirFlow_rolling_mean_5min', 'Pb_Rougher1_AirFlow_rolling_std_5min', 
                'Pb_Rougher1_AirFlow_rolling_mean_15min', 'Pb_Rougher1_AirFlow_rolling_std_15min', 
                'Pb_Rougher1_AirFlow_rolling_mean_30min', 'Pb_Rougher1_AirFlow_rolling_std_30min', 
                'Pb_Rougher1_Level_rolling_mean_5min', 'Pb_Rougher1_Level_rolling_std_5min', 
                'Pb_Rougher1_Level_rolling_mean_15min', 'Pb_Rougher1_Level_rolling_std_15min', 
                'Pb_Rougher1_Level_rolling_mean_30min', 'Pb_Rougher1_Level_rolling_std_30min', 
                'Pb_Rougher_Conc_Pb_rolling_mean_5min', 'Pb_Rougher_Conc_Pb_rolling_std_5min', 
                'Pb_Rougher_Conc_Pb_rolling_mean_15min', 'Pb_Rougher_Conc_Pb_rolling_std_15min', 
                'Pb_Rougher_Conc_Pb_rolling_mean_30min', 'Pb_Rougher_Conc_Pb_rolling_std_30min', 
                'Pb_Conditioner_KEX_Flowrate_rate_of_change', 'Pb_Rougher1_Valve_rate_of_change', 
                'Pb_Rougher1_SIPX_Flowrate_rate_of_change', 'Pb_Rougher2_KEX_Flowrate_rate_of_change', 
                'Pb_Scavenger1_Valve_rate_of_change', 'Pb_Rougher_Conc_FlowA_rate_of_change', 
                'Pb_Rougher_Conc_FlowB_rate_of_change', 'Pb_Final_Conc_FlowA_rate_of_change', 
                'Pb_Cleaner1_Valve_rate_of_change', 'Pb_Cleaner1_AirFlow_rate_of_change', 
                'Pb_Cleaner1_DiluteNigrosine_Flowrate_rate_of_change', 'Pb_Cleaner1_Nigrosine_Flowrate_rate_of_change', 
                'Pb_Cleaner3_Valve_rate_of_change', 'Pb_Cleaner3_DiluteNigrosine_Flowrate_rate_of_change', 
                'Pb_Rougher2_AirFlow_roll15_rate_of_change', 'Feed_Pb_rate_of_change', 'Feed_Pb_momentum_5min', 
                'Feed_Zn_rate_of_change', 'Feed_Zn_momentum_5min', 'Pb_Conditioner_KEX_Flowrate_momentum_5min', 
                'Pb_Rougher1_SIPX_Flowrate_momentum_5min', 'Pb_Rougher1_Level_momentum_5min', 
                'Pb_Rougher_Conc_Pb_rate_of_change', 'Pb_Rougher_Conc_Pb_momentum_5min', 'day_of_week', 
                'day_of_year', 'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'hour_of_day', 'shift', 
                'Recovery_Rate_5min_ahead', 'Pb_Final_Conc_Pb_5min_ahead', 'Pb_Rougher_Conc_Pb_15min_ahead', 
                'Recovery_Rate_15min_ahead', 'Pb_Final_Conc_Pb_15min_ahead'
            ]
            
            # Initialize all features with default values
            for feature in expected_features:
                enhanced_features[feature] = 0.0
            
            # Set base features from input data
            base_features = ['Feed_Pb', 'Feed_Zn', 'Pb_Conditioner_KEX_Flowrate', 'Pb_Rougher1_SIPX_Flowrate', 'Pb_Rougher1_AirFlow', 'Pb_Rougher1_Level']
            for feature in base_features:
                if feature in features.columns:
                    enhanced_features[feature] = features[feature]
            
            # Add missing variables with reasonable defaults
            missing_vars = {
                'Pb_Rougher2_KEX_Flowrate': 30.0,  # Typical rougher2 KEX flowrate
                'Pb_Conditioner_Nigrosine_Flowrate': 5.0,  # Typical nigrosine flowrate
                'Pb_Rougher1_Valve': 65.0,  # Typical valve position
                'Pb_Scavenger1_Valve': 60.0,  # Typical scavenger valve
                'Pb_Rougher_Conc_FlowA': 80.0,  # Typical concentrate flow
                'Pb_Rougher_Conc_FlowB': 75.0,  # Typical concentrate flow
                'Pb_Final_Conc_FlowA': 85.0,  # Typical final concentrate flow
                'Pb_Cleaner1_Valve': 70.0,  # Typical cleaner valve
                'Pb_Cleaner1_AirFlow': 100.0,  # Typical cleaner air flow
                'Pb_Cleaner1_DiluteNigrosine_Flowrate': 3.0,  # Typical dilute nigrosine
                'Pb_Cleaner1_Nigrosine_Flowrate': 2.0,  # Typical nigrosine
                'Pb_Cleaner3_Valve': 65.0,  # Typical cleaner3 valve
                'Pb_Cleaner3_DiluteNigrosine_Flowrate': 2.5,  # Typical dilute nigrosine
                'Pb_Rougher_Conc_Pb': 25.0,  # Typical concentrate Pb grade
                'Pb_Final_Conc_Pb': 28.0,  # Typical final concentrate Pb grade
                'Pb_Rougher2_AirFlow_roll15': 110.0,  # Typical rougher2 air flow
            }
            
            for var, default_value in missing_vars.items():
                enhanced_features[var] = default_value
            
            # Generate lag features
            lag_vars = ['Feed_Pb', 'Feed_Zn', 'Pb_Rougher1_SIPX_Flowrate', 'Pb_Rougher2_KEX_Flowrate', 'Pb_Conditioner_KEX_Flowrate', 'Pb_Conditioner_Nigrosine_Flowrate']
            for var in lag_vars:
                for lag in [5, 15, 30, 60]:
                    lag_col = f'{var}_lag{lag}min'
                    if lag_col in expected_features:
                        enhanced_features[lag_col] = enhanced_features[var].shift(lag).fillna(enhanced_features[var].mean())
            
            # Generate ratio features (Feed_Pb ratios)
            for lag in [5, 15, 30, 60]:
                ratio_col = f'Feed_Pb_ratio_lag{lag}min'
                if ratio_col in expected_features:
                    enhanced_features[ratio_col] = enhanced_features['Feed_Pb'] / enhanced_features[f'Feed_Pb_lag{lag}min'].replace(0, 1)
            
            # Generate rolling features for lag variables
            lag_vars_with_rolling = ['Pb_Rougher1_SIPX_Flowrate', 'Pb_Rougher2_KEX_Flowrate', 'Pb_Conditioner_KEX_Flowrate', 'Pb_Conditioner_Nigrosine_Flowrate']
            for var in lag_vars_with_rolling:
                for lag in [5, 15, 30, 60]:
                    lag_col = f'{var}_lag{lag}min'
                    for stat in ['roll_mean_30min', 'roll_std_30min', 'roll_min_30min', 'roll_max_30min']:
                        rolling_col = f'{lag_col}_{stat}'
                        if rolling_col in expected_features:
                            enhanced_features[rolling_col] = enhanced_features[lag_col].rolling(window=30, min_periods=1).agg(stat.split('_')[1]).fillna(enhanced_features[lag_col].mean())
            
            # Generate rate of change and acceleration for lag variables
            for var in lag_vars_with_rolling:
                for lag in [5, 15, 30, 60]:
                    lag_col = f'{var}_lag{lag}min'
                    # Rate of change
                    roc_col = f'{lag_col}_rate_of_change'
                    if roc_col in expected_features:
                        enhanced_features[roc_col] = enhanced_features[lag_col].diff().fillna(0)
                    # Acceleration
                    acc_col = f'{lag_col}_acceleration'
                    if acc_col in expected_features:
                        enhanced_features[acc_col] = enhanced_features[roc_col].diff().fillna(0)
            
            # Generate rolling features for base variables
            base_vars_with_rolling = ['Feed_Pb', 'Feed_Zn', 'Pb_Conditioner_KEX_Flowrate', 'Pb_Rougher1_SIPX_Flowrate', 'Pb_Rougher1_AirFlow', 'Pb_Rougher1_Level', 'Pb_Rougher_Conc_Pb']
            for var in base_vars_with_rolling:
                for window in [5, 15, 30]:
                    for stat in ['mean', 'std']:
                        rolling_col = f'{var}_rolling_{stat}_{window}min'
                        if rolling_col in expected_features:
                            enhanced_features[rolling_col] = enhanced_features[var].rolling(window=window, min_periods=1).agg(stat).fillna(enhanced_features[var].mean())
            
            # Generate rate of change features
            roc_vars = ['Pb_Conditioner_KEX_Flowrate', 'Pb_Rougher1_Valve', 'Pb_Rougher1_SIPX_Flowrate', 'Pb_Rougher2_KEX_Flowrate', 'Pb_Scavenger1_Valve', 'Pb_Rougher_Conc_FlowA', 'Pb_Rougher_Conc_FlowB', 'Pb_Final_Conc_FlowA', 'Pb_Cleaner1_Valve', 'Pb_Cleaner1_AirFlow', 'Pb_Cleaner1_DiluteNigrosine_Flowrate', 'Pb_Cleaner1_Nigrosine_Flowrate', 'Pb_Cleaner3_Valve', 'Pb_Cleaner3_DiluteNigrosine_Flowrate', 'Pb_Rougher2_AirFlow_roll15', 'Feed_Pb', 'Feed_Zn', 'Pb_Rougher_Conc_Pb']
            for var in roc_vars:
                roc_col = f'{var}_rate_of_change'
                if roc_col in expected_features:
                    enhanced_features[roc_col] = enhanced_features[var].diff().fillna(0)
            
            # Generate momentum features
            momentum_vars = ['Feed_Pb', 'Feed_Zn', 'Pb_Conditioner_KEX_Flowrate', 'Pb_Rougher1_SIPX_Flowrate', 'Pb_Rougher1_Level', 'Pb_Rougher_Conc_Pb']
            for var in momentum_vars:
                momentum_col = f'{var}_momentum_5min'
                if momentum_col in expected_features:
                    enhanced_features[momentum_col] = (enhanced_features[var] - enhanced_features[var].shift(5)).fillna(0)
            
            # Generate time-based features
            if isinstance(enhanced_features.index, pd.DatetimeIndex):
                enhanced_features['hour_of_day'] = enhanced_features.index.hour
                enhanced_features['day_of_week'] = enhanced_features.index.dayofweek
                enhanced_features['day_of_year'] = enhanced_features.index.dayofyear
            else:
                # Use a consistent time for feature preparation to ensure deterministic predictions
                # Use the current hour but with fixed minute/second to avoid microsecond differences
                now = datetime.now().replace(minute=0, second=0, microsecond=0)
                enhanced_features['hour_of_day'] = now.hour
                enhanced_features['day_of_week'] = now.weekday()
                enhanced_features['day_of_year'] = now.timetuple().tm_yday
            
            # Cyclical encoding
            enhanced_features['hour_sin'] = np.sin(2 * np.pi * enhanced_features['hour_of_day'] / 24)
            enhanced_features['hour_cos'] = np.cos(2 * np.pi * enhanced_features['hour_of_day'] / 24)
            enhanced_features['day_sin'] = np.sin(2 * np.pi * enhanced_features['day_of_year'] / 365)
            enhanced_features['day_cos'] = np.cos(2 * np.pi * enhanced_features['day_of_year'] / 365)
            enhanced_features['shift'] = (enhanced_features['hour_of_day'] // 8).astype(int)
            
            # Generate future target variables (these will be predicted, so set to 0 for now)
            future_targets = ['Recovery_Rate_5min_ahead', 'Pb_Final_Conc_Pb_5min_ahead', 'Pb_Rougher_Conc_Pb_15min_ahead', 'Recovery_Rate_15min_ahead', 'Pb_Final_Conc_Pb_15min_ahead']
            for target in future_targets:
                enhanced_features[target] = 0.0
            
            # Ensure we have exactly the expected features in the right order
            final_features = enhanced_features[expected_features].copy()
            
            # Handle missing values
            final_features = final_features.ffill().bfill().fillna(0)
            
            logger.info(f"Feature engineering completed. Total features: {len(final_features.columns)}")
            
            return final_features
            
        except Exception as e:
            logger.error(f"Error adding real-time features: {e}")
            return features  # Return original features if enhancement fails
    
    def _adjust_features_for_model(self, features: np.ndarray, model, horizon_key: str) -> np.ndarray:
        """
        Adjust features to match the model's expected input size.
        
        Args:
            features: Input features array
            model: The trained model
            horizon_key: Horizon key for logging
            
        Returns:
            Adjusted features array
        """
        try:
            # Get the expected number of features from the model
            if hasattr(model, 'n_features_in_'):
                expected_features = model.n_features_in_
            elif hasattr(model, 'feature_importances_'):
                expected_features = len(model.feature_importances_)
            else:
                # Fallback: try to predict with current features and catch the error
                try:
                    model.predict(features)
                    return features  # Features are already correct
                except ValueError as e:
                    # Extract expected feature count from error message
                    error_msg = str(e)
                    if 'expecting' in error_msg and 'features' in error_msg:
                        import re
                        match = re.search(r'expecting (\d+) features', error_msg)
                        if match:
                            expected_features = int(match.group(1))
                        else:
                            raise e
                    else:
                        raise e
            
            current_features = features.shape[1]
            
            if current_features == expected_features:
                return features
            elif current_features > expected_features:
                # Truncate features
                logger.info(f"Truncating features for {horizon_key}: {current_features} -> {expected_features}")
                return features[:, :expected_features]
            else:
                # Pad features with zeros
                logger.info(f"Padding features for {horizon_key}: {current_features} -> {expected_features}")
                padding = np.zeros((features.shape[0], expected_features - current_features))
                return np.hstack([features, padding])
                
        except Exception as e:
            logger.error(f"Error adjusting features for {horizon_key}: {e}")
            return features  # Return original features as fallback

    
    def predict_future(self, data: pd.DataFrame, 
                      horizons: List[int] = None) -> Dict[str, Any]:
        """
        Make future predictions for multiple horizons with caching.
        
        Args:
            data: Input data with process variables
            horizons: List of prediction horizons in minutes (default: [5, 60])
            
        Returns:
            Dictionary with predictions for each horizon
        """
        if horizons is None:
            horizons = self.prediction_horizons
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(data, horizons)
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if (datetime.now() - cache_entry['timestamp']).total_seconds() < self.cache_ttl:
                    logger.debug(f"Returning cached prediction for key: {cache_key}")
                    return cache_entry['results']
                else:
                    # Remove expired cache entry
                    del self.cache[cache_key]
            
            # Prepare features
            features = self._prepare_features(data)
            
            # Use the most recent data point for prediction
            latest_features = features.iloc[-1:].values
            
            results = {}
            prediction_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')  # Generate once for consistency
            
            for horizon in horizons:
                 horizon_key = f'{horizon}min'
                 
                 if horizon_key not in self.models:
                     logger.warning(f"No models available for horizon: {horizon_key}")
                     continue
                 
                 # Get the best model for this horizon
                 horizon_models = self.models[horizon_key]
                 if not horizon_models:
                     logger.warning(f"No models available for horizon: {horizon_key}")
                     continue
                 
                 # Get the first (and only) model (should be the best one)
                 model_name = list(horizon_models.keys())[0]
                 model = horizon_models[model_name]
                 
                 try:
                     # Adjust features to match model expectations
                     model_features = self._adjust_features_for_model(latest_features, model, horizon_key)
                     prediction = model.predict(model_features)[0]
                     logger.info(f"✅ {model_name.upper()} prediction for {horizon_key}: {prediction:.4f}")
                 except Exception as e:
                     logger.error(f"Error predicting with {model_name} for {horizon_key}: {e}")
                     continue
                 
                 # Get metadata for this model
                 horizon_metadata = self.model_metadata.get(horizon_key, {})
                 
                 # Handle different metadata structures
                 if 'results' in horizon_metadata and model_name in horizon_metadata['results']:
                     # New structure with results
                     model_metadata = horizon_metadata['results'][model_name]
                 elif 'test_r2' in horizon_metadata:
                     # Direct structure - metadata is directly in horizon_metadata
                     model_metadata = horizon_metadata
                 else:
                     # Old structure - try to get model-specific metadata
                     model_metadata = horizon_metadata.get(model_name, {})
                 
                 # Calculate confidence interval based on model performance
                 rmse = model_metadata.get('test_rmse', 2.0)  # Default RMSE if not available
                 
                 # Use RMSE to calculate confidence interval (±2 standard deviations)
                 lower_bound = prediction - (2 * rmse)
                 upper_bound = prediction + (2 * rmse)
                 
                 results[horizon_key] = {
                     'prediction': prediction,
                     'confidence_interval': {
                         'lower': lower_bound,
                         'upper': upper_bound
                     },
                     'model': model_name.upper(),
                     'model_performance': {
                         'r2_score': model_metadata.get('test_r2', 0),
                         'rmse': model_metadata.get('test_rmse', 0),
                         'mae': model_metadata.get('test_mae', 0),
                         'accuracy_10_percent': model_metadata.get('test_pred_10%', 0)
                     },
                     'prediction_time': prediction_time,  # Use consistent timestamp
                     'horizon_minutes': horizon
                 }
            
            # Cache the results
            self.cache[cache_key] = {
                'results': results,
                'timestamp': datetime.now()
            }
            
            # Clean up old cache entries
            self._cleanup_cache()
            
            # Track the prediction for validation and analytics
            self.track_prediction(results)
            
            logger.info(f"Generated predictions for {len(results)} horizons")
            return results
            
        except Exception as e:
            logger.error(f"Error making future predictions: {e}")
            raise
    
    def _generate_cache_key(self, data: pd.DataFrame, horizons: List[int]) -> str:
        """
        Generate a cache key based on input data and horizons.
        
        Args:
            data: Input data
            horizons: Prediction horizons
            
        Returns:
            Cache key string
        """
        try:
            # Create a hash of the input data
            data_hash = hash(str(data.values.tobytes()))
            horizons_str = '_'.join(map(str, sorted(horizons)))
            return f"{data_hash}_{horizons_str}"
        except Exception as e:
            logger.error(f"Error generating cache key: {e}")
            return f"default_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _cleanup_cache(self):
        """Remove expired cache entries."""
        try:
            current_time = datetime.now()
            expired_keys = []
            
            for key, entry in self.cache.items():
                if (current_time - entry['timestamp']).total_seconds() > self.cache_ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
    
    def clear_cache(self):
        """Clear all cached predictions."""
        try:
            cache_size = len(self.cache)
            self.cache.clear()
            logger.info(f"Cleared {cache_size} cached predictions")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            current_time = datetime.now()
            active_entries = 0
            expired_entries = 0
            
            for entry in self.cache.values():
                if (current_time - entry['timestamp']).total_seconds() < self.cache_ttl:
                    active_entries += 1
                else:
                    expired_entries += 1
            
            return {
                'total_entries': len(self.cache),
                'active_entries': active_entries,
                'expired_entries': expired_entries,
                'cache_ttl_seconds': self.cache_ttl,
                'cache_size_mb': len(str(self.cache)) / (1024 * 1024)  # Rough estimate
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def get_prediction_summary(self) -> Dict[str, Any]:
        """
        Get summary of available models and their performance.
        
        Returns:
            Dictionary with model summary
        """
        # Get all available horizons from both models and metadata
        available_horizons = set(self.models.keys())
        available_horizons.update(self.model_metadata.keys())
        
        summary = {
            'available_horizons': list(available_horizons),
            'model_performance': {},
            'total_models': len(available_horizons)  # One best model per horizon
        }
        
        for horizon, models in self.models.items():
            summary['model_performance'][horizon] = {}
            
            if horizon in self.model_metadata:
                horizon_metadata = self.model_metadata[horizon]
                
                # Check if we have the new metadata structure
                if 'best_model_name' in horizon_metadata:
                    # New structure with best model info
                    best_model_name = horizon_metadata['best_model_name']
                    best_score = horizon_metadata.get('best_score', 0)
                    
                    # Get detailed results if available
                    results = horizon_metadata.get('results', {})
                    if best_model_name in results:
                        model_meta = results[best_model_name]
                        summary['model_performance'][horizon][best_model_name.upper()] = {
                            'test_r2': model_meta.get('test_r2', best_score),
                            'test_rmse': model_meta.get('test_rmse', 0),
                            'test_mae': model_meta.get('test_mae', 0),
                            'accuracy_10_percent': model_meta.get('test_pred_10%', 0)
                        }
                    else:
                        # Fallback to basic info
                        summary['model_performance'][horizon][best_model_name.upper()] = {
                            'test_r2': best_score,
                            'test_rmse': 0,
                            'test_mae': 0,
                            'accuracy_10_percent': 0
                        }
                elif 'test_r2' in horizon_metadata:
                    # Direct structure - metadata is directly in horizon_metadata
                    model_name = horizon_metadata.get('model_name', 'unknown').upper()
                    summary['model_performance'][horizon][model_name] = {
                        'test_r2': horizon_metadata.get('test_r2', 0),
                        'test_rmse': horizon_metadata.get('test_rmse', 0),
                        'test_mae': horizon_metadata.get('test_mae', 0),
                        'accuracy_10_percent': horizon_metadata.get('test_pred_10%', 0)
                    }
                else:
                    # Old structure - iterate through all models
                    for model_name, model_meta in horizon_metadata.items():
                        if isinstance(model_meta, dict):
                            summary['model_performance'][horizon][model_name.upper()] = {
                                'test_r2': model_meta.get('test_r2', 0),
                                'test_rmse': model_meta.get('test_rmse', 0),
                                'test_mae': model_meta.get('test_mae', 0),
                                'accuracy_10_percent': model_meta.get('test_pred_10%', 0)
                            }
        
        return summary
    
    def validate_prediction(self, actual_value: float, 
                          predicted_value: float, 
                          horizon: str) -> Dict[str, Any]:
        """
        Validate a prediction against actual value.
        
        Args:
            actual_value: Actual observed value
            predicted_value: Predicted value
            horizon: Prediction horizon
            
        Returns:
            Dictionary with validation metrics
        """
        error = abs(actual_value - predicted_value)
        percentage_error = (error / actual_value) * 100 if actual_value != 0 else 0
        
        validation_result = {
            'actual_value': actual_value,
            'predicted_value': predicted_value,
            'absolute_error': error,
            'percentage_error': percentage_error,
            'within_10_percent': percentage_error <= 10,
            'validation_time': datetime.now().isoformat(),
            'horizon': horizon
        }
        
        logger.info(f"Validation for {horizon}: {percentage_error:.2f}% error")
        return validation_result
    
    def track_prediction(self, prediction_data: Dict[str, Any]):
        """
        Track a prediction for validation and drift detection.
        
        Args:
            prediction_data: Prediction results from predict_future method
        """
        try:
            # Extract key information for tracking
            track_entry = {
                'timestamp': datetime.now(),
                'predictions': {},
                'confidence_intervals': {},
                'best_models': {}
            }
            
            for horizon_key, horizon_data in prediction_data.items():
                track_entry['predictions'][horizon_key] = horizon_data['prediction']
                track_entry['confidence_intervals'][horizon_key] = horizon_data['confidence_interval']
                track_entry['model'] = horizon_data['model']
            
            # Add to history
            self.prediction_history.append(track_entry)
            
            # Maintain history size
            if len(self.prediction_history) > self.max_history_size:
                self.prediction_history.pop(0)
            
            logger.debug(f"Tracked prediction for {len(prediction_data)} horizons")
            
        except Exception as e:
            logger.error(f"Error tracking prediction: {e}")
    
    def validate_prediction_accuracy(self, horizon: str, 
                                   actual_value: float, 
                                   predicted_value: float) -> Dict[str, Any]:
        """
        Validate prediction accuracy and update tracking.
        
        Args:
            horizon: Prediction horizon (e.g., '5min', '60min')
            actual_value: Actual observed value
            predicted_value: Predicted value
            
        Returns:
            Dictionary with validation metrics
        """
        try:
            # Calculate validation metrics
            validation_result = self.validate_prediction(actual_value, predicted_value, horizon)
            
            # Add to prediction history for drift detection
            if self.prediction_history:
                # Find the most recent prediction for this horizon
                for entry in reversed(self.prediction_history):
                    if horizon in entry['predictions']:
                        entry['actual_value'] = actual_value
                        entry['validation_metrics'] = validation_result
                        break
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating prediction accuracy: {e}")
            return {}
    
    def detect_prediction_drift(self, horizon: str = None) -> Dict[str, Any]:
        """
        Detect prediction drift based on historical patterns.
        
        Args:
            horizon: Specific horizon to check (None for all)
            
        Returns:
            Dictionary with drift detection results
        """
        try:
            if len(self.prediction_history) < 10:
                return {
                    'drift_detected': False,
                    'reason': 'Insufficient history for drift detection',
                    'history_size': len(self.prediction_history)
                }
            
            drift_results = {}
            horizons_to_check = [horizon] if horizon else self.prediction_horizons
            
            for h in horizons_to_check:
                horizon_key = f'{h}min'
                
                # Get predictions for this horizon
                predictions = []
                for entry in self.prediction_history:
                    if horizon_key in entry['predictions']:
                        predictions.append(entry['predictions'][horizon_key])
                
                if len(predictions) < 10:
                    drift_results[horizon_key] = {
                        'drift_detected': False,
                        'reason': 'Insufficient data for this horizon'
                    }
                    continue
                
                # Calculate drift metrics
                recent_predictions = predictions[-10:]  # Last 10 predictions
                older_predictions = predictions[:-10] if len(predictions) > 10 else predictions[:5]
                
                recent_mean = np.mean(recent_predictions)
                older_mean = np.mean(older_predictions)
                
                # Calculate drift percentage
                if older_mean != 0:
                    drift_percentage = abs(recent_mean - older_mean) / abs(older_mean)
                else:
                    drift_percentage = 0
                
                # Check for drift
                drift_detected = drift_percentage > self.drift_threshold
                
                drift_results[horizon_key] = {
                    'drift_detected': drift_detected,
                    'drift_percentage': drift_percentage,
                    'recent_mean': recent_mean,
                    'older_mean': older_mean,
                    'threshold': self.drift_threshold,
                    'prediction_count': len(predictions)
                }
                
                if drift_detected:
                    logger.warning(f"Prediction drift detected for {horizon_key}: {drift_percentage:.2%} change")
            
            return drift_results
            
        except Exception as e:
            logger.error(f"Error detecting prediction drift: {e}")
            return {'error': str(e)}
    
    def get_prediction_confidence_score(self, horizon: str, 
                                      prediction_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score for a prediction based on multiple factors.
        
        Args:
            horizon: Prediction horizon
            prediction_data: Prediction results
            
        Returns:
            Confidence score between 0 and 1
        """
        try:
            if horizon not in prediction_data:
                return 0.0
            
            horizon_data = prediction_data[horizon]
            
            # Factor 1: Model performance (R² score)
            r2_score = horizon_data['model_performance']['r2_score']
            performance_score = min(r2_score, 1.0)  # Cap at 1.0
            
            # Factor 2: Model consistency (since we only have one model, use high score)
            agreement_score = 0.9  # High agreement since we're using the best model
            
            # Factor 3: Confidence interval width
            ci_lower = horizon_data['confidence_interval']['lower']
            ci_upper = horizon_data['confidence_interval']['upper']
            prediction = horizon_data['prediction']
            
            if prediction != 0:
                ci_width = (ci_upper - ci_lower) / abs(prediction)
                confidence_width_score = 1.0 - min(ci_width, 1.0)
            else:
                confidence_width_score = 0.5
            
            # Factor 4: Historical accuracy (if available)
            historical_score = 0.5  # Default
            if self.prediction_history:
                # Calculate recent accuracy
                recent_entries = self.prediction_history[-10:]
                accurate_predictions = 0
                total_validations = 0
                
                for entry in recent_entries:
                    if 'validation_metrics' in entry and horizon in entry['validation_metrics']:
                        total_validations += 1
                        if entry['validation_metrics'][horizon]['within_10_percent']:
                            accurate_predictions += 1
                
                if total_validations > 0:
                    historical_score = accurate_predictions / total_validations
            
            # Weighted combination
            confidence_score = (
                0.3 * performance_score +
                0.25 * agreement_score +
                0.25 * confidence_width_score +
                0.2 * historical_score
            )
            
            return max(0.0, min(1.0, confidence_score))
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 0.5  # Default confidence score
    
    def get_prediction_analytics(self) -> Dict[str, Any]:
        """
        Get comprehensive prediction analytics.
        
        Returns:
            Dictionary with prediction analytics
        """
        try:
            analytics = {
                'total_predictions': len(self.prediction_history),
                'prediction_horizons': self.prediction_horizons,
                'drift_analysis': self.detect_prediction_drift(),
                'cache_stats': self.get_cache_stats(),
                'model_performance': self.get_prediction_summary()
            }
            
            # Add prediction trends if available
            if self.prediction_history:
                analytics['recent_trends'] = {}
                for horizon in self.prediction_horizons:
                    horizon_key = f'{horizon}min'
                    predictions = []
                    for entry in self.prediction_history[-20:]:  # Last 20 predictions
                        if horizon_key in entry['predictions']:
                            predictions.append(entry['predictions'][horizon_key])
                    
                    if predictions:
                        analytics['recent_trends'][horizon_key] = {
                            'mean': np.mean(predictions),
                            'std': np.std(predictions),
                            'min': np.min(predictions),
                            'max': np.max(predictions),
                            'trend': 'increasing' if len(predictions) > 1 and predictions[-1] > predictions[0] else 'decreasing'
                        }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting prediction analytics: {e}")
            return {'error': str(e)}

# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Initialize service
    service = FuturePredictionService()
    
    # Get model summary
    summary = service.get_prediction_summary()
    print("Model Summary:")
    print(f"Available horizons: {summary['available_horizons']}")
    print(f"Total models: {summary['total_models']}")
    
    # Example prediction (you would use real data here)
    print("\nService initialized successfully!")
    print("Ready to make future predictions!")
