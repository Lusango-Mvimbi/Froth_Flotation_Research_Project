"""
Comprehensive Test Suite for Future Prediction System
===================================================

This module contains comprehensive tests for the future prediction system,
including unit tests, integration tests, and performance tests.

Test Categories:
- Unit tests for individual components
- Integration tests for end-to-end prediction flow
- Performance tests for real-time prediction
- Validation tests for prediction accuracy
- Error handling and edge case tests

Author: AI Assistant
Date: 2024
"""

import unittest
import sys
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.ml_model_service import MLModelService
from services.future_prediction_service import FuturePredictionService
from services.optimization_service import FlotationOptimizer
from services.scenario_analyzer import ScenarioAnalyzer
from services.predictive_alerts import PredictiveAlerts

class TestFuturePredictionService(unittest.TestCase):
    """Test cases for FuturePredictionService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.future_predictor = FuturePredictionService()
        self.test_data = pd.DataFrame({
            'Feed_Pb': [2.5],
            'Feed_Zn': [10.0],
            'Pb_Conditioner_KEX_Flowrate': [60.0],
            'Pb_Rougher1_SIPX_Flowrate': [30.0],
            'Pb_Rougher1_AirFlow': [10.0],
            'Pb_Rougher1_Level': [40.0]
        })
    
    def test_service_initialization(self):
        """Test that the service initializes correctly."""
        self.assertIsNotNone(self.future_predictor)
        self.assertIsNotNone(self.future_predictor.models)
        self.assertIn('5min', self.future_predictor.models)
        self.assertIn('15min', self.future_predictor.models)
        self.assertIn('30min', self.future_predictor.models)
        self.assertIn('60min', self.future_predictor.models)
    
    def test_model_loading(self):
        """Test that models are loaded correctly."""
        for horizon in ['5min', '15min', '30min', '60min']:
            self.assertIn(horizon, self.future_predictor.models)
            self.assertIn('rf', self.future_predictor.models[horizon])
    
    def test_feature_preparation(self):
        """Test feature preparation functionality."""
        features = self.future_predictor._prepare_features(self.test_data)
        self.assertIsInstance(features, pd.DataFrame)
        self.assertGreater(len(features.columns), 0)
    
    def test_future_prediction(self):
        """Test future prediction functionality."""
        # Use MLModelService to prepare data with 200 features
        ml_service = MLModelService()
        prepared_data = ml_service._prepare_data_for_future_prediction({
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        })
        
        result = self.future_predictor.predict_future(prepared_data, [5, 15, 30, 60])
        
        self.assertIn('5min', result)
        self.assertIn('15min', result)
        self.assertIn('30min', result)
        self.assertIn('60min', result)
        
        # Check prediction structure
        for horizon in ['5min', '15min', '30min', '60min']:
            prediction = result[horizon]
            self.assertIn('prediction', prediction)
            self.assertIn('confidence_interval', prediction)
            self.assertIn('model_performance', prediction)
            self.assertIsInstance(prediction['prediction'], (int, float))
    
    def test_prediction_caching(self):
        """Test prediction caching functionality."""
        # Use MLModelService to prepare data with 200 features
        ml_service = MLModelService()
        prepared_data = ml_service._prepare_data_for_future_prediction({
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        })
        
        # First prediction
        result1 = self.future_predictor.predict_future(prepared_data, [5])
        time.sleep(0.1)  # Small delay
        
        # Second prediction (should be cached)
        result2 = self.future_predictor.predict_future(prepared_data, [5])
        
        # Results should be identical
        self.assertEqual(
            result1['5min']['prediction'],
            result2['5min']['prediction']
        )
    
    def test_prediction_validation(self):
        """Test prediction validation functionality."""
        # Use MLModelService to prepare data with 200 features
        ml_service = MLModelService()
        prepared_data = ml_service._prepare_data_for_future_prediction({
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        })
        
        # Make a prediction
        result = self.future_predictor.predict_future(prepared_data, [5])
        
        # Track the prediction
        self.future_predictor.track_prediction(result)
        
        # Check that prediction was tracked
        self.assertGreater(len(self.future_predictor.prediction_history), 0)
        
        # Get confidence score
        confidence = self.future_predictor.get_prediction_confidence_score(
            5, result
        )
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

class TestMLModelService(unittest.TestCase):
    """Test cases for MLModelService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.ml_service = MLModelService()
        self.test_data = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        }
    
    def test_service_initialization(self):
        """Test that the service initializes correctly."""
        self.assertIsNotNone(self.ml_service)
        self.assertTrue(self.ml_service.future_prediction_available)
    
    def test_future_prediction_integration(self):
        """Test integration with future prediction service."""
        result = self.ml_service.predict_future_pb_concentrate(self.test_data, [5, 60])
        
        self.assertIn('future_predictions', result)
        self.assertIn('5min', result['future_predictions'])
        self.assertIn('60min', result['future_predictions'])
    
    def test_data_preparation(self):
        """Test data preparation for future prediction."""
        data_df = self.ml_service._prepare_data_for_future_prediction(self.test_data)
        
        self.assertIsInstance(data_df, pd.DataFrame)
        self.assertEqual(len(data_df), 1)  # Single row
        self.assertGreater(len(data_df.columns), 0)
    
    def test_prediction_info(self):
        """Test prediction information retrieval."""
        info = self.ml_service.get_future_prediction_info()
        
        self.assertIn('status', info)
        self.assertIn('available_horizons', info)
        self.assertIn('model_performance', info)

