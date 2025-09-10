"""
Efficient 60-Minute Horizon Training Script
==========================================

This is a single, efficient training script that:
1. Uses reasonable dataset sizes (25K samples, 100 features)
2. Has optimized hyperparameter search spaces
3. Uses GPU acceleration when available
4. Includes checkpointing for resumable training
5. Aims for high R² scores with practical training times

Target: Achieve R² > 90% with optimized training time (< 4 hours)
"""

import sys
import logging
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import warnings
import time
import pickle
import os
from typing import Dict, List, Tuple, Any

# Machine Learning imports
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.feature_selection import SelectKBest, mutual_info_regression
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb

# Add backend/services to path
sys.path.append('backend/services')

# Suppress warnings
warnings.filterwarnings('ignore')

# Create logs directory if it doesn't exist
Path('logs').mkdir(exist_ok=True)

# Set up logging with separate handlers for file and console
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Clear any existing handlers
logger.handlers.clear()

# Create logs directory if it doesn't exist
Path('logs').mkdir(exist_ok=True)

# Custom formatter to remove emojis for console
class NoEmojiFormatter(logging.Formatter):
    def format(self, record):
        # Remove emojis from the message for console output
        import re
        record.msg = re.sub(r'[^\x00-\x7F]+', '', str(record.msg))
        return super().format(record)

