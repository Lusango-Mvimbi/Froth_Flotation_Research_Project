"""
ML Model Implementation
======================

This module implements the ML model service following SOLID principles.
"""

import numpy as np
import pandas as pd
import os
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime
import joblib
from pathlib import Path

from interfaces import IMLModel, IFeatureProcessor, IProcessStatusAnalyzer

class GradientBoostingModel(IMLModel):
    """Gradient Boosting model implementation"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.model = None
        self.model_metadata = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained Random Forest model"""
        try:
            model_path = Path(__file__).parent.parent / 'trained_models' / 'rf_optimized_model.pkl'
            metadata_path = Path(__file__).parent.parent / 'trained_models' / 'rf_metadata.pkl'
            
            if model_path.exists() and metadata_path.exists():
                self.model = joblib.load(model_path)
                self.model_metadata = joblib.load(metadata_path)
                self.logger.info(f"Loaded trained model: {self.model_metadata['model_name'].upper()}")
                self.logger.info(f"Model Performance - R²: {self.model_metadata['test_r2']:.4f}, RMSE: {self.model_metadata['test_rmse']:.4f}")
            else:
                self.logger.warning("Trained model not found")
                self.model = None
                self.model_metadata = None
                
        except Exception as e:
            self.logger.error(f"Failed to load trained model: {e}")
            self.model = None
            self.model_metadata = None
    
    def predict(self, features: Dict[str, float]) -> float:
        """Make a prediction using the model"""
        if not self.is_loaded():
            self.logger.error("Model not loaded, cannot make prediction")
            return 0.0
        
        try:
            # Convert features to array format expected by model
            feature_array = np.array([list(features.values())])
            prediction = self.model.predict(feature_array)[0]
            return float(prediction)
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            return 0.0
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if self.model_metadata is not None:
            return {
                'model_name': self.model_metadata['model_name'].upper(),
                'model_type': self.model_metadata['model_type'],
                'test_r2': round(self.model_metadata['test_r2'], 4),
                'test_rmse': round(self.model_metadata['test_rmse'], 4),
                'test_mae': round(self.model_metadata['test_mae'], 4),
                'test_pred_10%': round(self.model_metadata['test_pred_10%'] * 100, 1),
                'training_date': self.model_metadata['training_date'],
                'status': 'loaded'
            }
        else:
            return {
                'model_name': 'RULE_BASED',
                'model_type': 'Rule-based prediction',
                'test_r2': 0.0,
                'test_rmse': 0.0,
                'test_mae': 0.0,
                'test_pred_10%': 0.0,
                'training_date': 'N/A',
                'status': 'fallback'
            }
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded"""
        return self.model is not None

class FeatureProcessor(IFeatureProcessor):
    """Feature processing implementation"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.feature_names = [
            'pH', 'Temperature', 'Pb_Rougher1_AirFlow', 'Pulp_Density',
            'Pb_Conditioner_KEX_Flowrate', 'Pb_Rougher1_SIPX_Flowrate',
            'Feed_Pb', 'Feed_Zn', 'Pb_Rougher1_Level', 'Impeller_Speed', 'Froth_Height'
        ]
        
        # Additional features for the 150-feature model
        self.additional_features = [
            'pH_lag1', 'pH_lag2', 'Temperature_lag1', 'Temperature_lag2',
            'Pb_Rougher1_AirFlow_lag1', 'Pb_Rougher1_AirFlow_lag2',
            'Pulp_Density_lag1', 'Pulp_Density_lag2',
            'Pb_Conditioner_KEX_Flowrate_lag1', 'Pb_Conditioner_KEX_Flowrate_lag2',
            'Pb_Rougher1_SIPX_Flowrate_lag1', 'Pb_Rougher1_SIPX_Flowrate_lag2',
            'Feed_Pb_lag1', 'Feed_Pb_lag2', 'Feed_Zn_lag1', 'Feed_Zn_lag2',
            'Pb_Rougher1_Level_lag1', 'Pb_Rougher1_Level_lag2',
            'Impeller_Speed_lag1', 'Impeller_Speed_lag2',
            'Froth_Height_lag1', 'Froth_Height_lag2'
        ]
    
    def prepare_features(self, raw_data: Dict[str, float]) -> Dict[str, float]:
        """Prepare features for model prediction"""
        features = {}
        
        # Add base features
        for feature in self.feature_names:
            features[feature] = raw_data.get(feature, 0.0)
        
        # Add lag features if available
        for feature in self.additional_features:
            features[feature] = raw_data.get(feature, 0.0)
        
        # Fill remaining features to reach 150 features
        remaining_features = 150 - len(features)
        for i in range(remaining_features):
            features[f'feature_{i+1}'] = 0.0
        
        return features
    
    def get_feature_names(self) -> List[str]:
        """Get the list of feature names"""
        return self.feature_names + self.additional_features
    
    def validate_features(self, features: Dict[str, float]) -> bool:
        """Validate if all required features are present"""
        required_features = self.get_feature_names()
        
        for feature in required_features:
            if feature not in features:
                self.logger.warning(f"Missing required feature: {feature}")
                return False
        
        return True