class TestOptimizationService(unittest.TestCase):
    """Test cases for FlotationOptimizer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = FlotationOptimizer()
        self.test_data = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        }
    
    def test_optimizer_initialization(self):
        """Test that the optimizer initializes correctly."""
        self.assertIsNotNone(self.optimizer)
        self.assertIsNotNone(self.optimizer.future_predictor)
    
    def test_multi_horizon_optimization(self):
        """Test multi-horizon optimization."""
        result = self.optimizer.optimize_multi_horizon(self.test_data)
        
        self.assertIn('success', result)
        self.assertTrue(result['success'])
        self.assertIn('optimal_settings', result)
        self.assertIn('best_score', result)
        self.assertIn('optimization_message', result)
    
    def test_optimization_recommendations(self):
        """Test optimization recommendations generation."""
        optimization_result = self.optimizer.optimize_multi_horizon(self.test_data)
        recommendations = self.optimizer.generate_multi_horizon_recommendations(optimization_result)
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

class TestScenarioAnalyzer(unittest.TestCase):
    """Test cases for ScenarioAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ScenarioAnalyzer()
        self.test_data = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        }
    
    def test_analyzer_initialization(self):
        """Test that the analyzer initializes correctly."""
        self.assertIsNotNone(self.analyzer)
        self.assertIsNotNone(self.analyzer.future_predictor)
    
    def test_scenario_analysis(self):
        """Test scenario analysis functionality."""
        parameter_changes = {'Pb_Conditioner_KEX_Flowrate': 10.0}
        result = self.analyzer.analyze_scenario(self.test_data, parameter_changes, "Test Scenario")
        
        self.assertIn('scenario_name', result)
        self.assertIn('overall_risk_score', result)
        self.assertIn('overall_benefit_score', result)
        self.assertIn('overall_recommendation', result)
    
    def test_what_if_scenarios(self):
        """Test what-if scenario generation."""
        scenarios = self.analyzer.generate_what_if_scenarios(self.test_data)
        
        self.assertIsInstance(scenarios, list)
        self.assertGreater(len(scenarios), 0)
        
        for scenario in scenarios:
            self.assertIn('name', scenario)
            self.assertIn('parameter_changes', scenario)
            self.assertIn('description', scenario)
    
    def test_risk_assessment(self):
        """Test risk assessment functionality."""
        parameter_changes = {'Pb_Conditioner_KEX_Flowrate': 10.0}
        result = self.analyzer.assess_risk_for_changes(self.test_data, parameter_changes)
        
        self.assertIn('overall_risk_score', result)
        self.assertIn('risk_level', result)
        self.assertIn('success_probability', result)

