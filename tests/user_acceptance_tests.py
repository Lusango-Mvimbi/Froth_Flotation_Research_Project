"""
User Acceptance Testing Framework for Froth Flotation Digital Twin
=================================================================

This module contains comprehensive user acceptance tests for the prediction system,
including test scenarios for different process conditions, validation of prediction
accuracy on historical data, and testing of proactive control recommendations.

Test Categories:
- Process condition scenarios
- Historical data validation
- Proactive control testing
- End-to-end workflow validation
- Performance and reliability testing

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
from services.prediction_validator import PredictionValidator

class TestProcessConditions(unittest.TestCase):
    """Test scenarios for different process conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.ml_service = MLModelService()
        self.future_predictor = FuturePredictionService()
        self.optimizer = FlotationOptimizer()
        self.analyzer = ScenarioAnalyzer()
        self.alerter = PredictiveAlerts()
        self.validator = PredictionValidator()
    
    def test_normal_operating_conditions(self):
        """Test predictions under normal operating conditions."""
        print("🧪 Testing Normal Operating Conditions...")
        
        # Normal operating conditions
        normal_data = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        }
        
        # Get predictions
        predictions = self.ml_service.predict_future_pb_concentrate(normal_data, [5, 60])
        
        # Validate predictions
        self.assertIn('future_predictions', predictions)
        self.assertIn('5min', predictions['future_predictions'])
        self.assertIn('15min', predictions['future_predictions'])
        self.assertIn('30min', predictions['future_predictions'])
        self.assertIn('60min', predictions['future_predictions'])
        
        # Check prediction ranges (should be reasonable for normal conditions)
        for horizon in ['5min', '15min', '30min', '60min']:
            prediction = predictions['future_predictions'][horizon]['prediction']
            self.assertGreater(prediction, 0, f"{horizon} prediction should be positive")
            self.assertLess(prediction, 50, f"{horizon} prediction should be reasonable")
        
        print("✅ Normal operating conditions test passed")
    
    def test_high_feed_grade_conditions(self):
        """Test predictions under high feed grade conditions."""
        print("🧪 Testing High Feed Grade Conditions...")
        
        # High feed grade conditions
        high_feed_data = {
            'Feed_Pb': 5.0,  # High Pb grade
            'Feed_Zn': 15.0,  # High Zn grade
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        }
        
        # Get predictions
        predictions = self.ml_service.predict_future_pb_concentrate(high_feed_data, [5, 15, 30, 60])
        
        # Validate predictions
        self.assertIn('future_predictions', predictions)
        
        # High feed grade should generally lead to higher concentrate predictions
        for horizon in ['5min', '15min', '30min', '60min']:
            prediction = predictions['future_predictions'][horizon]['prediction']
            self.assertGreater(prediction, 0, f"{horizon} prediction should be positive")
        
        print("✅ High feed grade conditions test passed")
    
    def test_low_feed_grade_conditions(self):
        """Test predictions under low feed grade conditions."""
        print("🧪 Testing Low Feed Grade Conditions...")
        
        # Low feed grade conditions
        low_feed_data = {
            'Feed_Pb': 1.0,  # Low Pb grade
            'Feed_Zn': 5.0,   # Low Zn grade
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        }
        
        # Get predictions
        predictions = self.ml_service.predict_future_pb_concentrate(low_feed_data, [5, 15, 30, 60])
        
        # Validate predictions
        self.assertIn('future_predictions', predictions)
        
        # Low feed grade should generally lead to lower concentrate predictions
        for horizon in ['5min', '15min', '30min', '60min']:
            prediction = predictions['future_predictions'][horizon]['prediction']
            self.assertGreater(prediction, 0, f"{horizon} prediction should be positive")
        
        print("✅ Low feed grade conditions test passed")
    
    def test_high_reagent_flow_conditions(self):
        """Test predictions under high reagent flow conditions."""
        print("🧪 Testing High Reagent Flow Conditions...")
        
        # High reagent flow conditions
        high_reagent_data = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 100.0,  # High KEX
            'Pb_Rougher1_SIPX_Flowrate': 50.0,     # High SIPX
            'Pb_Rougher1_AirFlow': 15.0,
            'Pb_Rougher1_Level': 40.0
        }
        
        # Get predictions
        predictions = self.ml_service.predict_future_pb_concentrate(high_reagent_data, [5, 15, 30, 60])
        
        # Validate predictions
        self.assertIn('future_predictions', predictions)
        
        # High reagent flows should affect predictions
        for horizon in ['5min', '15min', '30min', '60min']:
            prediction = predictions['future_predictions'][horizon]['prediction']
            self.assertGreater(prediction, 0, f"{horizon} prediction should be positive")
        
        print("✅ High reagent flow conditions test passed")
    
    def test_low_reagent_flow_conditions(self):
        """Test predictions under low reagent flow conditions."""
        print("🧪 Testing Low Reagent Flow Conditions...")
        
        # Low reagent flow conditions
        low_reagent_data = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 20.0,  # Low KEX
            'Pb_Rougher1_SIPX_Flowrate': 10.0,    # Low SIPX
            'Pb_Rougher1_AirFlow': 5.0,
            'Pb_Rougher1_Level': 40.0
        }
        
        # Get predictions
        predictions = self.ml_service.predict_future_pb_concentrate(low_reagent_data, [5, 15, 30, 60])
        
        # Validate predictions
        self.assertIn('future_predictions', predictions)
        
        # Low reagent flows should affect predictions
        for horizon in ['5min', '15min', '30min', '60min']:
            prediction = predictions['future_predictions'][horizon]['prediction']
            self.assertGreater(prediction, 0, f"{horizon} prediction should be positive")
        
        print("✅ Low reagent flow conditions test passed")

