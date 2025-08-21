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
        
    def _initialize_base_values(self):
        """Initialize base values for flotation parameters - ONLY parameters from training data"""
        # Based on actual training data analysis
        self.base_values = {
            'Feed_Zn': 10.32,  # From training data mean
            'Pb_Rougher1_Level': 39.01,  # From training data mean
        }
        
    def _calculate_optimal_balance(self):
        """Calculate optimal balance based on ACTUAL training data ranges"""
        self.logger.info("Calculating dynamic optimal balance based on training data")
        
        # Base feed characteristics - using ACTUAL training data ranges
        self.feed_pb = round(random.uniform(0.5, 2.5), 2)  # From training: 0.00 - 2.55
        self.feed_zn = round(random.uniform(8.0, 12.5), 2)  # From training: 0.00 - 14.20
        
        # Calculate optimal KEX based on ACTUAL training data ranges
        # Training data: -2.55 - 1499.97, Mean: 916.30 ± 300.58
        self.optimal_kex = round(random.uniform(600, 1200), 1)  # Realistic range from training
        
        # Calculate optimal SIPX based on ACTUAL training data ranges  
        # Training data: -1.31 - 1198.63, Mean: 439.93 ± 369.69
        self.optimal_sipx = round(random.uniform(200, 700), 1)  # Realistic range from training
        
        # Calculate optimal AirFlow based on ACTUAL training data ranges
        # Training data: 3.99 - 14.17, Mean: 9.97 ± 2.30
        self.optimal_airflow = round(random.uniform(7.0, 13.0), 2)  # Realistic range from training
        
        # Calculate optimal Level based on ACTUAL training data ranges
        # Training data: 0.00 - 86.50, Mean: 39.01 ± 30.10
        self.optimal_level = round(random.uniform(20.0, 60.0), 1)  # Realistic range from training
        
        self.logger.info(f"Optimal values calculated - KEX: {self.optimal_kex}, SIPX: {self.optimal_sipx}, AirFlow: {self.optimal_airflow}")
    
    def generate_data_point(self) -> Dict[str, Any]:
        """Generate a single flotation data point - ONLY parameters from training data"""
        # Add realistic variations based on ACTUAL training data ranges
        kex_variation = random.uniform(-100, 100)  # Large variation as per training data
        sipx_variation = random.uniform(-150, 150)  # Large variation as per training data
        airflow_variation = random.uniform(-1.5, 1.5)  # Smaller variation as per training data
        level_variation = random.uniform(-15, 15)  # Moderate variation as per training data
        
        # Generate data point with ONLY parameters from training data
        data_point = {
            'timestamp': datetime.now().isoformat(),
            'Feed_Pb': round(self.feed_pb + random.uniform(-0.2, 0.2), 2),  # Training: 0.00 - 2.55
            'Feed_Zn': round(self.feed_zn + random.uniform(-1.0, 1.0), 2),  # Training: 0.00 - 14.20
            'Pb_Conditioner_KEX_Flowrate': round(self.optimal_kex + kex_variation, 1),  # Training: -2.55 - 1499.97
            'Pb_Rougher1_SIPX_Flowrate': round(self.optimal_sipx + sipx_variation, 1),  # Training: -1.31 - 1198.63
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
            
            # Recalculate optimal balance if needed
            if 'kex' in controls or 'sipx' in controls:
                self._calculate_optimal_balance()
                
        except Exception as e:
            self.logger.error(f"Error updating control settings: {e}")
            raise

class HistoricalDataManager(IHistoricalDataManager):
    """Manages historical data for lag features"""
    
    def __init__(self, max_history: int = 100, logger: logging.Logger = None):
        self.max_history = max_history
        self.historical_data = []
        self.logger = logger or logging.getLogger(__name__)
    
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