class ProcessStatusAnalyzer(IProcessStatusAnalyzer):
    """Process status analysis implementation"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.target_ranges = {
            'pb_concentrate': (9.5, 11.5),   # Optimal range based on model predictions
            'recovery_rate': (75.0, 95.0),   # Target recovery range
        }
    
    def analyze_status(self, predictions: Dict[str, float]) -> str:
        """Analyze process status based on predictions"""
        pb_concentrate = predictions.get('pb_concentrate', 0.0)
        recovery_rate = predictions.get('recovery_rate', 0.0)
        
        # Check Pb concentrate status
        pb_min, pb_max = self.target_ranges['pb_concentrate']
        pb_status = self._get_parameter_status(pb_concentrate, pb_min, pb_max)
        
        # Check recovery rate status
        recovery_min, recovery_max = self.target_ranges['recovery_rate']
        recovery_status = self._get_parameter_status(recovery_rate, recovery_min, recovery_max)
        
        # Determine overall status
        if pb_status == 'critical' or recovery_status == 'critical':
            return 'critical'
        elif pb_status == 'warning' or recovery_status == 'warning':
            return 'warning'
        else:
            return 'optimal'
    
    def _get_parameter_status(self, value: float, min_val: float, max_val: float) -> str:
        """Get status for a single parameter"""
        if value < min_val * 0.8 or value > max_val * 1.2:
            return 'critical'
        elif value < min_val or value > max_val:
            return 'warning'
        else:
            return 'optimal'
    
    def get_target_ranges(self) -> Dict[str, Tuple[float, float]]:
        """Get target ranges for status analysis"""
        return self.target_ranges.copy()
    
    def get_recommendations(self, status: str, predictions: Dict[str, float]) -> List[str]:
        """Get recommendations based on status and predictions"""
        recommendations = []
        
        if status == 'critical':
            recommendations.extend([
                "Immediate intervention required",
                "Check reagent dosing systems",
                "Verify sensor calibrations",
                "Review feed characteristics"
            ])
        elif status == 'warning':
            recommendations.extend([
                "Monitor process parameters closely",
                "Consider adjusting reagent flow rates",
                "Check froth height and cell level",
                "Review air flow settings"
            ])
        else:  # optimal
            recommendations.extend([
                "Process operating within optimal ranges",
                "Continue current operating parameters",
                "Maintain regular monitoring schedule"
            ])
        
        return recommendations

class RecoveryCalculator:
    """Calculates recovery rate using froth flotation equations"""
    
    @staticmethod
    def calculate_recovery_rate(data: Dict[str, float]) -> float:
        """Calculate Pb recovery rate using froth flotation equations"""
        try:
            # Extract key parameters
            feed_pb = data.get('Feed_Pb', 2.5)
            pb_concentrate = data.get('pb_concentrate', 10.0)
            
            # Simplified recovery calculation based on feed and concentrate grades
            # This is a simplified model - in practice, more complex equations would be used
            if feed_pb > 0 and pb_concentrate > 0:
                # Recovery = (Concentrate Grade / Feed Grade) * Recovery Factor
                recovery_factor = 0.85  # Typical recovery factor for Pb flotation
                recovery = (pb_concentrate / feed_pb) * recovery_factor * 100
                return max(0.0, min(100.0, recovery))
            else:
                return 85.0  # Default recovery rate
                
        except Exception as e:
            logging.getLogger(__name__).error(f"Recovery calculation failed: {e}")
            return 85.0  # Default recovery rate