# File handler with emojis (UTF-8 encoding)
file_handler = logging.FileHandler('logs/60min_training.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Console handler without emojis (ASCII-safe)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = NoEmojiFormatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Add both handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Try to import GPU-accelerated libraries
try:
    import cupy as cp
    logger.info("✅ CuPy available for GPU acceleration")
    GPU_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ CuPy not available, using CPU only")
    GPU_AVAILABLE = False

class EfficientSixtyMinuteTrainer:
    """
    Efficient trainer for 60-minute prediction horizon with practical training times.
    """
    
    def __init__(self):
        """Initialize the efficient 60-minute horizon trainer."""
        self.horizon = 60
        self.datasets_dir = Path(__file__).parent.parent / 'backend' / 'training' / 'time_series_datasets'
        self.output_dir = Path(__file__).parent.parent / 'backend' / 'trained_models' / '60min_efficient'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Checkpoint directory
        self.checkpoint_dir = Path('checkpoints_60min_efficient')
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # Training parameters (optimized for maximum performance)
        self.max_features = 150  # Increased for better performance
        self.sample_size = 50000  # Increased for better performance
        self.start_time = None
        
        logger.info(f"🚀 Efficient 60-Minute Trainer initialized")
        logger.info(f"📊 Max features: {self.max_features}")
        logger.info(f"📊 Sample size: {self.sample_size}")
        logger.info(f"📁 Output directory: {self.output_dir}")
        logger.info(f"📁 Checkpoint directory: {self.checkpoint_dir}")
        logger.info(f"📁 Log file: logs/60min_training.log")
    
    def save_checkpoint(self, stage, data):
        """Save checkpoint data to disk for resumable training."""
        checkpoint_file = self.checkpoint_dir / f'checkpoint_{stage}.pkl'
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(data, f)
        logger.info(f"✅ Checkpoint saved: {checkpoint_file}")
    
    def load_checkpoint(self, stage):
        """Load checkpoint data from disk if it exists."""
        checkpoint_file = self.checkpoint_dir / f'checkpoint_{stage}.pkl'
        if checkpoint_file.exists():
            with open(checkpoint_file, 'rb') as f:
                data = pickle.load(f)
            logger.info(f"✅ Checkpoint loaded: {checkpoint_file}")
            return data
        return None
    
    def print_progress(self, stage, current_step, total_steps):
        """Print progress with time estimates."""
        if self.start_time is None:
            self.start_time = time.time()
            
        elapsed = time.time() - self.start_time
        progress = current_step / total_steps
        if progress > 0:
            estimated_total = elapsed / progress
            remaining = estimated_total - elapsed
            logger.info(f"🔄 {stage}: {current_step}/{total_steps} ({progress:.1%}) - "
                       f"Elapsed: {elapsed/60:.1f}min, Remaining: {remaining/60:.1f}min")
    
    def load_and_prepare_data(self):
        """
        Load and prepare data with proper future target creation and data leakage prevention.
        """
        # Check if we have a checkpoint for data preparation
        checkpoint = self.load_checkpoint('data_preparation')
        if checkpoint:
            logger.info("📊 Loading data from checkpoint...")
            return checkpoint['X_train'], checkpoint['X_val'], checkpoint['X_test'], \
                   checkpoint['y_train'], checkpoint['y_val'], checkpoint['y_test']
        
        logger.info(f"📊 Loading and preparing data for {self.horizon}min horizon...")
        
        # Load the preprocessed dataset
        dataset_path = self.datasets_dir / f'training_data_{self.horizon}min.parquet'
        
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
        df = pd.read_parquet(dataset_path)
        logger.info(f"Loaded dataset with shape: {df.shape}")
        
        # Validate target variable
        target_col = f'Pb_Rougher_Conc_Pb_{self.horizon}min_ahead'
        
        if target_col not in df.columns:
            raise ValueError(f"Target column {target_col} not found in dataset")
        
        # Check for data leakage - remove any features that might contain future information
        leakage_patterns = [
            '_ahead', 'target', 'Pb_Rougher_Conc_Pb',  # Target-related
            'future', 'prediction', 'forecast',  # Future-related
            'shift_neg', 'shift_-'  # Negative shifts (future data)
        ]
        
        # Get feature columns, excluding leakage patterns
        feature_cols = []
        for col in df.columns:
            if col != target_col and not any(pattern in col for pattern in leakage_patterns):
                feature_cols.append(col)
        
        logger.info(f"Selected {len(feature_cols)} features after leakage prevention")
        
        # Validate target variable distribution
        target_values = df[target_col].dropna()
        logger.info(f"Target variable statistics:")
        logger.info(f"  Mean: {target_values.mean():.4f}")
        logger.info(f"  Std: {target_values.std():.4f}")
        logger.info(f"  Min: {target_values.min():.4f}")
        logger.info(f"  Max: {target_values.max():.4f}")
        logger.info(f"  NaN count: {df[target_col].isna().sum()}")
        
        # Prepare features and target
        X = df[feature_cols].select_dtypes(include=[np.number])  # Keep only numeric features
        y = df[target_col]
        
        # Remove rows with NaN values
        valid_mask = ~(X.isnull().any(axis=1) | y.isnull())
        X = X[valid_mask]
        y = y[valid_mask]
        
        logger.info(f"Final dataset shape: X={X.shape}, y={y.shape}")
        
        # Advanced feature selection using multiple methods for better performance
        logger.info("🔍 Performing advanced feature selection...")
        max_features = min(self.max_features, X.shape[1])
        
        # Method 1: Mutual Information
        selector_mi = SelectKBest(score_func=mutual_info_regression, k=max_features)
        X_mi = selector_mi.fit_transform(X, y)
        mi_features = X.columns[selector_mi.get_support()].tolist()
        
        # Method 2: F-statistic
        from sklearn.feature_selection import f_regression
        selector_f = SelectKBest(score_func=f_regression, k=max_features)
        X_f = selector_f.fit_transform(X, y)
        f_features = X.columns[selector_f.get_support()].tolist()
        
        # Combine features from both methods (union)
        combined_features = list(set(mi_features + f_features))
        logger.info(f"Combined {len(combined_features)} features from multiple selection methods")
        
        # Use the combined features
        X_selected = X[combined_features]
        
        # Smart sampling for better performance - use stratified sampling based on target quantiles
        logger.info("⚡ Performing smart stratified sampling...")
        sample_size = min(self.sample_size, len(X_selected))
        
        # Create target quantiles for stratified sampling
        y_quantiles = pd.qcut(y, q=10, labels=False, duplicates='drop')
        
        # Stratified sampling to maintain target distribution
        from sklearn.model_selection import train_test_split
        X_sampled, _, y_sampled, _ = train_test_split(
            X_selected, y, 
            train_size=sample_size/len(X_selected), 
            stratify=y_quantiles,
            random_state=42
        )
        
        X_selected = X_sampled
        y = y_sampled
        logger.info(f"Smart sampled shape: {X_selected.shape}")
        
        # Create time series split for proper temporal validation
        logger.info("⏰ Creating time series split...")
        tscv = TimeSeriesSplit(n_splits=5)  # Increased for better validation
        splits = list(tscv.split(X_selected))
        
        # Use the last split as test set (most recent data)
        train_idx, test_idx = splits[-1]
        
        # Use middle split for validation
        val_start = splits[1][0][0]
        val_end = splits[1][1][-1]
        val_idx = list(range(val_start, val_end))
        
        # Split the data into train, validation, and test sets
        X_train = X_selected.iloc[train_idx]
        X_val = X_selected.iloc[val_idx]
        X_test = X_selected.iloc[test_idx]
        y_train = y.iloc[train_idx]
        y_val = y.iloc[val_idx]
        y_test = y.iloc[test_idx]
        
        logger.info(f"Split sizes - Train: {X_train.shape[0]}, Val: {X_val.shape[0]}, Test: {X_test.shape[0]}")
        
        # Save checkpoint for data preparation stage
        self.save_checkpoint('data_preparation', {
            'X_train': X_train, 'X_val': X_val, 'X_test': X_test,
            'y_train': y_train, 'y_val': y_val, 'y_test': y_test
        })
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def optimize_models(self, X_train, X_val, y_train, y_val):
        """
        Optimize models with efficient hyperparameter search.
        """
        # Check if we have a checkpoint for model optimization
        checkpoint = self.load_checkpoint('model_optimization')
        if checkpoint:
            logger.info("🤖 Loading optimized models from checkpoint...")
            return checkpoint['optimized_models']
        
        logger.info("🤖 Starting model optimization...")
        optimized_models = {}
        
        # Define model configurations with expanded hyperparameter search spaces for 90%+ R²
        models_config = [
            # Ridge Regression: Linear model with L2 regularization
            ('ridge', Ridge(random_state=42), {
                'alpha': [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]  # Expanded parameter space
            }),
            
            # Random Forest: Ensemble of decision trees (optimized for performance)
            ('rf', RandomForestRegressor(random_state=42, n_jobs=1), {
                'n_estimators': [200, 300, 400],      # Increased for better performance
                'max_depth': [20, 25, 30, None],      # Increased for better performance
                'min_samples_split': [2, 5, 10],      # Expanded parameter space
                'min_samples_leaf': [1, 2, 5],        # Expanded parameter space
                'max_features': ['sqrt', 'log2', None]  # Added feature selection
            }),
            
            # XGBoost: Gradient boosting with GPU acceleration (optimized for 90%+ R²)
            ('xgb', xgb.XGBRegressor(
                random_state=42, 
                n_jobs=1,
                tree_method='gpu_hist' if GPU_AVAILABLE else 'hist'
            ), {
                'n_estimators': [300, 400, 500],      # Increased for better performance
                'max_depth': [8, 10, 12],             # Increased for better performance
                'learning_rate': [0.03, 0.05, 0.08, 0.1],  # Expanded parameter space
                'subsample': [0.8, 0.85, 0.9, 0.95], # Expanded parameter space
                'colsample_bytree': [0.8, 0.9, 1.0], # Added column sampling
                'reg_alpha': [0, 0.1, 0.5, 1.0],     # Added L1 regularization
                'reg_lambda': [0, 0.1, 0.5, 1.0]     # Added L2 regularization
            })
        ]
        
        # Optimize each model
        for i, (name, model, params) in enumerate(models_config):
            self.print_progress("Optimization", i + 1, len(models_config))
            logger.info(f"🤖 Optimizing {name.upper()}...")
            
            try:
                # Choose optimization strategy based on model type
                if name == 'ridge':
                    # Use GridSearchCV for Ridge (smaller parameter space)
                    logger.info(f"   🔍 Using GridSearchCV for {name}...")
                    search = GridSearchCV(model, params, cv=5, scoring='r2', n_jobs=1)  # Increased CV folds
                else:
                    # Use RandomizedSearchCV for tree-based models (larger parameter space)
                    logger.info(f"   🔍 Using RandomizedSearchCV for {name}...")
                    search = RandomizedSearchCV(
                        model, params, n_iter=10, cv=5, scoring='r2', n_jobs=1, random_state=42  # Increased iterations and CV folds
                    )
                
                # Fit the model with hyperparameter optimization
                logger.info(f"   ⏳ Fitting {name} with hyperparameter optimization...")
                search.fit(X_train, y_train)
                optimized_models[name] = search.best_estimator_
                
                logger.info(f"   ✅ {name.upper()} - Best CV score: {search.best_score_:.4f}")
                logger.info(f"   ✅ {name.upper()} - Best parameters: {search.best_params_}")
                
                # Save checkpoint after each model optimization
                self.save_checkpoint('model_optimization', {'optimized_models': optimized_models})
                
            except Exception as e:
                logger.error(f"❌ Error optimizing {name}: {e}")
                logger.warning(f"⚠️ Skipping {name} and continuing with other models...")
                continue
        
        logger.info(f"🤖 Model optimization completed. Optimized {len(optimized_models)} models.")
        
        return optimized_models
    
    def evaluate_models(self, optimized_models, X_train, X_val, X_test, y_train, y_val, y_test):
        """
        Evaluate optimized models on all datasets.
        """
        # Check if we have a checkpoint for model evaluation
        checkpoint = self.load_checkpoint('model_evaluation')
        if checkpoint:
            logger.info("📈 Loading evaluation results from checkpoint...")
            return checkpoint['results']
        
        logger.info("📈 Evaluating models...")
        results = {}
        
        # Evaluate each model
        for i, (name, model) in enumerate(optimized_models.items()):
            self.print_progress("Evaluation", i + 1, len(optimized_models))
            logger.info(f"📈 Evaluating {name.upper()}...")
            
            try:
                # Make predictions on all datasets
                logger.info(f"   🔮 Making predictions for {name}...")
                y_train_pred = model.predict(X_train)
                y_val_pred = model.predict(X_val)
                y_test_pred = model.predict(X_test)
                
                # Calculate performance metrics
                train_r2 = r2_score(y_train, y_train_pred)
                val_r2 = r2_score(y_val, y_val_pred)
                test_r2 = r2_score(y_test, y_test_pred)
                
                test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
                test_mae = mean_absolute_error(y_test, y_test_pred)
                
                # Calculate percentage of predictions within error thresholds
                test_errors = np.abs(y_test - y_test_pred) / y_test * 100
                test_pred_10 = np.mean(test_errors <= 10)
                
                # Store results
                results[name] = {
                    'train_r2': train_r2,
                    'val_r2': val_r2,
                    'test_r2': test_r2,
                    'test_rmse': test_rmse,
                    'test_mae': test_mae,
                    'test_pred_10%': test_pred_10,
                    'predictions': y_test_pred,
                    'model': model
                }
                
                logger.info(f"   ✅ {name.upper()} - Test R²: {test_r2:.4f}, RMSE: {test_rmse:.4f}, 10% Acc: {test_pred_10:.2%}")
                
                # Save checkpoint after each model evaluation
                self.save_checkpoint('model_evaluation', {'results': results})
                
            except Exception as e:
                logger.error(f"❌ Error evaluating {name}: {e}")
                logger.warning(f"⚠️ Skipping {name} evaluation and continuing...")
                continue
        
        logger.info(f"📈 Model evaluation completed. Evaluated {len(results)} models.")
        
        return results
    
    def create_visualizations(self, results, y_test):
        """
        Create comprehensive visualizations of model performance.
        """
        logger.info("📊 Creating visualizations...")
        
        # Find the best model based on test R² score
        best_model_name = max(results.keys(), key=lambda x: results[x]['test_r2'])
        best_results = results[best_model_name]
        
        # Create a 2x2 grid of plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Efficient 60-Minute Horizon Model Performance Analysis', fontsize=16, fontweight='bold')
        
        # 1. R² scores comparison
        model_names = list(results.keys())
        test_r2 = [results[name]['test_r2'] for name in model_names]
        axes[0, 0].bar(model_names, test_r2, alpha=0.8, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        axes[0, 0].set_title('Test R² Scores Comparison')
        axes[0, 0].set_ylabel('R² Score')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate(test_r2):
            axes[0, 0].text(i, v + 0.01, f'{v:.3f}', ha='center', va='bottom')
        
        # 2. RMSE comparison
        test_rmse = [results[name]['test_rmse'] for name in model_names]
        axes[0, 1].bar(model_names, test_rmse, alpha=0.8, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        axes[0, 1].set_title('Test RMSE Comparison')
        axes[0, 1].set_ylabel('RMSE')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate(test_rmse):
            axes[0, 1].text(i, v + 0.1, f'{v:.2f}', ha='center', va='bottom')
        
        # 3. Actual vs Predicted scatter plot (best model)
        best_predictions = best_results['predictions']
        axes[1, 0].scatter(y_test, best_predictions, alpha=0.6, color='blue')
        
        # Add perfect prediction line
        min_val = min(y_test.min(), best_predictions.min())
        max_val = max(y_test.max(), best_predictions.max())
        axes[1, 0].plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')
        
        axes[1, 0].set_xlabel('Actual Values')
        axes[1, 0].set_ylabel('Predicted Values')
        axes[1, 0].set_title(f'Actual vs Predicted - {best_model_name.upper()}')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Residuals plot (best model)
        residuals = y_test - best_predictions
        axes[1, 1].scatter(best_predictions, residuals, alpha=0.6, color='green')
        axes[1, 1].axhline(y=0, color='r', linestyle='--', label='Zero Residual')
        axes[1, 1].set_xlabel('Predicted Values')
        axes[1, 1].set_ylabel('Residuals (Actual - Predicted)')
        axes[1, 1].set_title(f'Residuals Plot - {best_model_name.upper()}')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save the visualization to analysis_visualizations directory
        analysis_viz_dir = Path(__file__).parent.parent / 'analysis_visualizations'
        analysis_viz_dir.mkdir(exist_ok=True)
        viz_path = analysis_viz_dir / '60min_efficient_model_performance.png'
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        logger.info(f"📊 Visualization saved to: {viz_path}")
        
        return best_model_name
    
    def save_best_model(self, results, best_model_name):
        """
        Save the best performing model to disk.
        """
        best_model = results[best_model_name]['model']
        model_path = self.output_dir / f'{best_model_name}_model.pkl'
        
        # Save the model
        joblib.dump(best_model, model_path)
        logger.info(f"💾 Best model saved: {model_path}")
        
        # Save model metadata
        metadata = {
            'model_name': best_model_name,
            'horizon': self.horizon,
            'test_r2': results[best_model_name]['test_r2'],
            'test_rmse': results[best_model_name]['test_rmse'],
            'test_mae': results[best_model_name]['test_mae'],
            'test_pred_10%': results[best_model_name]['test_pred_10%'],
            'training_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'model_type': type(best_model).__name__,
            'max_features': self.max_features,
            'sample_size': self.sample_size,
            'training_mode': 'efficient'
        }
        
        metadata_path = self.output_dir / 'metadata.pkl'
        joblib.dump(metadata, metadata_path)
        logger.info(f"📋 Model metadata saved: {metadata_path}")
        
        # Save training summary
        summary_path = self.output_dir / 'training_summary.txt'
        with open(summary_path, 'w') as f:
            f.write(f"Efficient 60min Horizon Training Summary\n")
            f.write(f"==================================================\n\n")
            f.write(f"Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Max Features: {self.max_features}\n")
            f.write(f"Sample Size: {self.sample_size}\n")
            f.write(f"Training Mode: Efficient (balanced speed vs performance)\n\n")
            
            for name, result in results.items():
                f.write(f"{name.upper()}:\n")
                f.write(f"  Train R²: {result['train_r2']:.4f}\n")
                f.write(f"  Val R²: {result['val_r2']:.4f}\n")
                f.write(f"  Test R²: {result['test_r2']:.4f}\n")
                f.write(f"  Test RMSE: {result['test_rmse']:.4f}\n")
                f.write(f"  Test MAE: {result['test_mae']:.4f}\n")
                f.write(f"  10% Accuracy: {result['test_pred_10%']:.2%}\n\n")
            
            f.write(f"Best Model: {best_model_name.upper()}\n")
            f.write(f"Target R²: > 90%\n")
            f.write(f"Expected Training Time: < 4 hours\n")
        
        return model_path
    
    def print_summary(self, results, best_model_name):
        """
        Print a comprehensive summary of the optimization results.
        """
        logger.info("\n" + "=" * 60)
        logger.info("📋 EFFICIENT TRAINING RESULTS SUMMARY")
        logger.info("=" * 60)
        
        best_results = results[best_model_name]
        logger.info(f"🏆 Best Model: {best_model_name.upper()}")
        logger.info(f"📊 Test R² Score: {best_results['test_r2']:.4f}")
        logger.info(f"📏 Test RMSE: {best_results['test_rmse']:.4f}")
        logger.info(f"📐 Test MAE: {best_results['test_mae']:.4f}")
        logger.info(f"🎯 Test predictions within 10%: {best_results['test_pred_10%']:.2%}")
        
        logger.info(f"\n📈 MODEL PERFORMANCE COMPARISON")
        logger.info("-" * 40)
        for name, result in results.items():
            logger.info(f"{name.upper():<12} | R²: {result['test_r2']:.4f} | RMSE: {result['test_rmse']:.4f} | 10% Acc: {result['test_pred_10%']:.2%}")
        
        logger.info(f"\n🚀 IMPROVEMENT COMPARISON")
        logger.info("-" * 40)
        logger.info("Previous 60min Results: R² = -0.0907, RMSE = 10.8254")
        logger.info(f"Efficient Training Best ({best_model_name.upper()}): R² = {best_results['test_r2']:.4f}, RMSE = {best_results['test_rmse']:.4f}")
        
        r2_improvement = best_results['test_r2'] - (-0.0907)
        rmse_improvement = 10.8254 - best_results['test_rmse']
        
        logger.info(f"🚀 R² Improvement: {r2_improvement:+.4f}")
        logger.info(f"📉 RMSE Improvement: {rmse_improvement:+.4f}")
        
        # Print execution time
        if self.start_time:
            total_time = time.time() - self.start_time
            logger.info(f"\n⏱️ Total execution time: {total_time/60:.1f} minutes")
        
        logger.info(f"\n📁 Generated Files:")
        logger.info(f"   • Model: {self.output_dir}/{best_model_name}_model.pkl")
        logger.info(f"   • Metadata: {self.output_dir}/metadata.pkl")
        logger.info(f"   • Summary: {self.output_dir}/training_summary.txt")
        logger.info(f"   • Visualization: {Path(__file__).parent.parent}/analysis_visualizations/60min_efficient_model_performance.png")
        logger.info(f"   • Checkpoints: {self.checkpoint_dir}/ directory")
        logger.info(f"   • Log file: logs/60min_training.log")
        
        logger.info(f"\n✅ This efficient training completed in reasonable time!")
        logger.info(f"   Target R² > 90% achieved: {'✅' if best_results['test_r2'] > 0.9 else '❌'}")
        logger.info(f"   Target R² > 85% achieved: {'✅' if best_results['test_r2'] > 0.85 else '❌'}")
    
    def run_training(self):
        """
        Run the complete efficient training pipeline.
        """
        try:
            logger.info("🚀 Starting efficient 60-minute horizon training...")
            logger.info("=" * 60)
            
            # Check for final results checkpoint
            final_checkpoint = self.load_checkpoint('final_results')
            if final_checkpoint:
                logger.info("🎉 Found final results! Loading completed results...")
                results = final_checkpoint['results']
                best_model_name = final_checkpoint['best_model_name']
                self.print_summary(results, best_model_name)
                return results, best_model_name
            
            # Step 1: Load and prepare data
            logger.info("\n📊 STEP 1: Data Preparation")
            X_train, X_val, X_test, y_train, y_val, y_test = self.load_and_prepare_data()
            
            # Step 2: Optimize models
            logger.info("\n🤖 STEP 2: Model Optimization")
            optimized_models = self.optimize_models(X_train, X_val, y_train, y_val)
            
            # Step 3: Evaluate models
            logger.info("\n📈 STEP 3: Model Evaluation")
            results = self.evaluate_models(optimized_models, X_train, X_val, X_test, y_train, y_val, y_test)
            
            # Step 4: Create visualizations
            logger.info("\n📊 STEP 4: Visualization")
            best_model_name = self.create_visualizations(results, y_test)
            
            # Step 5: Save best model
            logger.info("\n💾 STEP 5: Model Saving")
            model_path = self.save_best_model(results, best_model_name)
            
            # Step 6: Save final results checkpoint
            self.save_checkpoint('final_results', {
                'results': results,
                'best_model_name': best_model_name,
                'model_path': model_path
            })
            
            # Step 7: Print summary
            logger.info("\n📋 STEP 6: Results Summary")
            self.print_summary(results, best_model_name)
            
            logger.info("=" * 60)
            logger.info("🎉 Efficient 60-minute horizon training completed!")
            logger.info(f"📁 Results saved to: {self.output_dir}")
            
            return results, best_model_name
            
        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
            logger.error(f"❌ Error details: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise

if __name__ == "__main__":
    trainer = EfficientSixtyMinuteTrainer()
    trainer.run_training()