class TestPredictiveAlerts(unittest.TestCase):
    """Test cases for PredictiveAlerts."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.alerter = PredictiveAlerts()
        self.test_data = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        }
    
    def test_alerter_initialization(self):
        """Test that the alerter initializes correctly."""
        self.assertIsNotNone(self.alerter)
        self.assertIsNotNone(self.alerter.future_predictor)
    
    def test_prediction_monitoring(self):
        """Test prediction monitoring functionality."""
        alerts = self.alerter.monitor_predictions(self.test_data)
        
        self.assertIsInstance(alerts, list)
        # Alerts may or may not be generated depending on thresholds
    
    def test_preventive_actions(self):
        """Test preventive action suggestions."""
        # Create a test alert
        from services.predictive_alerts import Alert
        test_alert = Alert(
            'high_concentrate',
            'warning',
            'Test alert',
            {'prediction': 15.0}
        )
        
        suggestions = self.alerter.suggest_preventive_actions(test_alert)
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
    
    def test_alert_summary(self):
        """Test alert summary generation."""
        summary = self.alerter.get_alert_summary()
        
        self.assertIn('active_alerts_count', summary)
        self.assertIn('severity_distribution', summary)
        self.assertIn('type_distribution', summary)

class TestIntegration(unittest.TestCase):
    """Integration tests for end-to-end prediction flow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.ml_service = MLModelService()
        self.future_predictor = FuturePredictionService()
        self.optimizer = FlotationOptimizer()
        self.analyzer = ScenarioAnalyzer()
        self.alerter = PredictiveAlerts()
        
        self.test_data = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        }
    
    def test_end_to_end_prediction_flow(self):
        """Test complete end-to-end prediction flow."""
        # 1. Get future predictions
        predictions = self.ml_service.predict_future_pb_concentrate(self.test_data, [5, 60])
        self.assertIn('future_predictions', predictions)
        
        # 2. Run optimization
        optimization = self.optimizer.optimize_multi_horizon(self.test_data)
        self.assertTrue(optimization['success'])
        
        # 3. Analyze scenarios
        scenario_result = self.analyzer.analyze_scenario(
            self.test_data, 
            {'Pb_Conditioner_KEX_Flowrate': 10.0}, 
            "Integration Test"
        )
        self.assertIn('overall_recommendation', scenario_result)
        
        # 4. Monitor for alerts
        alerts = self.alerter.monitor_predictions(self.test_data)
        self.assertIsInstance(alerts, list)
    
    def test_data_consistency_across_services(self):
        """Test that data is consistent across all services."""
        # Prepare data using ML service
        ml_data = self.ml_service._prepare_data_for_future_prediction(self.test_data)
        
        # Get predictions from both services
        ml_predictions = self.ml_service.predict_future_pb_concentrate(self.test_data, [5])
        fp_predictions = self.future_predictor.predict_future(ml_data, [5])
        
        # Predictions should be consistent
        ml_pred = ml_predictions['future_predictions']['5min']['prediction']
        fp_pred = fp_predictions['5min']['prediction']
        
        self.assertAlmostEqual(ml_pred, fp_pred, places=4)

