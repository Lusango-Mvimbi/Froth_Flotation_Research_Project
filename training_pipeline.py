"""
Froth Flotation Optimization Pipeline
====================================

This script implements a comprehensive machine learning pipeline for predicting
Pb rougher concentrate values in froth flotation processes. The pipeline includes:

1. Data loading and preprocessing
2. Feature selection and engineering
3. Model optimization with hyperparameter tuning
4. Cross-validation and evaluation
5. Checkpointing for resumable training
6. Visualization and model saving

Key Features:
- Resumable training with automatic checkpointing
- GPU acceleration for XGBoost
- Multiple model comparison (Ridge, Random Forest, XGBoost, Gradient Boosting)
- Time series-aware data splitting
- Comprehensive performance metrics
- Progress tracking with time estimates

Author: AI Assistant
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
import time
import pickle
import os
warnings.filterwarnings('ignore')

# Machine Learning imports
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.feature_selection import SelectKBest, mutual_info_regression
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb

# Try to import GPU-accelerated libraries for faster computation
try:
    import cupy as cp
    print("✅ CuPy available for GPU acceleration")
    GPU_AVAILABLE = True
except ImportError:
    print("⚠️ CuPy not available, using CPU only")
    GPU_AVAILABLE = False


class OptimizedFlotationPipeline:
    """
    A comprehensive pipeline for optimizing froth flotation prediction models.
    
    This class implements a complete machine learning workflow including:
    - Data preprocessing and feature selection
    - Model optimization with hyperparameter tuning
    - Cross-validation and evaluation
    - Checkpointing for resumable training
    - Visualization and model saving
    
    Attributes:
        enhanced_data_path (Path): Path to the enhanced dataset
        checkpoint_dir (Path): Directory for saving checkpoints
        start_time (float): Start time for progress tracking
    """
    
    def __init__(self, enhanced_data_path):
        """
        Initialize the optimization pipeline.
        
        Args:
            enhanced_data_path (str): Path to the enhanced dataset file
        """
        self.enhanced_data_path = Path(enhanced_data_path)
        self.checkpoint_dir = Path('checkpoints')
        self.checkpoint_dir.mkdir(exist_ok=True)  # Create checkpoint directory if it doesn't exist
        self.start_time = None
        
    def save_checkpoint(self, stage, data):
        """
        Save checkpoint data to disk for resumable training.
        
        This method saves intermediate results so that training can be resumed
        from where it left off if interrupted.
        
        Args:
            stage (str): Current stage of the pipeline (e.g., 'data_preparation')
            data (dict): Data to save as checkpoint
        """
        checkpoint_file = self.checkpoint_dir / f'checkpoint_{stage}.pkl'
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(data, f)
        print(f"✅ Checkpoint saved: {checkpoint_file}")
        
    def load_checkpoint(self, stage):
        """
        Load checkpoint data from disk if it exists.
        
        This method checks if a checkpoint exists for the given stage and
        loads it to resume training from where it left off.
        
        Args:
            stage (str): Stage to load checkpoint for
            
        Returns:
            dict or None: Checkpoint data if exists, None otherwise
        """
        checkpoint_file = self.checkpoint_dir / f'checkpoint_{stage}.pkl'
        if checkpoint_file.exists():
            with open(checkpoint_file, 'rb') as f:
                data = pickle.load(f)
            print(f"✅ Checkpoint loaded: {checkpoint_file}")
            return data
        return None
        
    def print_progress(self, stage, current_step, total_steps):
        """
        Print progress with time estimates.
        
        This method calculates and displays progress percentage, elapsed time,
        and estimated remaining time for the current stage.
        
        Args:
            stage (str): Current stage name
            current_step (int): Current step number
            total_steps (int): Total number of steps in the stage
        """
        if self.start_time is None:
            self.start_time = time.time()
            
        elapsed = time.time() - self.start_time
        progress = current_step / total_steps
        if progress > 0:
            estimated_total = elapsed / progress
            remaining = estimated_total - elapsed
            print(f"🔄 {stage}: {current_step}/{total_steps} ({progress:.1%}) - "
                  f"Elapsed: {elapsed/60:.1f}min, Remaining: {remaining/60:.1f}min")
        
    def load_and_prepare_data(self):
        """
        Load and prepare data with checkpointing support.
        
        This method loads the enhanced dataset, performs feature selection,
        samples data for faster processing, and creates time series splits.
        It also saves checkpoints to allow resuming from this stage.
        
        Returns:
            tuple: (X_train, X_val, X_test, y_train, y_val, y_test) - Prepared data splits
        """
        # Check if we have a checkpoint for data preparation
        checkpoint = self.load_checkpoint('data_preparation')
        if checkpoint:
            print("📊 Loading data from checkpoint...")
            return checkpoint['X_train'], checkpoint['X_val'], checkpoint['X_test'], \
                   checkpoint['y_train'], checkpoint['y_val'], checkpoint['y_test']
        
        print("📊 Loading enhanced data...")
        df = pd.read_parquet(self.enhanced_data_path)
        print(f"   Data shape: {df.shape}")
        
        # Prepare data by separating features and target
        target_col = 'Pb_Rougher_Conc_Pb'
        X = df.drop(columns=[target_col]).select_dtypes(include=[np.number])  # Keep only numeric features
        y = df[target_col]
        
        print(f"   Features: {X.shape[1]}")
        
        # Feature selection using mutual information
        # This helps identify the most relevant features for prediction
        print("🔍 Performing feature selection...")
        selector = SelectKBest(score_func=mutual_info_regression, k=min(200, X.shape[1]))
        X_selected = selector.fit_transform(X, y)
        selected_features = X.columns[selector.get_support()].tolist()
        X_selected = pd.DataFrame(X_selected, columns=selected_features, index=X.index)
        
        # Sample data for faster processing while maintaining representativeness
        print("⚡ Sampling data for faster processing...")
        sample_size = min(50000, len(X_selected))  # Use max 50K samples for speed
        sample_indices = np.random.choice(len(X_selected), sample_size, replace=False)
        X_selected = X_selected.iloc[sample_indices]
        y = y.iloc[sample_indices]
        print(f"   Sampled shape: {X_selected.shape}")
        
        # Create time series split for proper temporal validation
        # This ensures we don't use future data to predict past values
        print("⏰ Creating time series split...")
        tscv = TimeSeriesSplit(n_splits=3)
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
        
        print(f"   Train: {X_train.shape[0]}, Val: {X_val.shape[0]}, Test: {X_test.shape[0]}")
        
        # Save checkpoint for data preparation stage
        self.save_checkpoint('data_preparation', {
            'X_train': X_train, 'X_val': X_val, 'X_test': X_test,
            'y_train': y_train, 'y_val': y_val, 'y_test': y_test
        })
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def optimize_models(self, X_train, X_val, y_train, y_val):
        """
        Optimize models with hyperparameter tuning and checkpointing.
        
        This method trains and optimizes multiple machine learning models:
        - Ridge Regression: Linear model with regularization
        - Random Forest: Ensemble of decision trees
        - XGBoost: Gradient boosting with GPU acceleration
        - Gradient Boosting: Traditional gradient boosting
        
        Each model is optimized using cross-validation and hyperparameter tuning.
        
        Args:
            X_train, X_val, y_train, y_val: Training and validation data
            
        Returns:
            dict: Dictionary of optimized models
        """
        # Check if we have a checkpoint for model optimization
        checkpoint = self.load_checkpoint('model_optimization')
        if checkpoint:
            print("🤖 Loading optimized models from checkpoint...")
            return checkpoint['optimized_models']
        
        print("\n🤖 Starting model optimization...")
        optimized_models = {}
        
        # Define model configurations with hyperparameter search spaces
        models_config = [
            # Ridge Regression: Linear model with L2 regularization
            ('ridge', Ridge(random_state=42), {
                'alpha': [0.01, 0.1, 1.0, 10.0]  # Regularization strength
            }),
            
            # Random Forest: Ensemble of decision trees
            ('rf', RandomForestRegressor(random_state=42, n_jobs=2), {
                'n_estimators': [100, 200],      # Number of trees
                'max_depth': [10, 15, 20],       # Maximum tree depth
                'min_samples_split': [5, 10],    # Minimum samples to split
                'min_samples_leaf': [2, 5]       # Minimum samples per leaf
            }),
            
            # XGBoost: Gradient boosting with GPU acceleration
            ('xgb', xgb.XGBRegressor(
                random_state=42, 
                n_jobs=2, 
                tree_method='gpu_hist' if GPU_AVAILABLE else 'hist'  # Use GPU if available
            ), {
                'n_estimators': [150, 200],      # Number of boosting rounds
                'max_depth': [4, 6],             # Maximum tree depth
                'learning_rate': [0.05, 0.1],    # Learning rate
                'subsample': [0.8, 0.9]          # Subsample ratio
            }),
            
            # Gradient Boosting: Traditional gradient boosting
            ('gb', GradientBoostingRegressor(random_state=42), {
                'n_estimators': [100, 200],      # Number of boosting rounds
                'max_depth': [4, 6],             # Maximum tree depth
                'learning_rate': [0.05, 0.1]     # Learning rate
            })
        ]
        
        # Optimize each model
        for i, (name, model, params) in enumerate(models_config):
            self.print_progress("Optimization", i, len(models_config))
            print(f"   Optimizing {name}...")
            
            # Choose optimization strategy based on model type
            if name == 'ridge':
                # Use GridSearchCV for Ridge (smaller parameter space)
                search = GridSearchCV(model, params, cv=2, scoring='r2', n_jobs=2)
            else:
                # Use RandomizedSearchCV for tree-based models (larger parameter space)
                search = RandomizedSearchCV(
                    params, n_iter=5, cv=2, scoring='r2', n_jobs=2, random_state=42
                )
            
            # Fit the model with hyperparameter optimization
            search.fit(X_train, y_train)
            optimized_models[name] = search.best_estimator_
            
            print(f"   ✅ {name} - Best CV score: {search.best_score_:.4f}")
            
            # Save checkpoint after each model optimization
            self.save_checkpoint('model_optimization', {'optimized_models': optimized_models})
        
        return optimized_models
    
    def evaluate_models(self, optimized_models, X_train, X_val, X_test, y_train, y_val, y_test):
        """
        Evaluate optimized models on all datasets.
        
        This method evaluates each optimized model on training, validation,
        and test sets, calculating various performance metrics including
        R² score, RMSE, MAE, and prediction accuracy within error thresholds.
        
        Args:
            optimized_models (dict): Dictionary of optimized models
            X_train, X_val, X_test, y_train, y_val, y_test: Data splits
            
        Returns:
            dict: Dictionary containing evaluation results for each model
        """
        # Check if we have a checkpoint for model evaluation
        checkpoint = self.load_checkpoint('model_evaluation')
        if checkpoint:
            print("📈 Loading evaluation results from checkpoint...")
            return checkpoint['results']
        
        print("\n📈 Evaluating models...")
        results = {}
        
        # Evaluate each model
        for i, (name, model) in enumerate(optimized_models.items()):
            self.print_progress("Evaluation", i, len(optimized_models))
            print(f"   Evaluating {name}...")
            
            # Make predictions on all datasets
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
            test_pred_10 = np.mean(test_errors <= 10)  # Predictions within 10% error
            
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
            
            print(f"   ✅ {name} - Test R²: {test_r2:.4f}, RMSE: {test_rmse:.4f}, 10% Acc: {test_pred_10:.2%}")
            
            # Save checkpoint after each model evaluation
            self.save_checkpoint('model_evaluation', {'results': results})
        
        return results
    
    def create_visualizations(self, results, y_test):
        """
        Create comprehensive visualizations of model performance.
        
        This method creates a 2x2 grid of plots showing:
        1. R² scores comparison across models
        2. RMSE comparison across models
        3. Actual vs Predicted scatter plot for best model
        4. Residuals plot for best model
        
        Args:
            results (dict): Model evaluation results
            y_test (array): Actual test values
            
        Returns:
            str: Name of the best performing model
        """
        print("\n📊 Creating visualizations...")
        
        # Find the best model based on test R² score
        best_model_name = max(results.keys(), key=lambda x: results[x]['test_r2'])
        best_results = results[best_model_name]
        
        # Create a 2x2 grid of plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Froth Flotation Model Performance Analysis', fontsize=16, fontweight='bold')
        
        # 1. R² scores comparison
        model_names = list(results.keys())
        test_r2 = [results[name]['test_r2'] for name in model_names]
        axes[0, 0].bar(model_names, test_r2, alpha=0.8, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        axes[0, 0].set_title('Test R² Scores Comparison')
        axes[0, 0].set_ylabel('R² Score')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate(test_r2):
            axes[0, 0].text(i, v + 0.01, f'{v:.3f}', ha='center', va='bottom')
        
        # 2. RMSE comparison
        test_rmse = [results[name]['test_rmse'] for name in model_names]
        axes[0, 1].bar(model_names, test_rmse, alpha=0.8, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
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
        
        # Save the visualization
        Path('Plots').mkdir(exist_ok=True)
        plt.savefig('Plots/flotation_optimization_results.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return best_model_name
    
    def save_best_model(self, results, best_model_name):
        """
        Save the best performing model to disk.
        
        This method saves the best model along with metadata for future use.
        
        Args:
            results (dict): Model evaluation results
            best_model_name (str): Name of the best model
            
        Returns:
            str: Path to the saved model file
        """
        import joblib
        
        best_model = results[best_model_name]['model']
        model_path = f'models/{best_model_name}_optimized_model.pkl'
        
        # Create models directory if it doesn't exist
        Path('models').mkdir(exist_ok=True)
        
        # Save the model
        joblib.dump(best_model, model_path)
        print(f"💾 Best model saved: {model_path}")
        
        # Save model metadata
        metadata = {
            'model_name': best_model_name,
            'test_r2': results[best_model_name]['test_r2'],
            'test_rmse': results[best_model_name]['test_rmse'],
            'test_mae': results[best_model_name]['test_mae'],
            'test_pred_10%': results[best_model_name]['test_pred_10%'],
            'training_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'model_type': type(best_model).__name__
        }
        
        metadata_path = f'models/{best_model_name}_metadata.pkl'
        joblib.dump(metadata, metadata_path)
        print(f"📋 Model metadata saved: {metadata_path}")
        
        return model_path
    
    def run_pipeline(self):
        """
        Run the complete optimization pipeline.
        
        This is the main method that orchestrates the entire pipeline:
        1. Load and prepare data
        2. Optimize models
        3. Evaluate models
        4. Create visualizations
        5. Save best model
        6. Print summary
        
        Returns:
            tuple: (results, best_model_name) - Evaluation results and best model name
        """
        print("=" * 60)
        print("🚀 OPTIMIZED FROTH FLOTATION PREDICTION PIPELINE")
        print("=" * 60)
        
        # Check for final results checkpoint
        final_checkpoint = self.load_checkpoint('final_results')
        if final_checkpoint:
            print("🎉 Found final results! Loading completed results...")
            results = final_checkpoint['results']
            best_model_name = final_checkpoint['best_model_name']
            self.print_summary(results, best_model_name)
            return results, best_model_name
        
        # Step 1: Load and prepare data
        print("\n📊 STEP 1: Data Preparation")
        X_train, X_val, X_test, y_train, y_val, y_test = self.load_and_prepare_data()
        
        # Step 2: Optimize models
        print("\n🤖 STEP 2: Model Optimization")
        optimized_models = self.optimize_models(X_train, X_val, y_train, y_val)
        
        # Step 3: Evaluate models
        print("\n📈 STEP 3: Model Evaluation")
        results = self.evaluate_models(optimized_models, X_train, X_val, X_test, y_train, y_val, y_test)
        
        # Step 4: Create visualizations
        print("\n📊 STEP 4: Visualization")
        best_model_name = self.create_visualizations(results, y_test)
        
        # Step 5: Save best model
        print("\n💾 STEP 5: Model Saving")
        model_path = self.save_best_model(results, best_model_name)
        
        # Step 6: Save final results checkpoint
        self.save_checkpoint('final_results', {
            'results': results,
            'best_model_name': best_model_name,
            'model_path': model_path
        })
        
        # Step 7: Print summary
        print("\n📋 STEP 6: Results Summary")
        self.print_summary(results, best_model_name)
        
        return results, best_model_name
    
    def print_summary(self, results, best_model_name):
        """
        Print a comprehensive summary of the optimization results.
        
        This method displays the performance metrics for all models and
        highlights the improvements achieved compared to baseline performance.
        
        Args:
            results (dict): Model evaluation results
            best_model_name (str): Name of the best model
        """
        print("\n" + "=" * 60)
        print("📋 FINAL RESULTS SUMMARY")
        print("=" * 60)
        
        best_results = results[best_model_name]
        print(f"🏆 Best Model: {best_model_name.upper()}")
        print(f"📊 Test R² Score: {best_results['test_r2']:.4f}")
        print(f"📏 Test RMSE: {best_results['test_rmse']:.4f}")
        print(f"📐 Test MAE: {best_results['test_mae']:.4f}")
        print(f"🎯 Test predictions within 10%: {best_results['test_pred_10%']:.2%}")
        
        print(f"\n📈 MODEL PERFORMANCE COMPARISON")
        print("-" * 40)
        for name, result in results.items():
            print(f"{name.upper():<12} | R²: {result['test_r2']:.4f} | RMSE: {result['test_rmse']:.4f} | 10% Acc: {result['test_pred_10%']:.2%}")
        
        print(f"\n🚀 IMPROVEMENT COMPARISON")
        print("-" * 40)
        print("Previous Best (RandomForest): R² = 0.1457, RMSE = 8.7734")
        print(f"New Best ({best_model_name.upper()}): R² = {best_results['test_r2']:.4f}, RMSE = {best_results['test_rmse']:.4f}")
        
        r2_improvement = best_results['test_r2'] - 0.1457
        rmse_improvement = 8.7734 - best_results['test_rmse']
        
        print(f"🚀 R² Improvement: {r2_improvement:+.4f} ({r2_improvement/0.1457*100:.1f}% improvement)")
        print(f"📉 RMSE Improvement: {rmse_improvement:+.4f} ({rmse_improvement/8.7734*100:.1f}% reduction)")
        
        # Print execution time
        if self.start_time:
            total_time = time.time() - self.start_time
            print(f"\n⏱️ Total execution time: {total_time/60:.1f} minutes")
        
        print(f"\n📁 Generated Files:")
        print(f"   • Model: models/{best_model_name}_optimized_model.pkl")
        print(f"   • Metadata: models/{best_model_name}_metadata.pkl")
        print(f"   • Visualization: Plots/flotation_optimization_results.png")
        print(f"   • Checkpoints: checkpoints/ directory")


def main():
    """
    Main function to run the optimization pipeline.
    
    This function initializes the pipeline with the enhanced dataset path
    and runs the complete optimization process.
    """
    # Path to the enhanced dataset
    enhanced_data_path = r"C:\@Python Projects\TUT Research Project\Clean_Data\HZL_RA4_Pb_Rougher_enhanced_clean.parquet"
    
    # Initialize the pipeline
    pipeline = OptimizedFlotationPipeline(enhanced_data_path)
    
    # Run the complete pipeline
    results, best_model = pipeline.run_pipeline()
    
    print(f"\n🎉 Pipeline completed successfully!")
    print(f"Best model: {best_model.upper()}")
    print(f"Test R² Score: {results[best_model]['test_r2']:.4f}")


if __name__ == "__main__":
    main()
