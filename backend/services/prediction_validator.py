"""
Prediction Validator Service for Froth Flotation Digital Twin
============================================================

This service validates prediction accuracy by comparing predictions with actual outcomes,
calculates comprehensive accuracy metrics, and generates detailed validation reports.

Key Features:
- Compare predictions with actual outcomes
- Calculate prediction accuracy metrics
- Generate validation reports
- Track prediction performance over time
- Identify prediction drift and anomalies
- Provide confidence intervals for accuracy

Author: AI Assistant
Date: 2024
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
import logging
from datetime import datetime, timedelta
import sys
import os
from collections import deque
import json
from pathlib import Path

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.ml_model_service import MLModelService
from services.future_prediction_service import FuturePredictionService

logger = logging.getLogger(__name__)

class PredictionValidator:
    """
    Prediction validator service for froth flotation process.
    
    This service validates prediction accuracy by comparing predictions with actual outcomes,
    calculates comprehensive accuracy metrics, and generates detailed validation reports.
    """
    
    def __init__(self):
        """Initialize the prediction validator service"""
        self.ml_service = MLModelService()
        self.future_predictor = FuturePredictionService()
        
        # Validation parameters
        self.validation_horizons = [5, 15, 30, 60]  # minutes
        self.min_validation_age = 30  # minutes - minimum age for validation
        self.max_validation_age = 120  # minutes - maximum age for validation
        
        # Accuracy thresholds
        self.accuracy_thresholds = {
            'excellent': 0.95,  # 95% accuracy
            'good': 0.85,       # 85% accuracy
            'acceptable': 0.75,  # 75% accuracy
            'poor': 0.60        # 60% accuracy
        }
        
        # Validation history
        self.validation_history = deque(maxlen=1000)  # Keep last 1000 validations
        self.prediction_cache = deque(maxlen=500)     # Keep last 500 predictions
        
        # Performance tracking
        self.performance_metrics = {
            'total_validations': 0,
            'successful_validations': 0,
            'average_accuracy': 0.0,
            'accuracy_trend': 'stable',
            'last_validation': None
        }
        
        logger.info("Prediction Validator service initialized")
    
    def validate_prediction(self, 
                          prediction_data: Dict[str, Any],
                          actual_data: Dict[str, float],
                          validation_timestamp: datetime = None) -> Dict[str, Any]:
        """
        Validate a prediction against actual outcomes.
        
        Args:
            prediction_data: Prediction data from the prediction service
            actual_data: Actual process data for comparison
            validation_timestamp: Timestamp for validation (default: now)
            
        Returns:
            Dictionary with validation results
        """
        try:
            validation_time = validation_timestamp or datetime.now()
            
            if 'future_predictions' not in prediction_data:
                return {
                    'success': False,
                    'error': 'Invalid prediction data format'
                }
            
            actual_pb = actual_data.get('Actual_Pb_Concentrate', None)
            if actual_pb is None or actual_pb <= 0:
                return {
                    'success': False,
                    'error': 'No valid actual Pb concentrate data'
                }
            
            validation_results = {}
            overall_accuracy = 0.0
            total_predictions = 0
            
            # Validate each horizon
            for horizon in self.validation_horizons:
                horizon_key = f'{horizon}min'
                
                if horizon_key in prediction_data['future_predictions']:
                    prediction_info = prediction_data['future_predictions'][horizon_key]
                    predicted_pb = prediction_info['prediction']
                    
                    # Calculate accuracy metrics
                    accuracy_metrics = self._calculate_accuracy_metrics(
                        predicted_pb, actual_pb, prediction_info
                    )
                    
                    validation_results[horizon_key] = {
                        'predicted_value': predicted_pb,
                        'actual_value': actual_pb,
                        'accuracy_metrics': accuracy_metrics,
                        'validation_timestamp': validation_time.isoformat(),
                        'prediction_age_minutes': self._calculate_prediction_age(
                            prediction_data.get('prediction_time', validation_time.isoformat()),
                            validation_time
                        )
                    }
                    
                    overall_accuracy += accuracy_metrics['accuracy_percentage']
                    total_predictions += 1
            
            if total_predictions == 0:
                return {
                    'success': False,
                    'error': 'No valid predictions found for validation'
                }
            
            # Calculate overall accuracy
            overall_accuracy /= total_predictions
            
            # Create validation summary
            validation_summary = {
                'validation_timestamp': validation_time.isoformat(),
                'overall_accuracy': overall_accuracy,
                'accuracy_rating': self._get_accuracy_rating(overall_accuracy),
                'total_predictions_validated': total_predictions,
                'horizon_results': validation_results,
                'validation_age_range': {
                    'min_minutes': self.min_validation_age,
                    'max_minutes': self.max_validation_age
                }
            }
            
            # Store validation result
            self.validation_history.append(validation_summary)
            self._update_performance_metrics(validation_summary)
            
            logger.info(f"Validation completed - Overall accuracy: {overall_accuracy:.2%}")
            
            return {
                'success': True,
                'validation_summary': validation_summary
            }
            
        except Exception as e:
            logger.error(f"Prediction validation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_historical_predictions(self, 
                                      historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate multiple historical predictions.
        
        Args:
            historical_data: List of dictionaries with prediction and actual data
            
        Returns:
            Dictionary with comprehensive validation results
        """
        try:
            logger.info(f"Validating {len(historical_data)} historical predictions")
            
            validation_results = []
            successful_validations = 0
            
            for data_point in historical_data:
                prediction_data = data_point.get('prediction_data', {})
                actual_data = data_point.get('actual_data', {})
                timestamp = data_point.get('timestamp', datetime.now())
                
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                
                validation_result = self.validate_prediction(
                    prediction_data, actual_data, timestamp
                )
                
                if validation_result['success']:
                    validation_results.append(validation_result['validation_summary'])
                    successful_validations += 1
            
            # Generate comprehensive report
            comprehensive_report = self._generate_comprehensive_report(validation_results)
            
            logger.info(f"Historical validation completed - {successful_validations}/{len(historical_data)} successful")
            
            return {
                'success': True,
                'total_predictions': len(historical_data),
                'successful_validations': successful_validations,
                'comprehensive_report': comprehensive_report
            }
            
        except Exception as e:
            logger.error(f"Historical validation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def calculate_accuracy_metrics(self, 
                                 predicted_values: List[float],
                                 actual_values: List[float]) -> Dict[str, float]:
        """
        Calculate comprehensive accuracy metrics.
        
        Args:
            predicted_values: List of predicted values
            actual_values: List of actual values
            
        Returns:
            Dictionary with accuracy metrics
        """
        try:
            if len(predicted_values) != len(actual_values):
                raise ValueError("Predicted and actual values must have the same length")
            
            if len(predicted_values) == 0:
                return {}
            
            # Convert to numpy arrays for calculations
            pred = np.array(predicted_values)
            actual = np.array(actual_values)
            
            # Calculate basic metrics
            errors = pred - actual
            absolute_errors = np.abs(errors)
            percentage_errors = np.abs(errors / actual) * 100
            
            # Mean metrics
            mean_error = np.mean(errors)
            mean_absolute_error = np.mean(absolute_errors)
            mean_percentage_error = np.mean(percentage_errors)
            
            # Root mean square error
            rmse = np.sqrt(np.mean(errors ** 2))
            
            # R-squared (coefficient of determination)
            ss_res = np.sum(errors ** 2)
            ss_tot = np.sum((actual - np.mean(actual)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Accuracy percentage (100% - mean percentage error)
            accuracy_percentage = max(0, 100 - mean_percentage_error)
            
            # Additional metrics
            within_5_percent = np.sum(percentage_errors <= 5) / len(percentage_errors) * 100
            within_10_percent = np.sum(percentage_errors <= 10) / len(percentage_errors) * 100
            within_20_percent = np.sum(percentage_errors <= 20) / len(percentage_errors) * 100
            
            return {
                'mean_error': mean_error,
                'mean_absolute_error': mean_absolute_error,
                'mean_percentage_error': mean_percentage_error,
                'rmse': rmse,
                'r_squared': r_squared,
                'accuracy_percentage': accuracy_percentage,
                'within_5_percent': within_5_percent,
                'within_10_percent': within_10_percent,
                'within_20_percent': within_20_percent,
                'total_predictions': len(predicted_values)
            }
            
        except Exception as e:
            logger.error(f"Accuracy metrics calculation failed: {e}")
            return {}
    
    def generate_validation_report(self, 
                                 validation_period: str = 'all',
                                 output_format: str = 'json') -> Dict[str, Any]:
        """
        Generate a comprehensive validation report.
        
        Args:
            validation_period: Time period for report ('all', 'last_24h', 'last_7d', 'last_30d')
            output_format: Output format ('json', 'csv', 'html')
            
        Returns:
            Dictionary with validation report
        """
        try:
            logger.info(f"Generating validation report for period: {validation_period}")
            
            # Filter validation history based on period
            filtered_history = self._filter_validation_history(validation_period)
            
            if not filtered_history:
                return {
                    'success': False,
                    'error': f'No validation data available for period: {validation_period}'
                }
            
            # Generate report
            report = self._generate_detailed_report(filtered_history, validation_period)
            
            # Add performance trends
            report['performance_trends'] = self._calculate_performance_trends(filtered_history)
            
            # Add recommendations
            report['recommendations'] = self._generate_validation_recommendations(report)
            
            # Format output
            if output_format == 'csv':
                report['csv_data'] = self._convert_to_csv(report)
            elif output_format == 'html':
                report['html_data'] = self._convert_to_html(report)
            
            logger.info("Validation report generated successfully")
            
            return {
                'success': True,
                'report': report,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Validation report generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def detect_prediction_drift(self, 
                              window_size: int = 50,
                              drift_threshold: float = 0.15) -> Dict[str, Any]:
        """
        Detect prediction drift over time.
        
        Args:
            window_size: Number of recent validations to analyze
            drift_threshold: Threshold for detecting drift (15% by default)
            
        Returns:
            Dictionary with drift detection results
        """
        try:
            if len(self.validation_history) < window_size:
                return {
                    'success': False,
                    'error': f'Insufficient data for drift detection (need {window_size}, have {len(self.validation_history)})'
                }
            
            # Get recent validations
            recent_validations = list(self.validation_history)[-window_size:]
            
            # Extract accuracy values
            accuracies = [v['overall_accuracy'] for v in recent_validations]
            
            # Calculate drift metrics
            early_accuracies = accuracies[:window_size//2]
            late_accuracies = accuracies[window_size//2:]
            
            early_mean = np.mean(early_accuracies)
            late_mean = np.mean(late_accuracies)
            
            drift_magnitude = abs(late_mean - early_mean) / early_mean if early_mean > 0 else 0
            drift_direction = 'improving' if late_mean > early_mean else 'declining'
            
            # Detect significant drift
            significant_drift = drift_magnitude > drift_threshold
            
            # Calculate trend
            trend_slope = np.polyfit(range(len(accuracies)), accuracies, 1)[0]
            
            drift_result = {
                'drift_detected': significant_drift,
                'drift_magnitude': drift_magnitude,
                'drift_direction': drift_direction,
                'early_period_accuracy': early_mean,
                'late_period_accuracy': late_mean,
                'trend_slope': trend_slope,
                'window_size': window_size,
                'threshold': drift_threshold,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            if significant_drift:
                logger.warning(f"Prediction drift detected: {drift_magnitude:.2%} {drift_direction}")
            
            return {
                'success': True,
                'drift_analysis': drift_result
            }
            
        except Exception as e:
            logger.error(f"Drift detection failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive validation statistics.
        
        Returns:
            Dictionary with validation statistics
        """
        try:
            if not self.validation_history:
                return {
                    'total_validations': 0,
                    'message': 'No validation data available'
                }
            
            # Calculate statistics
            accuracies = [v['overall_accuracy'] for v in self.validation_history]
            
            stats = {
                'total_validations': len(self.validation_history),
                'average_accuracy': np.mean(accuracies),
                'accuracy_std': np.std(accuracies),
                'min_accuracy': np.min(accuracies),
                'max_accuracy': np.max(accuracies),
                'median_accuracy': np.median(accuracies),
                'accuracy_percentiles': {
                    '25th': np.percentile(accuracies, 25),
                    '75th': np.percentile(accuracies, 75),
                    '90th': np.percentile(accuracies, 90),
                    '95th': np.percentile(accuracies, 95)
                },
                'accuracy_distribution': {
                    'excellent': len([a for a in accuracies if a >= self.accuracy_thresholds['excellent']]),
                    'good': len([a for a in accuracies if self.accuracy_thresholds['good'] <= a < self.accuracy_thresholds['excellent']]),
                    'acceptable': len([a for a in accuracies if self.accuracy_thresholds['acceptable'] <= a < self.accuracy_thresholds['good']]),
                    'poor': len([a for a in accuracies if a < self.accuracy_thresholds['acceptable']])
                },
                'last_validation': self.performance_metrics['last_validation'],
                'validation_trend': self.performance_metrics['accuracy_trend']
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Statistics calculation failed: {e}")
            return {'error': str(e)}
    
    def _calculate_accuracy_metrics(self, 
                                  predicted_value: float,
                                  actual_value: float,
                                  prediction_info: Dict[str, Any]) -> Dict[str, float]:
        """Calculate accuracy metrics for a single prediction."""
        try:
            error = predicted_value - actual_value
            absolute_error = abs(error)
            percentage_error = abs(error / actual_value) * 100 if actual_value > 0 else 0
            
            accuracy_percentage = max(0, 100 - percentage_error)
            
            # Get model confidence
            model_confidence = prediction_info.get('model_performance', {}).get('r2_score', 0.5)
            
            return {
                'error': error,
                'absolute_error': absolute_error,
                'percentage_error': percentage_error,
                'accuracy_percentage': accuracy_percentage,
                'model_confidence': model_confidence,
                'within_5_percent': percentage_error <= 5,
                'within_10_percent': percentage_error <= 10,
                'within_20_percent': percentage_error <= 20
            }
            
        except Exception as e:
            logger.error(f"Accuracy metrics calculation failed: {e}")
            return {}
    
    def _calculate_prediction_age(self, prediction_time: str, validation_time: datetime) -> float:
        """Calculate the age of a prediction in minutes."""
        try:
            if isinstance(prediction_time, str):
                pred_time = datetime.fromisoformat(prediction_time)
            else:
                pred_time = prediction_time
            
            age_minutes = (validation_time - pred_time).total_seconds() / 60
            return max(0, age_minutes)
            
        except Exception as e:
            logger.error(f"Prediction age calculation failed: {e}")
            return 0.0
    
    def _get_accuracy_rating(self, accuracy: float) -> str:
        """Get accuracy rating based on thresholds."""
        if accuracy >= self.accuracy_thresholds['excellent']:
            return 'excellent'
        elif accuracy >= self.accuracy_thresholds['good']:
            return 'good'
        elif accuracy >= self.accuracy_thresholds['acceptable']:
            return 'acceptable'
        else:
            return 'poor'
    
    def _update_performance_metrics(self, validation_summary: Dict[str, Any]):
        """Update performance metrics with new validation."""
        self.performance_metrics['total_validations'] += 1
        self.performance_metrics['successful_validations'] += 1
        self.performance_metrics['last_validation'] = validation_summary['validation_timestamp']
        
        # Update average accuracy
        current_avg = self.performance_metrics['average_accuracy']
        new_accuracy = validation_summary['overall_accuracy']
        total_validations = self.performance_metrics['total_validations']
        
        self.performance_metrics['average_accuracy'] = (
            (current_avg * (total_validations - 1) + new_accuracy) / total_validations
        )
    
    def _filter_validation_history(self, period: str) -> List[Dict[str, Any]]:
        """Filter validation history based on time period."""
        if period == 'all':
            return list(self.validation_history)
        
        now = datetime.now()
        cutoff_time = None
        
        if period == 'last_24h':
            cutoff_time = now - timedelta(hours=24)
        elif period == 'last_7d':
            cutoff_time = now - timedelta(days=7)
        elif period == 'last_30d':
            cutoff_time = now - timedelta(days=30)
        else:
            return list(self.validation_history)
        
        filtered_history = []
        for validation in self.validation_history:
            validation_time = datetime.fromisoformat(validation['validation_timestamp'])
            if validation_time >= cutoff_time:
                filtered_history.append(validation)
        
        return filtered_history
    
    def _generate_detailed_report(self, 
                                validations: List[Dict[str, Any]], 
                                period: str) -> Dict[str, Any]:
        """Generate detailed validation report."""
        if not validations:
            return {}
        
        # Calculate overall statistics
        accuracies = [v['overall_accuracy'] for v in validations]
        
        report = {
            'period': period,
            'total_validations': len(validations),
            'average_accuracy': np.mean(accuracies),
            'accuracy_std': np.std(accuracies),
            'min_accuracy': np.min(accuracies),
            'max_accuracy': np.max(accuracies),
            'accuracy_rating_distribution': {},
            'horizon_performance': {},
            'validation_details': validations
        }
        
        # Calculate accuracy rating distribution
        for validation in validations:
            rating = validation['accuracy_rating']
            report['accuracy_rating_distribution'][rating] = report['accuracy_rating_distribution'].get(rating, 0) + 1
        
        # Calculate horizon performance
        for validation in validations:
            for horizon, result in validation['horizon_results'].items():
                if horizon not in report['horizon_performance']:
                    report['horizon_performance'][horizon] = []
                report['horizon_performance'][horizon].append(
                    result['accuracy_metrics']['accuracy_percentage']
                )
        
        # Calculate average accuracy per horizon
        for horizon in report['horizon_performance']:
            accuracies = report['horizon_performance'][horizon]
            report['horizon_performance'][horizon] = {
                'average_accuracy': np.mean(accuracies),
                'accuracy_std': np.std(accuracies),
                'total_predictions': len(accuracies)
            }
        
        return report
    
    def _calculate_performance_trends(self, validations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance trends over time."""
        if len(validations) < 2:
            return {'trend': 'insufficient_data'}
        
        accuracies = [v['overall_accuracy'] for v in validations]
        
        # Calculate trend
        x = range(len(accuracies))
        trend_slope = np.polyfit(x, accuracies, 1)[0]
        
        if trend_slope > 0.01:
            trend = 'improving'
        elif trend_slope < -0.01:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'trend_slope': trend_slope,
            'recent_accuracy': accuracies[-1] if accuracies else 0,
            'trend_strength': abs(trend_slope)
        }
    
    def _generate_validation_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        avg_accuracy = report.get('average_accuracy', 0)
        
        if avg_accuracy < self.accuracy_thresholds['acceptable']:
            recommendations.append("🚨 CRITICAL: Prediction accuracy is below acceptable threshold. Consider model retraining.")
        elif avg_accuracy < self.accuracy_thresholds['good']:
            recommendations.append("⚠️ WARNING: Prediction accuracy needs improvement. Review model performance and data quality.")
        
        # Check for horizon-specific issues
        horizon_performance = report.get('horizon_performance', {})
        for horizon, perf in horizon_performance.items():
            if perf['average_accuracy'] < self.accuracy_thresholds['acceptable']:
                recommendations.append(f"⚠️ {horizon} predictions show poor accuracy. Investigate model performance for this horizon.")
        
        # Check trends
        trends = report.get('performance_trends', {})
        if trends.get('trend') == 'declining':
            recommendations.append("📉 Prediction accuracy is declining. Monitor for model drift and consider intervention.")
        
        if not recommendations:
            recommendations.append("✅ Prediction accuracy is within acceptable ranges. Continue monitoring.")
        
        return recommendations
    
    def _convert_to_csv(self, report: Dict[str, Any]) -> str:
        """Convert report to CSV format."""
        # Implementation for CSV conversion
        return "CSV conversion not implemented yet"
    
    def _convert_to_html(self, report: Dict[str, Any]) -> str:
        """Convert report to HTML format."""
        # Implementation for HTML conversion
        return "HTML conversion not implemented yet"
    
    def _generate_comprehensive_report(self, validations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        if not validations:
            return {}
        
        # Calculate overall statistics
        accuracies = [v['overall_accuracy'] for v in validations]
        
        return {
            'total_validations': len(validations),
            'average_accuracy': np.mean(accuracies),
            'accuracy_std': np.std(accuracies),
            'min_accuracy': np.min(accuracies),
            'max_accuracy': np.max(accuracies),
            'accuracy_rating_distribution': {},
            'validation_details': validations
        }
