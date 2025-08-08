"""
Flotation Digital Twin Integration
=================================

This module provides integration capabilities for the flotation digital twin,
loading the trained model and providing real-time predictions for process monitoring.
"""

import pandas as pd
import numpy as np
import joblib
import pickle
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Deep Learning
import tensorflow as tf
from tensorflow.keras.models import load_model

class FlotationDigitalTwin:
    """Digital Twin class for flotation process monitoring"""
    
    def __init__(self, model_dir=None):
        """
        Initialize the digital twin with trained model
        
        Parameters:
        -----------
        model_dir : str, optional
            Directory containing the trained model files
        """
        if model_dir is None:
            model_dir = r'C:\@Python Projects\TUT Research Project\Models'
        
        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.model_info = None
        self.feature_columns = None
        self.target_column = None
        self.time_steps = None
        self.model_type = None
        
        # Load model and configuration
        self._load_model()
        
    def _load_model(self):
        """Load the trained model and configuration"""
        try:
            # Load model information
            with open(os.path.join(self.model_dir, 'model_info.pkl'), 'rb') as f:
                self.model_info = pickle.load(f)
            
            self.model_type = self.model_info['model_type']
            self.feature_columns = self.model_info['feature_columns']
            self.target_column = self.model_info['target_column']
            self.time_steps = self.model_info.get('time_steps')
            
            print(f"Loaded model: {self.model_info['best_model']}")
            print(f"Model type: {self.model_type}")
            print(f"Features: {len(self.feature_columns)}")
            print(f"Target: {self.target_column}")
            
            # Load model and scaler
            if self.model_type == 'linear_regression':
                self.model = joblib.load(os.path.join(self.model_dir, 'linear_regression_model.pkl'))
                self.scaler = joblib.load(os.path.join(self.model_dir, 'linear_regression_scaler.pkl'))
                
            elif self.model_type == 'random_forest':
                self.model = joblib.load(os.path.join(self.model_dir, 'random_forest_model.pkl'))
                # Random Forest doesn't need scaling
                
            elif self.model_type == 'lstm':
                self.model = load_model(os.path.join(self.model_dir, 'lstm_model.h5'))
                self.scaler = joblib.load(os.path.join(self.model_dir, 'lstm_scaler.pkl'))
                
            print("✅ Model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def preprocess_input(self, data):
        """
        Preprocess input data for prediction
        
        Parameters:
        -----------
        data : pd.DataFrame
            Input data with features
            
        Returns:
        --------
        processed_data : np.ndarray
            Preprocessed data ready for prediction
        """
        # Ensure we have the required features
        missing_features = set(self.feature_columns) - set(data.columns)
        if missing_features:
            raise ValueError(f"Missing features: {missing_features}")
        
        # Select only the required features
        X = data[self.feature_columns]
        
        # Handle NaN values
        if X.isna().any().any():
            print("Warning: NaN values detected, filling with forward fill")
            X = X.fillna(method='ffill').fillna(method='bfill')
        
        # Scale data if needed
        if self.scaler is not None:
            X_scaled = self.scaler.transform(X)
        else:
            X_scaled = X.values
            
        return X_scaled
    
    def predict_single(self, data):
        """
        Make a single prediction
        
        Parameters:
        -----------
        data : pd.DataFrame
            Input data with features (single row or multiple rows)
            
        Returns:
        --------
        prediction : float or np.ndarray
            Predicted Pb grade value(s)
        """
        X_scaled = self.preprocess_input(data)
        
        if self.model_type == 'lstm':
            # For LSTM, we need sequences
            if len(data) < self.time_steps:
                raise ValueError(f"LSTM requires at least {self.time_steps} time steps")
            
            # Create sequence for the last time_steps
            sequence = X_scaled[-self.time_steps:].reshape(1, self.time_steps, -1)
            prediction = self.model.predict(sequence, verbose=0).flatten()[0]
        else:
            # For other models, use the last row
            prediction = self.model.predict(X_scaled[-1:], verbose=0)[0]
        
        return prediction
    
    def predict_batch(self, data):
        """
        Make batch predictions
        
        Parameters:
        -----------
        data : pd.DataFrame
            Input data with features (multiple rows)
            
        Returns:
        --------
        predictions : np.ndarray
            Array of predicted Pb grade values
        """
        X_scaled = self.preprocess_input(data)
        
        if self.model_type == 'lstm':
            # For LSTM, create sequences
            if len(data) < self.time_steps:
                raise ValueError(f"LSTM requires at least {self.time_steps} time steps")
            
            predictions = []
            for i in range(self.time_steps, len(X_scaled) + 1):
                sequence = X_scaled[i-self.time_steps:i].reshape(1, self.time_steps, -1)
                pred = self.model.predict(sequence, verbose=0).flatten()[0]
                predictions.append(pred)
            
            return np.array(predictions)
        else:
            # For other models, predict all rows
            return self.model.predict(X_scaled, verbose=0)
    
    def predict_with_confidence(self, data, n_iterations=100):
        """
        Make predictions with confidence intervals (for Random Forest)
        
        Parameters:
        -----------
        data : pd.DataFrame
            Input data with features
        n_iterations : int
            Number of iterations for confidence calculation
            
        Returns:
        --------
        prediction : float
            Mean prediction
        confidence_interval : tuple
            (lower_bound, upper_bound) at 95% confidence
        """
        if self.model_type != 'random_forest':
            prediction = self.predict_single(data)
            return prediction, (prediction, prediction)
        
        X_scaled = self.preprocess_input(data)
        
        # Get predictions from all trees
        predictions = []
        for estimator in self.model.estimators_:
            pred = estimator.predict(X_scaled[-1:])[0]
            predictions.append(pred)
        
        predictions = np.array(predictions)
        
        # Calculate statistics
        mean_pred = np.mean(predictions)
        std_pred = np.std(predictions)
        
        # 95% confidence interval
        lower_bound = mean_pred - 1.96 * std_pred
        upper_bound = mean_pred + 1.96 * std_pred
        
        return mean_pred, (lower_bound, upper_bound)
    
    def get_model_performance(self):
        """Get model performance metrics"""
        if self.model_info is None:
            return None
        
        return self.model_info['test_performance']
    
    def get_feature_importance(self, top_n=10):
        """
        Get feature importance (for Random Forest and Linear Regression)
        
        Parameters:
        -----------
        top_n : int
            Number of top features to return
            
        Returns:
        --------
        importance_df : pd.DataFrame
            DataFrame with feature importance
        """
        if self.model_type == 'random_forest':
            importance = self.model.feature_importances_
        elif self.model_type == 'linear_regression':
            importance = np.abs(self.model.coef_)
        else:
            return None
        
        importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        return importance_df.head(top_n)
    
    def simulate_process_conditions(self, base_data, variations=None):
        """
        Simulate different process conditions
        
        Parameters:
        -----------
        base_data : pd.DataFrame
            Base process data
        variations : dict, optional
            Dictionary of feature variations to simulate
            
        Returns:
        --------
        simulation_results : pd.DataFrame
            Results of the simulation
        """
        if variations is None:
            variations = {}
        
        results = []
        
        for feature, variation_range in variations.items():
            if feature not in self.feature_columns:
                print(f"Warning: {feature} not in model features")
                continue
            
            for value in variation_range:
                # Create modified data
                modified_data = base_data.copy()
                modified_data[feature] = value
                
                # Make prediction
                prediction = self.predict_single(modified_data)
                
                results.append({
                    'feature': feature,
                    'value': value,
                    'predicted_grade': prediction
                })
        
        return pd.DataFrame(results)
    
    def monitor_process(self, real_time_data, threshold=0.1):
        """
        Monitor process in real-time and detect anomalies
        
        Parameters:
        -----------
        real_time_data : pd.DataFrame
            Real-time process data
        threshold : float
            Threshold for anomaly detection (relative to historical performance)
            
        Returns:
        --------
        monitoring_result : dict
            Monitoring results with predictions and alerts
        """
        try:
            # Make prediction
            prediction = self.predict_single(real_time_data)
            
            # Get model performance for comparison
            performance = self.get_model_performance()
            rmse = performance['rmse'] if performance else 0.1
            
            # Calculate confidence bounds
            if self.model_type == 'random_forest':
                pred, (lower, upper) = self.predict_with_confidence(real_time_data)
                confidence_interval = (lower, upper)
            else:
                confidence_interval = (prediction - rmse, prediction + rmse)
            
            # Check for anomalies
            is_anomaly = False
            if performance:
                # Simple anomaly detection based on prediction confidence
                if abs(prediction - np.mean([confidence_interval[0], confidence_interval[1]])) > threshold * rmse:
                    is_anomaly = True
            
            return {
                'timestamp': datetime.now(),
                'predicted_grade': prediction,
                'confidence_interval': confidence_interval,
                'is_anomaly': is_anomaly,
                'model_performance': performance
            }
            
        except Exception as e:
            return {
                'timestamp': datetime.now(),
                'error': str(e),
                'is_anomaly': True
            }
    
    def generate_report(self, data, output_path=None):
        """
        Generate a comprehensive prediction report
        
        Parameters:
        -----------
        data : pd.DataFrame
            Input data for prediction
        output_path : str, optional
            Path to save the report
            
        Returns:
        --------
        report : dict
            Comprehensive prediction report
        """
        try:
            # Make predictions
            predictions = self.predict_batch(data)
            
            # Calculate statistics
            report = {
                'model_info': {
                    'model_type': self.model_type,
                    'best_model': self.model_info['best_model'],
                    'features_used': len(self.feature_columns),
                    'target_variable': self.target_column
                },
                'predictions': {
                    'mean': np.mean(predictions),
                    'std': np.std(predictions),
                    'min': np.min(predictions),
                    'max': np.max(predictions),
                    'count': len(predictions)
                },
                'performance': self.get_model_performance(),
                'feature_importance': self.get_feature_importance().to_dict('records') if self.get_feature_importance() is not None else None,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save report if path provided
            if output_path:
                import json
                with open(output_path, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                print(f"Report saved to: {output_path}")
            
            return report
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return None

def main():
    """Example usage of the Digital Twin"""
    # Initialize digital twin
    digital_twin = FlotationDigitalTwin()
    
    # Example: Load some test data
    test_data_path = r'C:\@Python Projects\TUT Research Project\Clean_Data\HZL_RA4_Pb_Rougher_2025-07_clean.parquet'
    
    if os.path.exists(test_data_path):
        test_data = pd.read_parquet(test_data_path)
        
        # Select a small sample for testing
        sample_data = test_data[digital_twin.feature_columns].tail(20)
        
        print("\n=== Digital Twin Test ===")
        print(f"Sample data shape: {sample_data.shape}")
        
        # Make prediction
        prediction = digital_twin.predict_single(sample_data)
        print(f"Predicted Pb Grade: {prediction:.4f}%")
        
        # Get model performance
        performance = digital_twin.get_model_performance()
        print(f"Model R²: {performance['r2']:.4f}")
        print(f"Model RMSE: {performance['rmse']:.4f}")
        
        # Generate report
        report = digital_twin.generate_report(sample_data)
        print(f"Report generated: {report['predictions']['count']} predictions")
        
    else:
        print("Test data not found. Please ensure the model is trained first.")

if __name__ == "__main__":
    main()
