"""
Froth Flotation Prediction Script
================================

This script provides a simple interface for making predictions using the
optimized froth flotation model. It loads the trained model and provides
functions for both single predictions and batch predictions.

Key Features:
- Load optimized model and metadata
- Single prediction interface
- Batch prediction interface
- Input validation and preprocessing
- Prediction confidence estimation

Author: AI Assistant
Date: 2024
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class FlotationPredictor:
    """
    A class for making predictions using the optimized froth flotation model.
    
    This class loads the trained model and provides methods for making
    predictions on new data with proper preprocessing and validation.
    
    Attributes:
        model: The trained machine learning model
        metadata (dict): Model metadata including performance metrics
        feature_names (list): Names of features used by the model
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the predictor by loading the trained model.
        
        Args:
            model_path (str, optional): Path to the model file. If None, 
                                      loads the best model automatically.
        """
        if model_path is None:
            # Try to find the best model automatically
            models_dir = Path('models')
            if models_dir.exists():
                model_files = list(models_dir.glob('*_optimized_model.pkl'))
                if model_files:
                    model_path = str(model_files[0])  # Use the first found model
                    print(f"📁 Auto-detected model: {model_path}")
                else:
                    raise FileNotFoundError("No optimized model found. Please run the training pipeline first.")
            else:
                raise FileNotFoundError("Models directory not found. Please run the training pipeline first.")
        
        # Load the model
        print(f"🤖 Loading model from: {model_path}")
        self.model = joblib.load(model_path)
        
        # Load metadata if available
        metadata_path = model_path.replace('_optimized_model.pkl', '_metadata.pkl')
        if Path(metadata_path).exists():
            self.metadata = joblib.load(metadata_path)
            print(f"📋 Model metadata loaded:")
            print(f"   • Model Type: {self.metadata['model_type']}")
            print(f"   • Test R² Score: {self.metadata['test_r2']:.4f}")
            print(f"   • Test RMSE: {self.metadata['test_rmse']:.4f}")
            print(f"   • Training Date: {self.metadata['training_date']}")
        else:
            self.metadata = {}
            print("⚠️ No metadata found for the model")
        
        # Get feature names from the model if available
        if hasattr(self.model, 'feature_names_in_'):
            self.feature_names = list(self.model.feature_names_in_)
        else:
            self.feature_names = None
            print("⚠️ Feature names not available from model")
        
        print("✅ Model loaded successfully!")
    
    def preprocess_input(self, data):
        """
        Preprocess input data to match the format expected by the model.
        
        This method handles data validation, feature selection, and formatting
        to ensure the input data is compatible with the trained model.
        
        Args:
            data (pd.DataFrame or dict): Input data to preprocess
            
        Returns:
            pd.DataFrame: Preprocessed data ready for prediction
        """
        # Convert dict to DataFrame if necessary
        if isinstance(data, dict):
            data = pd.DataFrame([data])
        
        # Ensure data is a DataFrame
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input data must be a pandas DataFrame or dictionary")
        
        # Select only numeric columns
        numeric_data = data.select_dtypes(include=[np.number])
        
        # Check if we have the expected features
        if self.feature_names is not None:
            # Check for missing features
            missing_features = set(self.feature_names) - set(numeric_data.columns)
            if missing_features:
                print(f"⚠️ Missing features: {missing_features}")
                # Add missing features with default values (0)
                for feature in missing_features:
                    numeric_data[feature] = 0
            
            # Select only the features used by the model
            numeric_data = numeric_data[self.feature_names]
        
        # Handle missing values
        if numeric_data.isnull().any().any():
            print("⚠️ Found missing values, filling with median...")
            numeric_data = numeric_data.fillna(numeric_data.median())
        
        return numeric_data
    
    def predict_single(self, input_data):
        """
        Make a single prediction.
        
        This method takes input data for a single sample and returns
        the predicted Pb rougher concentrate value.
        
        Args:
            input_data (dict or pd.DataFrame): Input features for one sample
            
        Returns:
            float: Predicted Pb rougher concentrate value
        """
        # Preprocess the input data
        processed_data = self.preprocess_input(input_data)
        
        # Make prediction
        prediction = self.model.predict(processed_data)[0]
        
        return prediction
    
    def predict_batch(self, input_data):
        """
        Make predictions for multiple samples.
        
        This method takes input data for multiple samples and returns
        predictions for all samples.
        
        Args:
            input_data (pd.DataFrame): Input features for multiple samples
            
        Returns:
            np.array: Array of predicted Pb rougher concentrate values
        """
        # Preprocess the input data
        processed_data = self.preprocess_input(input_data)
        
        # Make predictions
        predictions = self.model.predict(processed_data)
        
        return predictions
    
    def predict_with_confidence(self, input_data, n_iterations=100):
        """
        Make predictions with confidence intervals using bootstrapping.
        
        This method provides prediction confidence by using the model's
        internal structure (if available) or bootstrapping techniques.
        
        Args:
            input_data (dict or pd.DataFrame): Input features
            n_iterations (int): Number of iterations for confidence estimation
            
        Returns:
            dict: Dictionary containing prediction and confidence interval
        """
        processed_data = self.preprocess_input(input_data)
        
        # For Random Forest models, we can use the individual tree predictions
        if hasattr(self.model, 'estimators_'):
            predictions = []
            for estimator in self.model.estimators_:
                pred = estimator.predict(processed_data)[0]
                predictions.append(pred)
            
            mean_prediction = np.mean(predictions)
            std_prediction = np.std(predictions)
            confidence_interval = (mean_prediction - 2*std_prediction, mean_prediction + 2*std_prediction)
            
            return {
                'prediction': mean_prediction,
                'confidence_interval': confidence_interval,
                'std': std_prediction,
                'method': 'tree_variance'
            }
        else:
            # For other models, return single prediction
            prediction = self.model.predict(processed_data)[0]
            return {
                'prediction': prediction,
                'confidence_interval': (prediction, prediction),
                'std': 0.0,
                'method': 'single_prediction'
            }
    
    def get_model_info(self):
        """
        Get information about the loaded model.
        
        Returns:
            dict: Dictionary containing model information
        """
        info = {
            'model_type': type(self.model).__name__,
            'feature_count': len(self.feature_names) if self.feature_names else 'Unknown',
            'metadata': self.metadata
        }
        
        # Add model-specific information
        if hasattr(self.model, 'n_estimators'):
            info['n_estimators'] = self.model.n_estimators
        
        if hasattr(self.model, 'max_depth'):
            info['max_depth'] = self.model.max_depth
        
        return info


def main():
    """
    Main function demonstrating how to use the FlotationPredictor.
    
    This function shows examples of how to load the model and make predictions.
    """
    try:
        # Initialize the predictor
        predictor = FlotationPredictor()
        
        # Get model information
        model_info = predictor.get_model_info()
        print(f"\n📊 Model Information:")
        for key, value in model_info.items():
            print(f"   • {key}: {value}")
        
        # Example: Single prediction
        print(f"\n🔮 Example Single Prediction:")
        
        # Create sample input data (you would replace this with real data)
        sample_input = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 3.2,
            'Feed_Cu': 0.8,
            'Feed_Fe': 15.0,
            'Feed_SiO2': 45.0,
            'Feed_S': 2.1,
            'Feed_CaO': 8.5,
            'Feed_MgO': 2.3,
            'Feed_Al2O3': 12.0,
            'Feed_As': 0.15,
            'Feed_Sb': 0.08,
            'Feed_Bi': 0.02,
            'Feed_Cd': 0.05,
            'Feed_Au': 0.8,
            'Feed_Ag': 12.0,
            'Feed_Sn': 0.1,
            'Feed_Mo': 0.02,
            'Feed_W': 0.01,
            'Feed_Co': 0.05,
            'Feed_Ni': 0.1
        }
        
        # Make prediction
        prediction = predictor.predict_single(sample_input)
        print(f"   Input features: {len(sample_input)} features")
        print(f"   Predicted Pb Rougher Concentrate: {prediction:.2f}%")
        
        # Example: Prediction with confidence
        confidence_result = predictor.predict_with_confidence(sample_input)
        print(f"\n🎯 Prediction with Confidence:")
        print(f"   Prediction: {confidence_result['prediction']:.2f}%")
        print(f"   Confidence Interval: {confidence_result['confidence_interval'][0]:.2f}% - {confidence_result['confidence_interval'][1]:.2f}%")
        print(f"   Standard Deviation: {confidence_result['std']:.2f}%")
        print(f"   Method: {confidence_result['method']}")
        
        print(f"\n✅ Prediction system ready for use!")
        print(f"💡 Use predictor.predict_single(data) for single predictions")
        print(f"💡 Use predictor.predict_batch(data) for batch predictions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have run the training pipeline first to generate the model.")


if __name__ == "__main__":
    main()
