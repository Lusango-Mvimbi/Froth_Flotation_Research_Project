"""
Data Generator Implementation
============================

This module implements the data generation service following SOLID principles.
"""

import random
import numpy as np
from datetime import datetime
from typing import Dict, Any, Tuple, List
import logging

from services.interfaces import IDataGenerator, IHistoricalDataManager

class FlotationDataGenerator(IDataGenerator):
    """Generates realistic flotation data with dynamic optimal balance"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._initialize_base_values()
        self._calculate_optimal_balance()
        self.logger.info(f"Data generator initialized with KEX={self.optimal_kex}, SIPX={self.optimal_sipx}")
        
    def _initialize_base_values(self):
        """Initialize base values for flotation parameters - ONLY parameters from training data"""
        # Based on actual training data analysis
        self.base_values = {
            'Feed_Zn': 10.32,  # From training data mean
            'Pb_Rougher1_Level': 39.01,  # From training data mean
        }
        
    def _calculate_optimal_balance(self):
        """Calculate optimal balance based on ACTUAL training data ranges"""
        self.logger.debug("Calculating dynamic optimal balance based on training data")
        
        # Base feed characteristics - using ACTUAL training data ranges
        self.feed_pb = round(random.uniform(0.5, 2.5), 2)  # From training: 0.00 - 2.55
        self.feed_zn = round(random.uniform(8.0, 12.5), 2)  # From training: 0.00 - 14.20
        
        # Use control ranges for KEX and SIPX (operator-controlled parameters)
        control_ranges = self.get_control_ranges()
        # Initialize with default optimal values - operator will control these
        self.optimal_kex = control_ranges['kex']['optimal']  # Default: 60.0 L/min
        self.optimal_sipx = control_ranges['sipx']['optimal']  # Default: 30.0 L/min
        
        # Calculate optimal AirFlow based on ACTUAL training data ranges
        # Training data: 3.99 - 14.17, Mean: 9.97 ± 2.30
        self.optimal_airflow = round(random.uniform(7.0, 13.0), 2)  # Realistic range from training
        
        # Calculate optimal Level based on ACTUAL training data ranges
        # Training data: 0.00 - 86.50, Mean: 39.01 ± 30.10
        self.optimal_level = round(random.uniform(20.0, 60.0), 1)  # Realistic range from training
        
        self.logger.debug(f"Optimal values calculated - KEX: {self.optimal_kex}, SIPX: {self.optimal_sipx}, AirFlow: {self.optimal_airflow}")
    
    def _update_dynamic_values(self):
        """Update KEX and SIPX values only when operator changes them - no automatic changes"""
        # KEX and SIPX values should only change when operator sets them
        # This method is kept for compatibility but does nothing automatically
        pass
    
    def generate_data_point(self) -> Dict[str, Any]:
        """Generate a single flotation data point - ONLY parameters from training data"""
        # KEX and SIPX values are controlled by operator - no automatic changes
        
        # Generate fresh feed values each time for better variation
        fresh_feed_pb = round(random.uniform(0.5, 2.5), 2)  # Full range from training data
        fresh_feed_zn = round(random.uniform(8.0, 12.5), 2)  # Full range from training data
        
        # Add realistic variations for other parameters
        airflow_variation = random.uniform(-1.5, 1.5)  # Smaller variation as per training data
        level_variation = random.uniform(-15, 15)  # Moderate variation as per training data
        
        # Generate data point with ONLY parameters from training data
        data_point = {
            'timestamp': datetime.now().isoformat(),
            'Feed_Pb': fresh_feed_pb,  # Fresh value each time for better variation
            'Feed_Zn': fresh_feed_zn,  # Fresh value each time for better variation
            'Pb_Conditioner_KEX_Flowrate': round(self.optimal_kex, 1),  # Use operator's control setting directly
            'Pb_Rougher1_SIPX_Flowrate': round(self.optimal_sipx, 1),  # Use operator's control setting directly
            'Pb_Rougher1_AirFlow': round(self.optimal_airflow + airflow_variation, 2),  # Training: 3.99 - 14.17
            'Pb_Rougher1_Level': round(self.optimal_level + level_variation, 1),  # Training: 0.00 - 86.50
        }
        
        return data_point
    
    def get_parameter_ranges(self) -> Dict[str, Tuple[float, float]]:
        """Get valid parameter ranges - ONLY from training data"""
        return {
            'Feed_Pb': (0.0, 2.55),  # From training data
            'Feed_Zn': (0.0, 14.20),  # From training data
            'Pb_Conditioner_KEX_Flowrate': (-2.55, 1499.97),  # From training data
            'Pb_Rougher1_SIPX_Flowrate': (-1.31, 1198.63),  # From training data
            'Pb_Rougher1_AirFlow': (3.99, 14.17),  # From training data
            'Pb_Rougher1_Level': (0.0, 86.50),  # From training data
        }
    
    def get_control_ranges(self) -> Dict[str, Dict[str, Any]]:
        """Get control ranges based on realistic training data ranges and current process conditions"""
        # Calculate optimal ranges based on training data analysis and current conditions
        # Training data analysis shows optimal KEX range: 35-75 L/min, optimal SIPX range: 18-45 L/min
        
        # Base optimal ranges from training data analysis and industry knowledge
        # Training data range: KEX -2.55 to 1499.97, SIPX -1.31 to 1198.63
        # Industry realistic ranges: KEX 20-100 L/min, SIPX 10-50 L/min
        # Using middle 50% of realistic ranges for optimal operation
        kex_optimal_min = 40.0  # 25th percentile of realistic range (20-100)
        kex_optimal_max = 80.0  # 75th percentile of realistic range (20-100)
        sipx_optimal_min = 20.0  # 25th percentile of realistic range (10-50)
        sipx_optimal_max = 40.0  # 75th percentile of realistic range (10-50)
        
        # Adjust based on current process conditions (if we have historical data)
        # For now, use training data based ranges
        return {
            'kex': {
                'min': 0.0,  # Training data minimum: -2.55, but 0 is more realistic for control
                'max': 100.0,  # Realistic maximum for KEX flow rate
                'optimal_min': kex_optimal_min,  # Calculated optimal minimum
                'optimal_max': kex_optimal_max,  # Calculated optimal maximum
                'optimal': (kex_optimal_min + kex_optimal_max) / 2,  # Mid-point of optimal range
                'unit': 'L/min',
                'description': 'Collector reagent flow rate'
            },
            'sipx': {
                'min': 0.0,  # Training data minimum: -1.31, but 0 is more realistic for control
                'max': 60.0,  # Realistic maximum for SIPX flow rate
                'optimal_min': sipx_optimal_min,  # Calculated optimal minimum
                'optimal_max': sipx_optimal_max,  # Calculated optimal maximum
                'optimal': (sipx_optimal_min + sipx_optimal_max) / 2,  # Mid-point of optimal range
                'unit': 'L/min',
                'description': 'Frother reagent flow rate'
            }
        }
    
    def get_target_ranges(self) -> Dict[str, Dict[str, Any]]:
        """Get target ranges for prediction cards and status analysis - based on training data"""
        return {
            'pb_concentrate': {
                'min': 15.0,  # Realistic minimum from training data
                'max': 35.0,  # Realistic maximum from training data (45.82% was max)
                'optimal': 24.35,  # Training data mean
                'unit': '%'
            },
            'recovery': {
                'min': 75.0,
                'max': 95.0,
                'optimal': 85.0,
                'unit': '%'
            },
            'feed_grade': {
                'min': 0.5,  # Training data realistic minimum
                'max': 2.5,  # Training data realistic maximum
                'optimal': 1.47,  # Training data mean
                'unit': '%'
            },
            'status': {
                'good': ['optimal', 'good', 'stable'],
                'warning': ['suboptimal', 'warning'],
                'critical': ['critical', 'error', 'fault']
            }
        }
    
    def validate_parameters(self, params: Dict[str, float]) -> bool:
        """Validate if parameters are within acceptable ranges"""
        ranges = self.get_parameter_ranges()
        
        for param, value in params.items():
            if param in ranges:
                min_val, max_val = ranges[param]
                if not (min_val <= value <= max_val):
                    self.logger.warning(f"Parameter {param} = {value} is outside valid range [{min_val}, {max_val}]")
                    return False
        
        return True
    
    def update_control_settings(self, controls: Dict[str, float]) -> None:
        """Update control settings for the flotation process"""
        try:
            # Update optimal values based on new control settings
            if 'kex' in controls:
                self.optimal_kex = controls['kex']
                self.logger.info(f"Updated optimal KEX to: {self.optimal_kex}")
            
            if 'sipx' in controls:
                self.optimal_sipx = controls['sipx']
                self.logger.info(f"Updated optimal SIPX to: {self.optimal_sipx}")
            
            # Don't recalculate optimal balance - keep operator's chosen values
            self.logger.info(f"Control settings updated successfully: KEX={self.optimal_kex}, SIPX={self.optimal_sipx}")
            
            # Force the next data generation to use these values
            self.logger.info(f"Next data generation will use KEX={self.optimal_kex}, SIPX={self.optimal_sipx}")
                
        except Exception as e:
            self.logger.error(f"Error updating control settings: {e}")
            raise

class HistoricalDataManager(IHistoricalDataManager):
    """Manages historical data for lag features"""
    
    def __init__(self, max_history: int = 100, logger: logging.Logger = None):
        self.max_history = max_history
        self.historical_data = []
        from services.shared_logging import get_logger
        self.logger = logger or get_logger(__name__)
    
    def add_data_point(self, data_point: Dict[str, Any]) -> None:
        """Add a new data point to historical data"""
        self.historical_data.append(data_point)
        
        # Keep only the most recent data points
        if len(self.historical_data) > self.max_history:
            self.historical_data.pop(0)
    
    def get_recent_data(self, count: int) -> List[Dict[str, Any]]:
        """Get the most recent data points"""
        return self.historical_data[-count:] if self.historical_data else []
    
    def get_lag_features(self, current_data: Dict[str, float]) -> Dict[str, float]:
        """Calculate lag features from historical data"""
        lag_features = {}
        
        if len(self.historical_data) < 2:
            # If not enough historical data, use current values
            for key, value in current_data.items():
                if isinstance(value, (int, float)):
                    lag_features[f"{key}_lag1"] = value
                    lag_features[f"{key}_lag2"] = value
            return lag_features
        
        # Get the last two data points
        last_data = self.historical_data[-1]
        second_last_data = self.historical_data[-2]
        
        # Calculate lag features for numerical parameters
        for key, current_value in current_data.items():
            if isinstance(current_value, (int, float)):
                lag1_value = last_data.get(key, current_value)
                lag2_value = second_last_data.get(key, current_value)
                
                lag_features[f"{key}_lag1"] = lag1_value
                lag_features[f"{key}_lag2"] = lag2_value
        
        return lag_features