class TestHistoricalDataValidation(unittest.TestCase):
    """Test validation of prediction accuracy on historical data."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = PredictionValidator()
        self.ml_service = MLModelService()
    
    def test_prediction_accuracy_metrics(self):
        """Test calculation of prediction accuracy metrics."""
        print("🧪 Testing Prediction Accuracy Metrics...")
        
        # Create test data
        predicted_values = [10.5, 11.2, 9.8, 10.9, 11.5]
        actual_values = [10.0, 11.0, 10.0, 11.0, 11.0]
        
        # Calculate accuracy metrics
        metrics = self.validator.calculate_accuracy_metrics(predicted_values, actual_values)
        
        # Validate metrics
        self.assertIn('mean_error', metrics)
        self.assertIn('mean_absolute_error', metrics)
        self.assertIn('mean_percentage_error', metrics)
        self.assertIn('rmse', metrics)
        self.assertIn('r_squared', metrics)
        self.assertIn('accuracy_percentage', metrics)
        self.assertIn('within_5_percent', metrics)
        self.assertIn('within_10_percent', metrics)
        self.assertIn('within_20_percent', metrics)
        
        # Check that metrics are reasonable
        self.assertGreaterEqual(metrics['accuracy_percentage'], 0)
        self.assertLessEqual(metrics['accuracy_percentage'], 100)
        self.assertGreaterEqual(metrics['within_5_percent'], 0)
        self.assertLessEqual(metrics['within_5_percent'], 100)
        
        print("✅ Prediction accuracy metrics test passed")
    
    def test_single_prediction_validation(self):
        """Test validation of a single prediction."""
        print("🧪 Testing Single Prediction Validation...")
        
        # Create test prediction data
        prediction_data = {
            'future_predictions': {
                '5min': {
                    'prediction': 10.5,
                    'model_performance': {'r2_score': 0.85}
                },
                '60min': {
                    'prediction': 11.2,
                    'model_performance': {'r2_score': 0.80}
                }
            }
        }
        
        # Create test actual data
        actual_data = {
            'Actual_Pb_Concentrate': 10.0
        }
        
        # Validate prediction
        validation_result = self.validator.validate_prediction(prediction_data, actual_data)
        
        # Validate result
        self.assertTrue(validation_result['success'])
        self.assertIn('validation_summary', validation_result)
        
        summary = validation_result['validation_summary']
        self.assertIn('overall_accuracy', summary)
        self.assertIn('accuracy_rating', summary)
        self.assertIn('horizon_results', summary)
        
        print("✅ Single prediction validation test passed")
    
    def test_historical_predictions_validation(self):
        """Test validation of multiple historical predictions."""
        print("🧪 Testing Historical Predictions Validation...")
        
        # Create test historical data
        historical_data = [
            {
                'prediction_data': {
                    'future_predictions': {
                        '5min': {'prediction': 10.5, 'model_performance': {'r2_score': 0.85}},
                        '60min': {'prediction': 11.2, 'model_performance': {'r2_score': 0.80}}
                    }
                },
                'actual_data': {'Actual_Pb_Concentrate': 10.0},
                'timestamp': datetime.now()
            },
            {
                'prediction_data': {
                    'future_predictions': {
                        '5min': {'prediction': 11.0, 'model_performance': {'r2_score': 0.85}},
                        '60min': {'prediction': 11.5, 'model_performance': {'r2_score': 0.80}}
                    }
                },
                'actual_data': {'Actual_Pb_Concentrate': 11.0},
                'timestamp': datetime.now()
            }
        ]
        
        # Validate historical predictions
        validation_result = self.validator.validate_historical_predictions(historical_data)
        
        # Validate result
        self.assertTrue(validation_result['success'])
        self.assertIn('total_predictions', validation_result)
        self.assertIn('successful_validations', validation_result)
        self.assertIn('comprehensive_report', validation_result)
        
        print("✅ Historical predictions validation test passed")
    
    def test_prediction_drift_detection(self):
        """Test detection of prediction drift."""
        print("🧪 Testing Prediction Drift Detection...")
        
        # Add some validation history for drift detection
        for i in range(60):
            # Simulate declining accuracy over time
            accuracy = 0.95 - (i * 0.005)  # Declining from 95% to 65%
            
            validation_summary = {
                'validation_timestamp': (datetime.now() - timedelta(hours=i)).isoformat(),
                'overall_accuracy': accuracy,
                'accuracy_rating': 'good' if accuracy > 0.8 else 'acceptable',
                'total_predictions_validated': 2,
                'horizon_results': {}
            }
            
            self.validator.validation_history.append(validation_summary)
        
        # Detect drift
        drift_result = self.validator.detect_prediction_drift(window_size=50)
        
        # Validate result
        self.assertTrue(drift_result['success'])
        self.assertIn('drift_analysis', drift_result)
        
        drift_analysis = drift_result['drift_analysis']
        self.assertIn('drift_detected', drift_analysis)
        self.assertIn('drift_magnitude', drift_analysis)
        self.assertIn('drift_direction', drift_analysis)
        
        print("✅ Prediction drift detection test passed")

class TestProactiveControlRecommendations(unittest.TestCase):
    """Test proactive control recommendations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = FlotationOptimizer()
        self.analyzer = ScenarioAnalyzer()
        self.alerter = PredictiveAlerts()
    
    def test_optimization_recommendations(self):
        """Test optimization recommendations generation."""
        print("🧪 Testing Optimization Recommendations...")
        
        # Test data
        test_data = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        }
        
        # Run optimization
        optimization_result = self.optimizer.optimize_multi_horizon(test_data)
        
        # Generate recommendations
        recommendations = self.optimizer.generate_multi_horizon_recommendations(optimization_result)
        
        # Validate recommendations
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Check recommendation content
        for recommendation in recommendations:
            self.assertIsInstance(recommendation, str)
            self.assertGreater(len(recommendation), 10)
        
        print("✅ Optimization recommendations test passed")
    
    def test_scenario_analysis_recommendations(self):
        """Test scenario analysis recommendations."""
        print("🧪 Testing Scenario Analysis Recommendations...")
        
        # Test data
        test_data = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        }
        
        # Test different scenarios
        scenarios = [
            {'Pb_Conditioner_KEX_Flowrate': 10.0},  # Increase KEX
            {'Pb_Conditioner_KEX_Flowrate': -10.0}, # Decrease KEX
            {'Pb_Rougher1_SIPX_Flowrate': 5.0},     # Increase SIPX
            {'Pb_Rougher1_SIPX_Flowrate': -5.0},    # Decrease SIPX
        ]
        
        for i, parameter_changes in enumerate(scenarios):
            # Analyze scenario
            scenario_result = self.analyzer.analyze_scenario(
                test_data, parameter_changes, f"Scenario {i+1}"
            )
            
            # Validate result
            self.assertIn('overall_recommendation', scenario_result)
            self.assertIn('overall_risk_score', scenario_result)
            self.assertIn('overall_benefit_score', scenario_result)
            
            recommendation = scenario_result['overall_recommendation']
            self.assertIsInstance(recommendation, str)
            self.assertGreater(len(recommendation), 10)
        
        print("✅ Scenario analysis recommendations test passed")
    
    def test_predictive_alerts_recommendations(self):
        """Test predictive alerts recommendations."""
        print("🧪 Testing Predictive Alerts Recommendations...")
        
        # Test data that should trigger alerts
        test_data = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        }
        
        # Monitor for alerts
        alerts = self.alerter.monitor_predictions(test_data)
        
        # Validate alerts
        self.assertIsInstance(alerts, list)
        
        # Test preventive actions for each alert
        for alert in alerts:
            suggestions = self.alerter.suggest_preventive_actions(alert)
            
            # Validate suggestions
            self.assertIsInstance(suggestions, list)
            self.assertGreater(len(suggestions), 0)
            
            for suggestion in suggestions:
                self.assertIsInstance(suggestion, str)
                self.assertGreater(len(suggestion), 10)
        
        print("✅ Predictive alerts recommendations test passed")
    
    def test_what_if_scenarios(self):
        """Test what-if scenario generation and analysis."""
        print("🧪 Testing What-If Scenarios...")
        
        # Test data
        test_data = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        }
        
        # Generate what-if scenarios
        scenarios = self.analyzer.generate_what_if_scenarios(test_data)
        
        # Validate scenarios
        self.assertIsInstance(scenarios, list)
        self.assertGreater(len(scenarios), 0)
        
        # Analyze each scenario
        scenario_results = []
        for scenario in scenarios:
            result = self.analyzer.analyze_scenario(
                test_data, 
                scenario['parameter_changes'], 
                scenario['name']
            )
            scenario_results.append(result)
        
        # Compare scenarios
        comparison_result = self.analyzer.compare_scenarios(scenario_results)
        
        # Validate comparison
        self.assertIn('ranked_scenarios', comparison_result)
        self.assertIn('recommendations', comparison_result)
        
        print("✅ What-if scenarios test passed")

