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

from interfaces import IDataGenerator, IHistoricalDataManager

class FlotationDataGenerator(IDataGenerator):
    """Generates realistic flotation data with dynamic optimal balance"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._initialize_base_values()
        self._calculate_optimal_balance()
        
    def _initialize_base_values(self):
        """Initialize base values for flotation parameters"""
        self.base_values = {
            'pH': 11.25,
            'Temperature': 25.0,
            'Pulp_Density': 30.0,
            'Feed_Zn': 10.0,
            'Cell_Level': 70.0,
            'Froth_Height': 15.0,
            'Pb_Conditioner_Nigrosine_Flowrate_Min': 12.0,
            'Pb_Conditioner_Nigrosine_Flowrate_Max': 18.0
        }
        
    def _calculate_optimal_balance(self):
        """Calculate optimal balance based on reagent interactions"""
        self.logger.info("Calculating dynamic optimal balance for flotation parameters")
        
        # Base feed characteristics
        self.feed_pb = round(random.uniform(2.0, 3.5), 2)
        self.feed_zn = round(random.uniform(8.0, 12.0), 2)
        
        # Calculate optimal KEX based on feed characteristics
        zn_factor = self.feed_zn / 10.0
        pb_factor = self.feed_pb / 2.5
        self.optimal_kex = round(35 + (zn_factor - 1.0) * 15 + (pb_factor - 1.0) * 10, 1)
        self.optimal_kex = max(35, min(60, self.optimal_kex))
        
        # Calculate optimal SIPX based on KEX
        kex_factor = self.optimal_kex / 47.0
        self.optimal_sipx = round(20 + (kex_factor - 1.0) * 8 + random.uniform(-2, 2), 1)
        self.optimal_sipx = max(15, min(30, self.optimal_sipx))
        
        # Calculate optimal AirFlow based on froth height and cell level
        froth_factor = self.base_values['Froth_Height'] / 15.0
        level_factor = self.base_values['Cell_Level'] / 70.0
        self.optimal_airflow = round(120 + (froth_factor - 1.0) * 20 + (level_factor - 1.0) * 15, 1)
        self.optimal_airflow = max(100, min(150, self.optimal_airflow))
        
        # Calculate optimal Impeller Speed
        self.optimal_impeller = round(1200 + random.uniform(-50, 50), 0)
        self.optimal_impeller = max(1100, min(1300, self.optimal_impeller))
        
        self.logger.info(f"Optimal values calculated - KEX: {self.optimal_kex}, SIPX: {self.optimal_sipx}, AirFlow: {self.optimal_airflow}")
    
    def generate_data_point(self) -> Dict[str, Any]:
        """Generate a single flotation data point"""
        # Add realistic variations to optimal values
        kex_variation = random.uniform(-3, 3)
        sipx_variation = random.uniform(-2, 2)
        airflow_variation = random.uniform(-10, 10)
        impeller_variation = random.uniform(-30, 30)
        
        # Generate data point with realistic variations
        data_point = {
            'timestamp': datetime.now().isoformat(),
            'pH': round(self.base_values['pH'] + random.uniform(-0.2, 0.2), 2),
            'Temperature': round(self.base_values['Temperature'] + random.uniform(-1, 1), 1),
            'Pulp_Density': round(self.base_values['Pulp_Density'] + random.uniform(-2, 2), 1),
            'Feed_Pb': round(self.feed_pb + random.uniform(-0.1, 0.1), 2),
            'Feed_Zn': round(self.feed_zn + random.uniform(-0.2, 0.2), 2),
            'Pb_Conditioner_KEX_Flowrate': round(self.optimal_kex + kex_variation, 1),
            'Pb_Rougher1_SIPX_Flowrate': round(self.optimal_sipx + sipx_variation, 1),
            'Pb_Rougher1_AirFlow': round(self.optimal_airflow + airflow_variation, 1),
            'Pb_Rougher1_Level': round(self.base_values['Cell_Level'] + random.uniform(-3, 3), 1),
            'Impeller_Speed': round(self.optimal_impeller + impeller_variation, 0),
            'Froth_Height': round(self.base_values['Froth_Height'] + random.uniform(-1, 1), 1),
            'Pb_Conditioner_Nigrosine_Flowrate_Min': round(self.base_values['Pb_Conditioner_Nigrosine_Flowrate_Min'] + random.uniform(-1, 1), 1),
            'Pb_Conditioner_Nigrosine_Flowrate_Max': round(self.base_values['Pb_Conditioner_Nigrosine_Flowrate_Max'] + random.uniform(-1, 1), 1)
        }
        
        return data_point
    
    def get_parameter_ranges(self) -> Dict[str, Tuple[float, float]]:
        """Get valid parameter ranges"""
        return {
            'pH': (10.5, 12.0),
            'Temperature': (20.0, 30.0),
            'Pulp_Density': (25.0, 35.0),
            'Feed_Pb': (1.5, 4.0),
            'Feed_Zn': (7.0, 13.0),
            'Pb_Conditioner_KEX_Flowrate': (30.0, 65.0),
            'Pb_Rougher1_SIPX_Flowrate': (12.0, 35.0),
            'Pb_Rougher1_AirFlow': (90.0, 160.0),
            'Pb_Rougher1_Level': (60.0, 80.0),
            'Impeller_Speed': (1050.0, 1350.0),
            'Froth_Height': (12.0, 18.0)
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
