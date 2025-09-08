"""
Time-Series Preprocessor for Future Prediction
============================================

This module prepares the cleaned flotation data for time-series prediction training.
It creates future target variables and structures data for predicting outcomes
5, 15, 30, and 60 minutes ahead.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import warnings
from datetime import datetime, timedelta
import joblib
import os

# Suppress warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class TimeSeriesPreprocessor:
    """
    Preprocesses flotation data for time-series prediction training.
    Creates future target variables and prepares features for ML models.
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize the time-series preprocessor.
        
        Args:
            data_path: Path to the cleaned data file
        """
        self.data_path = data_path or r"C:\@Python Projects\TUT Research Project\Clean_Data\HZL_RA4_Pb_Rougher_enhanced_clean.parquet"
        self.raw_data = None
        self.processed_data = None
        self.feature_columns = []
        self.target_columns = []
        self.prediction_horizons = [5, 15, 30, 60]  # minutes ahead
        
        # Key variables for prediction
        self.key_input_vars = [
            'Feed_Pb', 'Feed_Zn',
            'Pb_Conditioner_KEX_Flowrate', 'Pb_Rougher1_SIPX_Flowrate',
            'Pb_Rougher1_AirFlow', 'Pb_Rougher1_Level'
        ]
        
        self.key_target_vars = [
            'Pb_Rougher_Conc_Pb', 'Pb_Final_Conc_Pb'
        ]
        
        logger.info("TimeSeriesPreprocessor initialized")
    
    def load_data(self) -> pd.DataFrame:
        """
        Load the cleaned flotation data.
        
        Returns:
            DataFrame with the loaded data
        """
        try:
            logger.info(f"Loading data from: {self.data_path}")
            
            if not os.path.exists(self.data_path):
                raise FileNotFoundError(f"Data file not found: {self.data_path}")
            
            # Load the parquet file
            self.raw_data = pd.read_parquet(self.data_path)
            
            # Ensure index is datetime
            if not isinstance(self.raw_data.index, pd.DatetimeIndex):
                self.raw_data.index = pd.to_datetime(self.raw_data.index)
            
            # Sort by timestamp
            self.raw_data = self.raw_data.sort_index()
            
            logger.info(f"Data loaded successfully. Shape: {self.raw_data.shape}")
            logger.info(f"Time range: {self.raw_data.index.min()} to {self.raw_data.index.max()}")
            
            return self.raw_data
            
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise
    
    def create_future_targets(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create future target variables for different prediction horizons.
        
        Args:
            df: Input DataFrame with current data
            
        Returns:
            DataFrame with future target variables added
        """
        logger.info("Creating future target variables...")
        
        df_future = df.copy()
        
        # Create future targets for each horizon
        for horizon in self.prediction_horizons:
            logger.info(f"Creating {horizon}-minute ahead predictions...")
            
            for target_var in self.key_target_vars:
                if target_var in df.columns:
                    future_col = f"{target_var}_{horizon}min_ahead"
                    
                    # Shift the target variable forward by the horizon
                    df_future[future_col] = df[target_var].shift(-horizon)
                    
                    # Also create recovery rate predictions
                    if 'Pb' in target_var and 'Conc' in target_var:
                        # Calculate recovery rate: Recovery = 100 * (c/f) * (f-t)/(c-t)
                        # Where c=concentrate, f=feed, t=tailings
                        feed_pb = df['Feed_Pb']
                        concentrate_pb = df[target_var]
                        
                        # Estimate tailings (typically 30% of feed grade)
                        tailings_pb = feed_pb * 0.3
                        
                        # Calculate recovery rate
                        recovery = 100 * (concentrate_pb / feed_pb) * (feed_pb - tailings_pb) / (concentrate_pb - tailings_pb)
                        
                        # Shift recovery forward
                        recovery_future_col = f"Recovery_Rate_{horizon}min_ahead"
                        df_future[recovery_future_col] = recovery.shift(-horizon)
        
        # Remove rows with NaN values (at the end where we don't have future data)
        initial_rows = len(df_future)
        df_future = df_future.dropna()
        final_rows = len(df_future)
        
        logger.info(f"Future targets created. Rows: {initial_rows} -> {final_rows} (removed {initial_rows - final_rows} rows with NaN)")
        
        return df_future
    
    def add_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add rolling statistical features for time-series prediction.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with rolling features added
        """
        logger.info("Adding rolling statistical features...")
        
        df_rolling = df.copy()
        
        # Rolling windows to consider (reduced for efficiency)
        windows = [5, 15, 30]  # minutes
        
        # Key variables for rolling features (reduced set)
        rolling_vars = [
            'Feed_Pb', 'Feed_Zn', 'Pb_Conditioner_KEX_Flowrate',
            'Pb_Rougher1_SIPX_Flowrate', 'Pb_Rougher1_AirFlow',
            'Pb_Rougher1_Level', 'Pb_Rougher_Conc_Pb'
        ]
        
        for var in rolling_vars:
            if var in df.columns:
                for window in windows:
                    # Rolling mean
                    df_rolling[f'{var}_rolling_mean_{window}min'] = df[var].rolling(window=window, min_periods=1).mean()
                    
                    # Rolling standard deviation
                    df_rolling[f'{var}_rolling_std_{window}min'] = df[var].rolling(window=window, min_periods=1).std()
        
        logger.info("Rolling features added successfully")
        return df_rolling
    
    def add_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add trend and momentum features.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with trend features added
        """
        logger.info("Adding trend and momentum features...")
        
        df_trend = df.copy()
        
        # Key variables for trend analysis
        trend_vars = [
            'Feed_Pb', 'Feed_Zn', 'Pb_Conditioner_KEX_Flowrate',
            'Pb_Rougher1_SIPX_Flowrate', 'Pb_Rougher1_AirFlow',
            'Pb_Rougher1_Level', 'Pb_Rougher_Conc_Pb'
        ]
        
        for var in trend_vars:
            if var in df.columns:
                # Rate of change (1st derivative)
                df_trend[f'{var}_rate_of_change'] = df[var].diff()
                
                # Momentum (change over last 5 periods)
                df_trend[f'{var}_momentum_5min'] = df[var] - df[var].shift(5)
        
        logger.info("Trend features added successfully")
        return df_trend
    
    def add_seasonality_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add seasonality features based on time patterns.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with seasonality features added
        """
        logger.info("Adding seasonality features...")
        
        df_seasonal = df.copy()
        
        # Extract time components
        df_seasonal['hour_of_day'] = df.index.hour
        df_seasonal['day_of_week'] = df.index.dayofweek
        
        # Cyclical encoding for hour (0-23)
        df_seasonal['hour_sin'] = np.sin(2 * np.pi * df_seasonal['hour_of_day'] / 24)
        df_seasonal['hour_cos'] = np.cos(2 * np.pi * df_seasonal['hour_of_day'] / 24)
        
        # Shift patterns (assuming 8-hour shifts)
        df_seasonal['shift'] = (df_seasonal['hour_of_day'] // 8).astype(int)
        
        logger.info("Seasonality features added successfully")
        return df_seasonal
    
    def select_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Select relevant features for prediction.
        
        Args:
            df: Input DataFrame with all features
            
        Returns:
            DataFrame with selected features
        """
        logger.info("Selecting relevant features...")
        
        # Base features (current values)
        base_features = [
            'Feed_Pb', 'Feed_Zn', 'Pb_Conditioner_KEX_Flowrate',
            'Pb_Rougher1_SIPX_Flowrate', 'Pb_Rougher1_AirFlow',
            'Pb_Rougher1_Level'
        ]
        
        # Lag features (already in the data)
        lag_features = [col for col in df.columns if 'lag' in col.lower()]
        
        # Rolling features
        rolling_features = [col for col in df.columns if 'rolling' in col.lower()]
        
        # Trend features
        trend_features = [col for col in df.columns if any(x in col for x in ['rate_of_change', 'momentum'])]
        
        # Seasonality features
        seasonal_features = [col for col in df.columns if any(x in col for x in ['hour_', 'day_', 'shift'])]
        
        # Target variables (future predictions)
        target_features = [col for col in df.columns if 'ahead' in col.lower()]
        
        # Combine all feature lists
        all_features = base_features + lag_features + rolling_features + trend_features + seasonal_features + target_features
        
        # Filter to only existing columns and remove duplicates
        existing_features = list(dict.fromkeys([col for col in all_features if col in df.columns]))
        
        # Select features
        df_selected = df[existing_features].copy()
        
        # Store feature lists for later use
        self.feature_columns = [col for col in existing_features if col not in target_features]
        self.target_columns = target_features
        
        logger.info(f"Selected {len(self.feature_columns)} feature columns and {len(self.target_columns)} target columns")
        
        return df_selected
    
    def prepare_training_data(self) -> Dict[str, pd.DataFrame]:
        """
        Prepare training data for different prediction horizons.
        
        Returns:
            Dictionary with training datasets for each horizon
        """
        logger.info("Preparing training data for all prediction horizons...")
        
        # Load and process data
        df = self.load_data()
        df = self.create_future_targets(df)
        df = self.add_rolling_features(df)
        df = self.add_trend_features(df)
        df = self.add_seasonality_features(df)
        df = self.select_features(df)
        
        # Store processed data
        self.processed_data = df
        
        # Create training datasets for each horizon
        training_datasets = {}
        
        for horizon in self.prediction_horizons:
            logger.info(f"Creating training dataset for {horizon}-minute predictions...")
            
            # Get target columns for this horizon
            horizon_targets = [col for col in self.target_columns if f'{horizon}min_ahead' in col]
            
            if horizon_targets:
                # Create dataset with features and targets for this horizon
                horizon_features = self.feature_columns + horizon_targets
                horizon_data = df[horizon_features].copy()
                
                # Remove rows with NaN values
                horizon_data = horizon_data.dropna()
                
                training_datasets[f'{horizon}min'] = horizon_data
                
                logger.info(f"{horizon}min dataset shape: {horizon_data.shape}")
        
        return training_datasets
    
    def save_training_datasets(self, training_datasets: Dict[str, pd.DataFrame], output_dir: str = None):
        """
        Save training datasets to files.
        
        Args:
            training_datasets: Dictionary of training datasets
            output_dir: Output directory for saving datasets
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / 'training' / 'time_series_datasets'
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving training datasets to: {output_dir}")
        
        for horizon, dataset in training_datasets.items():
            filename = f"training_data_{horizon}.parquet"
            filepath = output_dir / filename
            
            dataset.to_parquet(filepath)
            logger.info(f"Saved {horizon} dataset: {filepath}")
        
        # Save feature and target column lists
        metadata = {
            'feature_columns': self.feature_columns,
            'target_columns': self.target_columns,
            'prediction_horizons': self.prediction_horizons,
            'processed_timestamp': datetime.now().isoformat()
        }
        
        metadata_path = output_dir / 'dataset_metadata.pkl'
        joblib.dump(metadata, metadata_path)
        logger.info(f"Saved dataset metadata: {metadata_path}")
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of the processed data.
        
        Returns:
            Dictionary with data summary
        """
        if self.processed_data is None:
            return {"error": "No data processed yet"}
        
        summary = {
            'total_rows': len(self.processed_data),
            'total_columns': len(self.processed_data.columns),
            'feature_columns': len(self.feature_columns),
            'target_columns': len(self.target_columns),
            'prediction_horizons': self.prediction_horizons,
            'time_range': {
                'start': self.processed_data.index.min().isoformat(),
                'end': self.processed_data.index.max().isoformat()
            },
            'missing_values': self.processed_data.isnull().sum().sum(),
            'key_features_sample': self.feature_columns[:10],
            'target_variables': self.target_columns
        }
        
        return summary

# Example usage and testing
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize preprocessor
    preprocessor = TimeSeriesPreprocessor()
    
    # Prepare training data
    training_datasets = preprocessor.prepare_training_data()
    
    # Save datasets
    preprocessor.save_training_datasets(training_datasets)
    
    # Print summary
    summary = preprocessor.get_data_summary()
    print("\nData Summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")