class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.ml_service = MLModelService()
        self.optimizer = FlotationOptimizer()
        self.analyzer = ScenarioAnalyzer()
        self.alerter = PredictiveAlerts()
        self.validator = PredictionValidator()
    
    def test_complete_prediction_workflow(self):
        """Test complete prediction and control workflow."""
        print("🧪 Testing Complete Prediction Workflow...")
        
        # 1. Initial process data
        process_data = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        }
        
        # 2. Get future predictions
        predictions = self.ml_service.predict_future_pb_concentrate(process_data, [5, 60])
        self.assertIn('future_predictions', predictions)
        
        # 3. Run optimization
        optimization_result = self.optimizer.optimize_multi_horizon(process_data)
        self.assertTrue(optimization_result['success'])
        
        # 4. Analyze scenarios
        scenario_result = self.analyzer.analyze_scenario(
            process_data, 
            {'Pb_Conditioner_KEX_Flowrate': 10.0}, 
            "Workflow Test"
        )
        self.assertIn('overall_recommendation', scenario_result)
        
        # 5. Monitor for alerts
        alerts = self.alerter.monitor_predictions(process_data)
        self.assertIsInstance(alerts, list)
        
        # 6. Validate predictions (simulate actual data)
        actual_data = {'Actual_Pb_Concentrate': 10.5}
        validation_result = self.validator.validate_prediction(predictions, actual_data)
        self.assertTrue(validation_result['success'])
        
        print("✅ Complete prediction workflow test passed")
    
    def test_performance_under_load(self):
        """Test system performance under load."""
        print("🧪 Testing Performance Under Load...")
        
        test_data = {
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Pb_Conditioner_KEX_Flowrate': 60.0,
            'Pb_Rougher1_SIPX_Flowrate': 30.0,
            'Pb_Rougher1_AirFlow': 10.0,
            'Pb_Rougher1_Level': 40.0
        }
        
        # Test multiple rapid predictions
        start_time = time.time()
        
        for i in range(50):
            predictions = self.ml_service.predict_future_pb_concentrate(test_data, [5, 60])
            optimization = self.optimizer.optimize_multi_horizon(test_data)
            alerts = self.alerter.monitor_predictions(test_data)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance should be reasonable (less than 30 seconds for 50 iterations)
        self.assertLess(total_time, 30, f"Performance test took {total_time:.2f}s, should be under 30s")
        
        avg_time_per_iteration = total_time / 50
        print(f"   Average time per iteration: {avg_time_per_iteration:.3f}s")
        
        print("✅ Performance under load test passed")
    
    def test_system_reliability(self):
        """Test system reliability with various inputs."""
        print("🧪 Testing System Reliability...")
        
        # Test with various input conditions
        test_cases = [
            # Normal conditions
            {
                'Feed_Pb': 2.5, 'Feed_Zn': 10.0, 'Pb_Conditioner_KEX_Flowrate': 60.0,
                'Pb_Rougher1_SIPX_Flowrate': 30.0, 'Pb_Rougher1_AirFlow': 10.0, 'Pb_Rougher1_Level': 40.0
            },
            # Edge cases
            {
                'Feed_Pb': 0.1, 'Feed_Zn': 1.0, 'Pb_Conditioner_KEX_Flowrate': 10.0,
                'Pb_Rougher1_SIPX_Flowrate': 5.0, 'Pb_Rougher1_AirFlow': 2.0, 'Pb_Rougher1_Level': 20.0
            },
            {
                'Feed_Pb': 10.0, 'Feed_Zn': 50.0, 'Pb_Conditioner_KEX_Flowrate': 150.0,
                'Pb_Rougher1_SIPX_Flowrate': 80.0, 'Pb_Rougher1_AirFlow': 25.0, 'Pb_Rougher1_Level': 80.0
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            try:
                # Test predictions
                predictions = self.ml_service.predict_future_pb_concentrate(test_case, [5, 60])
                self.assertIn('future_predictions', predictions)
                
                # Test optimization
                optimization = self.optimizer.optimize_multi_horizon(test_case)
                self.assertTrue(optimization['success'])
                
                # Test alerts
                alerts = self.alerter.monitor_predictions(test_case)
                self.assertIsInstance(alerts, list)
                
                print(f"   Test case {i+1} passed")
                
            except Exception as e:
                self.fail(f"Test case {i+1} failed: {str(e)}")
        
        print("✅ System reliability test passed")

def run_user_acceptance_tests():
    """Run all user acceptance tests."""
    print("🚀 Running User Acceptance Tests...")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestProcessConditions,
        TestHistoricalDataValidation,
        TestProactiveControlRecommendations,
        TestEndToEndWorkflow
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 User Acceptance Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    if not result.failures and not result.errors:
        print("\n✅ All user acceptance tests passed!")
    
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == '__main__':
    # Run user acceptance tests
    success = run_user_acceptance_tests()
    
    if success:
        print("\n🎉 User acceptance testing completed successfully!")
        print("The prediction system is ready for production use.")
    else:
        print("\n⚠️ User acceptance testing completed with issues.")
        print("Please review and fix the failing tests before production deployment.")
