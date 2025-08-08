"""
Flotation Grade Prediction Models
================================

This script implements three models for predicting Pb grade in rougher concentrate:
1. Linear Regression - Baseline linear model
2. Random Forest - Non-linear ensemble model  
3. XGBoost - Advanced gradient boosting model

Target: Pb_Rougher_Conc_Pb (Lead grade in rougher concentrate)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Machine Learning
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression

# XGBoost
import xgboost as xgb
from xgboost import XGBRegressor

# Utilities
import joblib
import pickle
import os

# Set random seeds for reproducibility
np.random.seed(42)

class FlotationModelTrainer:
    """Trainer class for flotation grade prediction models"""
    
    def __init__(self, data_path, target_col='Pb_Rougher_Conc_Pb'):
        self.data_path = data_path
        self.target_col = target_col
        self.models = {}
        self.scalers = {}
        self.results = {}
        
    def load_and_prepare_data(self):
        """Load and prepare data for modeling"""
        print("Loading data...")
        self.df = pd.read_parquet(self.data_path)
        print(f"Data shape: {self.df.shape}")
        
        # Prepare features
        exclude_cols = [self.target_col, 'month', 'day', 'hour', 'minute']
        feature_cols = [col for col in self.df.columns if col not in exclude_cols]
        
        X = self.df[feature_cols]
        y = self.df[self.target_col]
        
        # Remove NaN values
        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask]
        y = y[mask]
        
        # Feature selection
        selector = SelectKBest(score_func=f_regression, k=20)
        X_selected = selector.fit_transform(X, y)
        self.selected_features = X.columns[selector.get_support()]
        X = X[self.selected_features]
        
        print(f"Selected {len(self.selected_features)} features")
        print(f"Final data shape: X={X.shape}, y={y.shape}")
        
        return X, y
    
    def create_time_series_split(self, X, y, test_size=0.2, val_size=0.2):
        """Create time series train/validation/test split"""
        n_samples = len(X)
        test_start = int(n_samples * (1 - test_size))
        val_start = int(test_start * (1 - val_size))
        
        X_train = X.iloc[:val_start]
        y_train = y.iloc[:val_start]
        
        X_val = X.iloc[val_start:test_start]
        y_val = y.iloc[val_start:test_start]
        
        X_test = X.iloc[test_start:]
        y_test = y.iloc[test_start:]
        
        print(f"Train set: {X_train.shape[0]} samples")
        print(f"Val set: {X_val.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def evaluate_model(self, y_true, y_pred, dataset_name):
        """Evaluate model performance"""
        mse = mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        rmse = np.sqrt(mse)
        
        print(f"{dataset_name}:")
        print(f"  MSE: {mse:.4f}")
        print(f"  MAE: {mae:.4f}")
        print(f"  RMSE: {rmse:.4f}")
        print(f"  R²: {r2:.4f}")
        print()
        
        return {'mse': mse, 'mae': mae, 'rmse': rmse, 'r2': r2}
    
    def train_linear_regression(self, X_train, X_val, X_test, y_train, y_val, y_test):
        """Train Linear Regression model"""
        print("=== Training Linear Regression Model ===")
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_train_pred = model.predict(X_train_scaled)
        y_val_pred = model.predict(X_val_scaled)
        y_test_pred = model.predict(X_test_scaled)
        
        # Evaluate
        results = {}
        results['train'] = self.evaluate_model(y_train, y_train_pred, "Train")
        results['val'] = self.evaluate_model(y_val, y_val_pred, "Validation")
        results['test'] = self.evaluate_model(y_test, y_test_pred, "Test")
        
        # Store model and scaler
        self.models['linear_regression'] = model
        self.scalers['linear_regression'] = scaler
        self.results['linear_regression'] = results
        
        return model, scaler, results
    
    def train_random_forest(self, X_train, X_val, X_test, y_train, y_val, y_test):
        """Train Random Forest model"""
        print("=== Training Random Forest Model ===")
        
        # Train model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # Predictions
        y_train_pred = model.predict(X_train)
        y_val_pred = model.predict(X_val)
        y_test_pred = model.predict(X_test)
        
        # Evaluate
        results = {}
        results['train'] = self.evaluate_model(y_train, y_train_pred, "Train")
        results['val'] = self.evaluate_model(y_val, y_val_pred, "Validation")
        results['test'] = self.evaluate_model(y_test, y_test_pred, "Test")
        
        # Store model
        self.models['random_forest'] = model
        self.results['random_forest'] = results
        
        return model, results
    
    def create_lagged_features(self, X, y, lag_steps=3):
        """Create lagged features for time series modeling"""
        X_lagged = X.copy()
        
        for lag in range(1, lag_steps + 1):
            for col in X.columns:
                X_lagged[f'{col}_lag_{lag}'] = X[col].shift(lag)
        
        # Remove rows with NaN values from lagging
        X_lagged = X_lagged.dropna()
        y_lagged = y[X_lagged.index]
        
        return X_lagged, y_lagged
    
    def train_xgboost(self, X_train, X_val, X_test, y_train, y_val, y_test, lag_steps=3):
        """Train XGBoost model with lagged features"""
        print("=== Training XGBoost Model ===")
        
        # Create lagged features
        X_train_lagged, y_train_lagged = self.create_lagged_features(X_train, y_train, lag_steps)
        X_val_lagged, y_val_lagged = self.create_lagged_features(X_val, y_val, lag_steps)
        X_test_lagged, y_test_lagged = self.create_lagged_features(X_test, y_test, lag_steps)
        
        print(f"XGBoost features shape:")
        print(f"Train: {X_train_lagged.shape}")
        print(f"Validation: {X_val_lagged.shape}")
        print(f"Test: {X_test_lagged.shape}")
        
        # Scale the data
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_lagged)
        X_val_scaled = scaler.transform(X_val_lagged)
        X_test_scaled = scaler.transform(X_test_lagged)
        
        # Convert back to DataFrame for feature names
        X_train_scaled_df = pd.DataFrame(X_train_scaled, index=X_train_lagged.index, columns=X_train_lagged.columns)
        X_val_scaled_df = pd.DataFrame(X_val_scaled, index=X_val_lagged.index, columns=X_val_lagged.columns)
        X_test_scaled_df = pd.DataFrame(X_test_scaled, index=X_test_lagged.index, columns=X_test_lagged.columns)
        
        # Build and train XGBoost model
        model = XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            early_stopping_rounds=20,
            eval_metric='rmse'
        )
        
        # Train model with early stopping
        model.fit(
            X_train_scaled_df, y_train_lagged,
            eval_set=[(X_val_scaled_df, y_val_lagged)],
            verbose=1
        )
        
        # Predictions
        y_train_pred = model.predict(X_train_scaled_df)
        y_val_pred = model.predict(X_val_scaled_df)
        y_test_pred = model.predict(X_test_scaled_df)
        
        # Evaluate
        results = {}
        results['train'] = self.evaluate_model(y_train_lagged, y_train_pred, "Train")
        results['val'] = self.evaluate_model(y_val_lagged, y_val_pred, "Validation")
        results['test'] = self.evaluate_model(y_test_lagged, y_test_pred, "Test")
        
        # Store model and scaler
        self.models['xgboost'] = model
        self.scalers['xgboost'] = scaler
        self.results['xgboost'] = results
        self.lag_steps = lag_steps
        self.feature_names = X_train_lagged.columns.tolist()
        
        return model, scaler, results
    
    def compare_models(self):
        """Compare all models and select the best one"""
        print("=== Model Comparison ===")
        
        models = ['linear_regression', 'random_forest', 'xgboost']
        model_names = ['Linear Regression', 'Random Forest', 'XGBoost']
        
        comparison_data = []
        for model_name, display_name in zip(models, model_names):
            if model_name in self.results:
                for dataset in ['train', 'val', 'test']:
                    comparison_data.append({
                        'Model': display_name,
                        'Dataset': dataset,
                        'MSE': self.results[model_name][dataset]['mse'],
                        'MAE': self.results[model_name][dataset]['mae'],
                        'RMSE': self.results[model_name][dataset]['rmse'],
                        'R²': self.results[model_name][dataset]['r2']
                    })
        
        comparison_df = pd.DataFrame(comparison_data)
        print(comparison_df.round(4))
        
        # Determine best model
        test_results = comparison_df[comparison_df['Dataset'] == 'test']
        best_model_idx = test_results['R²'].idxmax()
        best_model = test_results.loc[best_model_idx, 'Model']
        
        print(f"\n🏆 Best Model: {best_model}")
        print(f"Test R² Score: {test_results.loc[best_model_idx, 'R²']:.4f}")
        print(f"Test RMSE: {test_results.loc[best_model_idx, 'RMSE']:.4f}")
        
        return best_model, comparison_df
    
    def save_best_model(self, best_model, model_dir=None):
        """Save the best performing model"""
        if model_dir is None:
            model_dir = r'C:\@Python Projects\TUT Research Project\Models'
        
        os.makedirs(model_dir, exist_ok=True)
        
        # Map display name to model key
        model_mapping = {
            'Linear Regression': 'linear_regression',
            'Random Forest': 'random_forest',
            'XGBoost': 'xgboost'
        }
        
        model_key = model_mapping[best_model]
        
        # Save model and preprocessing
        if model_key == 'linear_regression':
            joblib.dump(self.models[model_key], os.path.join(model_dir, 'linear_regression_model.pkl'))
            joblib.dump(self.scalers[model_key], os.path.join(model_dir, 'linear_regression_scaler.pkl'))
            model_type = 'linear_regression'
        elif model_key == 'random_forest':
            joblib.dump(self.models[model_key], os.path.join(model_dir, 'random_forest_model.pkl'))
            model_type = 'random_forest'
        else:  # XGBoost
            joblib.dump(self.models[model_key], os.path.join(model_dir, 'xgboost_model.pkl'))
            joblib.dump(self.scalers[model_key], os.path.join(model_dir, 'xgboost_scaler.pkl'))
            model_type = 'xgboost'
        
        # Save model information
        model_info = {
            'model_type': model_type,
            'best_model': best_model,
            'feature_columns': list(self.selected_features),
            'target_column': self.target_col,
            'lag_steps': getattr(self, 'lag_steps', None),
            'feature_names': getattr(self, 'feature_names', None),
            'test_performance': self.results[model_key]['test']
        }
        
        with open(os.path.join(model_dir, 'model_info.pkl'), 'wb') as f:
            pickle.dump(model_info, f)
        
        print(f"✅ Best model ({best_model}) saved to {model_dir}")
        print(f"Model type: {model_type}")
        print(f"Test R²: {model_info['test_performance']['r2']:.4f}")
        print(f"Test RMSE: {model_info['test_performance']['rmse']:.4f}")
        
        return model_info
    
    def train_all_models(self):
        """Train all three models and select the best one"""
        # Load and prepare data
        X, y = self.load_and_prepare_data()
        
        # Create time series split
        X_train, X_val, X_test, y_train, y_val, y_test = self.create_time_series_split(X, y)
        
        # Train models
        self.train_linear_regression(X_train, X_val, X_test, y_train, y_val, y_test)
        self.train_random_forest(X_train, X_val, X_test, y_train, y_val, y_test)
        self.train_xgboost(X_train, X_val, X_test, y_train, y_val, y_test)
        
        # Compare and select best model
        best_model, comparison_df = self.compare_models()
        
        # Save best model
        model_info = self.save_best_model(best_model)
        
        return best_model, comparison_df, model_info

def main():
    """Main function to run the complete modeling pipeline"""
    # Initialize trainer
    data_path = r'C:\@Python Projects\TUT Research Project\Clean_Data\HZL_RA4_Pb_Rougher_2025-07_clean.parquet'
    trainer = FlotationModelTrainer(data_path)
    
    # Train all models
    best_model, comparison_df, model_info = trainer.train_all_models()
    
    print("\n" + "="*50)
    print("MODELING COMPLETE!")
    print("="*50)
    print(f"Best Model: {best_model}")
    print(f"Ready for Digital Twin Integration!")
    
    return trainer, best_model, comparison_df, model_info

if __name__ == "__main__":
    trainer, best_model, comparison_df, model_info = main()