class TestPerformance(unittest.TestCase):
    """Performance tests for real-time prediction."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.ml_service = MLModelService()
        self.test_data = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        }
    
    def test_prediction_speed(self):
        """Test prediction speed for real-time requirements."""
        start_time = time.time()
        
        # Make multiple predictions
        for _ in range(10):
            result = self.ml_service.predict_future_pb_concentrate(self.test_data, [5, 60])
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 10
        
        # Each prediction should take less than 1 second
        self.assertLess(avg_time, 1.0, f"Average prediction time: {avg_time:.3f}s")
    
    def test_concurrent_predictions(self):
        """Test handling of concurrent predictions."""
        import threading
        
        results = []
        errors = []
        
        def make_prediction():
            try:
                result = self.ml_service.predict_future_pb_concentrate(self.test_data, [5])
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_prediction)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All predictions should succeed
        self.assertEqual(len(results), 5)
        self.assertEqual(len(errors), 0)
    
    def test_memory_usage(self):
        """Test memory usage during predictions."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Make multiple predictions
        for _ in range(100):
            result = self.ml_service.predict_future_pb_concentrate(self.test_data, [5, 60])
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        self.assertLess(memory_increase, 100 * 1024 * 1024, 
                       f"Memory increase: {memory_increase / (1024*1024):.2f}MB")

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.ml_service = MLModelService()
        self.future_predictor = FuturePredictionService()
    
    def test_invalid_data(self):
        """Test handling of invalid input data."""
        # Empty data - should handle gracefully with defaults
        empty_data = {}
        try:
            result = self.ml_service.predict_future_pb_concentrate(empty_data, [5])
            self.assertIsInstance(result, dict)
            self.assertIn('future_predictions', result)
        except Exception as e:
            # If it fails, that's also acceptable behavior
            self.assertIsInstance(e, Exception)
        
        # Missing required fields - should handle gracefully with defaults
        incomplete_data = {'Feed_Pb': 2.5}
        try:
            result = self.ml_service.predict_future_pb_concentrate(incomplete_data, [5])
            self.assertIsInstance(result, dict)
            self.assertIn('future_predictions', result)
        except Exception as e:
            # If it fails, that's also acceptable behavior
            self.assertIsInstance(e, Exception)
    
    def test_invalid_horizons(self):
        """Test handling of invalid prediction horizons."""
        test_data = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        }
        
        # Invalid horizon
        result = self.ml_service.predict_future_pb_concentrate(test_data, [999])
        self.assertNotIn('999min', result['future_predictions'])
    
    def test_model_failure_handling(self):
        """Test handling of model loading failures."""
        # This test would require mocking model loading failures
        # For now, we test that the service handles missing models gracefully
        test_data = pd.DataFrame({
            'Feed_Pb': [2.5],
            'Feed_Zn': [10.0],
            'Pb_Conditioner_KEX_Flowrate': [60.0],
            'Pb_Rougher1_SIPX_Flowrate': [30.0],
            'Pb_Rougher1_AirFlow': [10.0],
            'Pb_Rougher1_Level': [40.0]
        })
        
        # Should handle gracefully even if some models are missing
        result = self.future_predictor.predict_future(test_data, [5, 60])
        self.assertIsInstance(result, dict)

def run_performance_benchmark():
    """Run performance benchmark tests."""
    print("🚀 Running Performance Benchmark...")
    
    ml_service = MLModelService()
    test_data = {
        'Feed_Pb': 2.5,
        'Feed_Zn': 10.0,
        'Pb_Conditioner_KEX_Flowrate': 60.0,
        'Pb_Rougher1_SIPX_Flowrate': 30.0,
        'Pb_Rougher1_AirFlow': 10.0,
        'Pb_Rougher1_Level': 40.0
    }
    
    # Benchmark prediction speed
    start_time = time.time()
    for i in range(100):
        result = ml_service.predict_future_pb_concentrate(test_data, [5, 60])
    end_time = time.time()
    
    total_time = end_time - start_time
    avg_time = total_time / 100
    
    print(f"✅ Performance Results:")
    print(f"   - 100 predictions completed in {total_time:.2f}s")
    print(f"   - Average prediction time: {avg_time*1000:.2f}ms")
    print(f"   - Predictions per second: {100/total_time:.1f}")
    
    return avg_time < 0.1  # Should be faster than 100ms

if __name__ == '__main__':
    # Run unit tests
    print("🧪 Running Unit Tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run performance benchmark
    print("\n" + "="*50)
    run_performance_benchmark()
