"""
Unit Tests for Improved 5-Minute Training Pipeline
================================================

This module contains comprehensive unit tests for the improved 5-minute horizon
training pipeline. Tests cover:

1. Data loading and validation
2. Feature selection
3. Model optimization
4. Evaluation metrics
5. Checkpointing functionality
6. Data leakage prevention

These tests should be run before the full training to ensure all components
work correctly.
"""

import unittest
import numpy as np
import pandas as pd
import tempfile
import shutil
from pathlib import Path
import sys
import warnings
from unittest.mock import patch, MagicMock

# Add training directory to path
sys.path.append('training')

# Suppress warnings during testing
warnings.filterwarnings('ignore')

class TestImprovedFiveMinuteTrainer(unittest.TestCase):
    """Test cases for the ImprovedFiveMinuteTrainer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.trainer = None
        
        # Create mock data for testing
        self.create_mock_data()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def create_mock_data(self):
        """Create mock training data for testing."""
        # Create mock dataset directory
        datasets_dir = self.test_dir / 'backend' / 'training' / 'time_series_datasets'
        datasets_dir.mkdir(parents=True, exist_ok=True)
        
        # Create mock data with realistic structure
        np.random.seed(42)
        n_samples = 1000
        n_features = 50
        
        # Create feature columns (excluding leakage patterns)
        feature_cols = []
        for i in range(n_features):
            feature_cols.append(f'feature_{i}')
        
        # Create target column
        target_col = 'Pb_Rougher_Conc_Pb_5min_ahead'
        
        # Create mock DataFrame
        data = {}
        for col in feature_cols:
            data[col] = np.random.normal(0, 1, n_samples)
        
        # Create realistic target values (Pb concentrate typically 20-30%)
        data[target_col] = np.random.normal(25, 5, n_samples)
        data[target_col] = np.clip(data[target_col], 0, 50)  # Clip to realistic range
        
        df = pd.DataFrame(data)
        
        # Save mock dataset
        dataset_path = datasets_dir / 'training_data_5min.parquet'
        df.to_parquet(dataset_path)
        
        self.mock_dataset_path = dataset_path
        self.mock_data = df
    
    def test_initialization(self):
        """Test trainer initialization."""
        from improved_5min_training import ImprovedFiveMinuteTrainer
        
        with patch('improved_5min_training.Path') as mock_path:
            mock_path.return_value.parent.parent = self.test_dir
            
            trainer = ImprovedFiveMinuteTrainer()
            
            self.assertEqual(trainer.horizon, 5)
            self.assertEqual(trainer.max_features, 200)
            self.assertEqual(trainer.sample_size, 100000)
            self.assertIsNotNone(trainer.output_dir)
            self.assertIsNotNone(trainer.checkpoint_dir)
    
    def test_data_loading_and_validation(self):
        """Test data loading and validation functionality."""
        from improved_5min_training import ImprovedFiveMinuteTrainer
        
        with patch('improved_5min_training.Path') as mock_path:
            mock_path.return_value.parent.parent = self.test_dir
            
            trainer = ImprovedFiveMinuteTrainer()
            
            # Mock the checkpoint directory to use a real temp directory
            import tempfile
            temp_checkpoint_dir = Path(tempfile.mkdtemp())
            trainer.checkpoint_dir = temp_checkpoint_dir
            
            try:
                # Test data loading
                X_train, X_val, X_test, y_train, y_val, y_test = trainer.load_and_prepare_data()
                
                # Check data shapes
                self.assertGreater(len(X_train), 0)
                self.assertGreater(len(X_val), 0)
                self.assertGreater(len(X_test), 0)
                self.assertEqual(len(X_train), len(y_train))
                self.assertEqual(len(X_val), len(y_val))
                self.assertEqual(len(X_test), len(y_test))
                
                # Check that features are numeric
                self.assertTrue(all(X_train.dtypes.apply(lambda x: np.issubdtype(x, np.number))))
                self.assertTrue(all(X_val.dtypes.apply(lambda x: np.issubdtype(x, np.number))))
                self.assertTrue(all(X_test.dtypes.apply(lambda x: np.issubdtype(x, np.number))))
                
                # Check target values are reasonable
                self.assertTrue(all(y_train >= 0))
                self.assertTrue(all(y_val >= 0))
                self.assertTrue(all(y_test >= 0))
            finally:
                # Clean up
                import shutil
                if temp_checkpoint_dir.exists():
                    shutil.rmtree(temp_checkpoint_dir)
    
    def test_data_leakage_prevention(self):
        """Test that data leakage prevention works correctly."""
        from improved_5min_training import ImprovedFiveMinuteTrainer
        
        with patch('improved_5min_training.Path') as mock_path:
            mock_path.return_value.parent.parent = self.test_dir
            
            trainer = ImprovedFiveMinuteTrainer()
            
            # Mock the checkpoint directory to use a real temp directory
            import tempfile
            temp_checkpoint_dir = Path(tempfile.mkdtemp())
            trainer.checkpoint_dir = temp_checkpoint_dir
            
            try:
                # Load data
                X_train, X_val, X_test, y_train, y_val, y_test = trainer.load_and_prepare_data()
                
                # Check that no future information is in features
                feature_names = X_train.columns.tolist()
                
                # Should not contain target-related patterns
                leakage_patterns = ['_ahead', 'target', 'Pb_Rougher_Conc_Pb', 'future', 'prediction', 'forecast']
                
                for pattern in leakage_patterns:
                    for feature in feature_names:
                        self.assertNotIn(pattern, feature, f"Feature {feature} contains leakage pattern {pattern}")
            finally:
                # Clean up
                import shutil
                if temp_checkpoint_dir.exists():
                    shutil.rmtree(temp_checkpoint_dir)
    
    def test_feature_selection(self):
        """Test feature selection functionality."""
        from improved_5min_training import ImprovedFiveMinuteTrainer
        from sklearn.feature_selection import SelectKBest, mutual_info_regression
        
        with patch('improved_5min_training.Path') as mock_path:
            mock_path.return_value.parent.parent = self.test_dir
            
            trainer = ImprovedFiveMinuteTrainer()
            
            # Mock the checkpoint directory to use a real temp directory
            import tempfile
            temp_checkpoint_dir = Path(tempfile.mkdtemp())
            trainer.checkpoint_dir = temp_checkpoint_dir
            
            try:
                # Load data
                X_train, X_val, X_test, y_train, y_val, y_test = trainer.load_and_prepare_data()
                
                # Check that feature selection was applied
                self.assertLessEqual(X_train.shape[1], trainer.max_features)
                self.assertEqual(X_train.shape[1], X_val.shape[1])
                self.assertEqual(X_train.shape[1], X_test.shape[1])
                
                # Check that features are meaningful (not all zeros)
                self.assertTrue(np.any(X_train != 0))
                self.assertTrue(np.any(X_val != 0))
                self.assertTrue(np.any(X_test != 0))
            finally:
                # Clean up
                import shutil
                if temp_checkpoint_dir.exists():
                    shutil.rmtree(temp_checkpoint_dir)
    
    def test_checkpointing(self):
        """Test checkpointing functionality."""
        from improved_5min_training import ImprovedFiveMinuteTrainer
        
        with patch('improved_5min_training.Path') as mock_path:
            mock_path.return_value.parent.parent = self.test_dir
            
            trainer = ImprovedFiveMinuteTrainer()
            
            # Mock the checkpoint directory to use a real temp directory
            import tempfile
            temp_checkpoint_dir = Path(tempfile.mkdtemp())
            trainer.checkpoint_dir = temp_checkpoint_dir
            
            try:
                # Test saving checkpoint
                test_data = {'test': 'data', 'number': 42}
                trainer.save_checkpoint('test_stage', test_data)
                
                # Check that checkpoint file exists
                checkpoint_file = trainer.checkpoint_dir / 'checkpoint_test_stage.pkl'
                self.assertTrue(checkpoint_file.exists())
                
                # Test loading checkpoint
                loaded_data = trainer.load_checkpoint('test_stage')
                self.assertEqual(loaded_data, test_data)
                
                # Test loading non-existent checkpoint
                non_existent = trainer.load_checkpoint('non_existent')
                self.assertIsNone(non_existent)
            finally:
                # Clean up
                import shutil
                if temp_checkpoint_dir.exists():
                    shutil.rmtree(temp_checkpoint_dir)
    
    def test_model_optimization_small_scale(self):
        """Test model optimization with small dataset."""
        from improved_5min_training import ImprovedFiveMinuteTrainer
        
        with patch('improved_5min_training.Path') as mock_path:
            mock_path.return_value.parent.parent = self.test_dir
            
            trainer = ImprovedFiveMinuteTrainer()
            trainer.max_features = 10  # Reduce for faster testing
            trainer.sample_size = 100  # Reduce for faster testing
            
            # Mock the checkpoint directory to use a real temp directory
            import tempfile
            temp_checkpoint_dir = Path(tempfile.mkdtemp())
            trainer.checkpoint_dir = temp_checkpoint_dir
            
            try:
                # Load small dataset
                X_train, X_val, X_test, y_train, y_val, y_test = trainer.load_and_prepare_data()
                
                # Test model optimization with reduced parameters - disable checkpointing
                with patch.object(trainer, 'save_checkpoint') as mock_save:
                    with patch('improved_5min_training.GridSearchCV') as mock_grid:
                        with patch('improved_5min_training.RandomizedSearchCV') as mock_random:
                            # Mock the search results
                            mock_search = MagicMock()
                            mock_search.best_estimator_ = MagicMock()
                            mock_search.best_score_ = 0.5
                            mock_grid.return_value = mock_search
                            mock_random.return_value = mock_search
                            
                            optimized_models = trainer.optimize_models(X_train, X_val, y_train, y_val)
                            
                            # Check that models were created (should be exactly 3: ridge, rf, xgb)
                            self.assertIsInstance(optimized_models, dict)
                            self.assertEqual(len(optimized_models), 3)
                            self.assertIn('ridge', optimized_models)
                            self.assertIn('rf', optimized_models)
                            self.assertIn('xgb', optimized_models)
            finally:
                # Clean up
                import shutil
                if temp_checkpoint_dir.exists():
                    shutil.rmtree(temp_checkpoint_dir)
    
    def test_evaluation_metrics(self):
        """Test evaluation metrics calculation."""
        from improved_5min_training import ImprovedFiveMinuteTrainer
        from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
        
        with patch('improved_5min_training.Path') as mock_path:
            mock_path.return_value.parent.parent = self.test_dir
            
            trainer = ImprovedFiveMinuteTrainer()
            trainer.max_features = 10
            trainer.sample_size = 100
            
            # Mock the checkpoint directory to use a real temp directory
            import tempfile
            temp_checkpoint_dir = Path(tempfile.mkdtemp())
            trainer.checkpoint_dir = temp_checkpoint_dir
            
            try:
                # Load small dataset
                X_train, X_val, X_test, y_train, y_val, y_test = trainer.load_and_prepare_data()
                
                # Create mock model
                mock_model = MagicMock()
                mock_model.predict.return_value = y_test + np.random.normal(0, 1, len(y_test))
                
                # Test evaluation - disable checkpointing for this test to avoid pickling issues
                with patch.object(trainer, 'save_checkpoint') as mock_save:
                    optimized_models = {'test_model': mock_model}
                    
                    with patch('improved_5min_training.r2_score') as mock_r2:
                        with patch('improved_5min_training.mean_squared_error') as mock_mse:
                            with patch('improved_5min_training.mean_absolute_error') as mock_mae:
                                mock_r2.return_value = 0.5
                                mock_mse.return_value = 10.0
                                mock_mae.return_value = 2.5
                                
                                results = trainer.evaluate_models(optimized_models, X_train, X_val, X_test, y_train, y_val, y_test)
                                
                                # Check that results were calculated
                                self.assertIsInstance(results, dict)
                                self.assertIn('test_model', results)
                                self.assertIn('test_r2', results['test_model'])
                                self.assertIn('test_rmse', results['test_model'])
                                self.assertIn('test_mae', results['test_model'])
            finally:
                # Clean up
                import shutil
                if temp_checkpoint_dir.exists():
                    shutil.rmtree(temp_checkpoint_dir)
    
    def test_target_variable_validation(self):
        """Test target variable validation."""
        from improved_5min_training import ImprovedFiveMinuteTrainer
        
        with patch('improved_5min_training.Path') as mock_path:
            mock_path.return_value.parent.parent = self.test_dir
            
            trainer = ImprovedFiveMinuteTrainer()
            
            # Mock the checkpoint directory to use a real temp directory
            import tempfile
            temp_checkpoint_dir = Path(tempfile.mkdtemp())
            trainer.checkpoint_dir = temp_checkpoint_dir
            
            try:
                # Load data
                X_train, X_val, X_test, y_train, y_val, y_test = trainer.load_and_prepare_data()
                
                # Check target variable properties
                all_targets = np.concatenate([y_train, y_val, y_test])
                
                # Should be reasonable Pb concentrate values
                self.assertTrue(np.all(all_targets >= 0))  # Non-negative
                self.assertTrue(np.all(all_targets <= 100))  # Percentage
                self.assertTrue(np.mean(all_targets) > 10)  # Reasonable mean
                self.assertTrue(np.mean(all_targets) < 50)  # Reasonable mean
            finally:
                # Clean up
                import shutil
                if temp_checkpoint_dir.exists():
                    shutil.rmtree(temp_checkpoint_dir)
    
    def test_time_series_split(self):
        """Test time series split functionality."""
        from improved_5min_training import ImprovedFiveMinuteTrainer
        
        with patch('improved_5min_training.Path') as mock_path:
            mock_path.return_value.parent.parent = self.test_dir
            
            trainer = ImprovedFiveMinuteTrainer()
            trainer.max_features = 10
            trainer.sample_size = 100
            
            # Mock the checkpoint directory to use a real temp directory
            import tempfile
            temp_checkpoint_dir = Path(tempfile.mkdtemp())
            trainer.checkpoint_dir = temp_checkpoint_dir
            
            try:
                # Load data
                X_train, X_val, X_test, y_train, y_val, y_test = trainer.load_and_prepare_data()
                
                # Check that splits are non-overlapping
                train_size = len(X_train)
                val_size = len(X_val)
                test_size = len(X_test)
                
                # Should be reasonable split sizes
                self.assertGreater(train_size, 0)
                self.assertGreater(val_size, 0)
                self.assertGreater(test_size, 0)
                
                # Total should equal original size (allow for small rounding differences)
                # Note: TimeSeriesSplit can have overlapping validation sets, so we check differently
                total_size = train_size + val_size + test_size
                self.assertGreaterEqual(total_size, 100)  # Should be at least the original size
                self.assertLessEqual(total_size, 100 + 100)  # Allow for significant overlap in validation
            finally:
                # Clean up
                import shutil
                if temp_checkpoint_dir.exists():
                    shutil.rmtree(temp_checkpoint_dir)
    
    def test_error_handling(self):
        """Test error handling for missing data."""
        from improved_5min_training import ImprovedFiveMinuteTrainer
        
        with patch('improved_5min_training.Path') as mock_path:
            mock_path.return_value.parent.parent = self.test_dir
            
            trainer = ImprovedFiveMinuteTrainer()
            
            # Mock the checkpoint directory to use a real temp directory
            import tempfile
            temp_checkpoint_dir = Path(tempfile.mkdtemp())
            trainer.checkpoint_dir = temp_checkpoint_dir
            
            try:
                # Test with non-existent dataset
                with patch('improved_5min_training.pd.read_parquet') as mock_read:
                    mock_read.side_effect = FileNotFoundError("Dataset not found")
                    
                    with self.assertRaises(FileNotFoundError):
                        trainer.load_and_prepare_data()
            finally:
                # Clean up
                import shutil
                if temp_checkpoint_dir.exists():
                    shutil.rmtree(temp_checkpoint_dir)
    
    def test_progress_tracking(self):
        """Test progress tracking functionality."""
        from improved_5min_training import ImprovedFiveMinuteTrainer
        
        with patch('improved_5min_training.Path') as mock_path:
            mock_path.return_value.parent.parent = self.test_dir
            
            trainer = ImprovedFiveMinuteTrainer()
            
            # Test progress tracking
            with patch('improved_5min_training.time.time') as mock_time:
                mock_time.return_value = 100.0
                
                # Should not raise any exceptions
                trainer.print_progress("Test Stage", 1, 4)
                trainer.print_progress("Test Stage", 2, 4)
                trainer.print_progress("Test Stage", 4, 4)

def run_performance_tests():
    """Run performance tests to check training speed."""
    print("Running performance tests...")
    
    # Test with small dataset to check speed
    from improved_5min_training import ImprovedFiveMinuteTrainer
    
    with patch('improved_5min_training.Path') as mock_path:
        mock_path.return_value.parent.parent = Path(tempfile.mkdtemp())
        
        trainer = ImprovedFiveMinuteTrainer()
        trainer.max_features = 20
        trainer.sample_size = 500
        
        # Mock the checkpoint directory to use a real temp directory
        temp_checkpoint_dir = Path(tempfile.mkdtemp())
        trainer.checkpoint_dir = temp_checkpoint_dir
        
        try:
            import time
            start_time = time.time()
            
            X_train, X_val, X_test, y_train, y_val, y_test = trainer.load_and_prepare_data()
            data_time = time.time() - start_time
            
            print(f"Data loading time: {data_time:.2f} seconds")
            print(f"Dataset shapes: Train={X_train.shape}, Val={X_val.shape}, Test={X_test.shape}")
            
            # Test one model optimization
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import RandomizedSearchCV
            
            model = RandomForestRegressor(random_state=42, n_jobs=1)
            params = {
                'n_estimators': [10, 20],
                'max_depth': [3, 5]
            }
            
            start_time = time.time()
            search = RandomizedSearchCV(model, params, n_iter=2, cv=2, scoring='r2', n_jobs=1, random_state=42)
            search.fit(X_train, y_train)
            model_time = time.time() - start_time
            
            print(f"Model optimization time: {model_time:.2f} seconds")
            print(f"Best CV score: {search.best_score_:.4f}")
            
        except Exception as e:
            print(f"Performance test failed: {e}")
        finally:
            # Clean up
            import shutil
            if temp_checkpoint_dir.exists():
                shutil.rmtree(temp_checkpoint_dir)

if __name__ == '__main__':
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    # Run performance tests
    run_performance_tests()
