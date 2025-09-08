"""
Predictive Alerts Service for Froth Flotation Digital Twin
========================================================

This service monitors future predictions and generates alerts when problems are indicated,
suggests preventive actions, and tracks prediction accuracy over time.

Key Features:
- Monitor future predictions for potential problems
- Generate alerts based on prediction thresholds
- Suggest preventive actions
- Track prediction accuracy over time
- Alert severity classification
- Historical alert tracking

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

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.ml_model_service import MLModelService
from services.future_prediction_service import FuturePredictionService

logger = logging.getLogger(__name__)

class Alert:
    """Alert class to represent a predictive alert."""
    
    def __init__(self, 
                 alert_type: str,
                 severity: str,
                 message: str,
                 prediction_data: Dict[str, Any],
                 timestamp: datetime = None):
        self.alert_type = alert_type
        self.severity = severity  # 'critical', 'warning', 'info'
        self.message = message
        self.prediction_data = prediction_data
        self.timestamp = timestamp or datetime.now()
        self.acknowledged = False
        self.resolved = False
        self.alert_id = f"{alert_type}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}"

class PredictiveAlerts:
    """
    Predictive alerts service for froth flotation process monitoring.
    
    This service monitors future predictions and generates alerts when potential
    problems are detected, suggests preventive actions, and tracks accuracy.
    """
    
    def __init__(self):
        """Initialize the predictive alerts service"""
        self.ml_service = MLModelService()
        self.future_predictor = FuturePredictionService()
        
        # Alert thresholds
        self.alert_thresholds = {
            'critical': {
                'pb_concentrate_min': 7.0,    # Below 7% Pb concentrate
                'pb_concentrate_max': 15.0,   # Above 15% Pb concentrate
                'confidence_min': 0.6,        # Below 60% confidence
                'trend_threshold': -3.0       # Declining by more than 3%
            },
            'warning': {
                'pb_concentrate_min': 8.0,    # Below 8% Pb concentrate
                'pb_concentrate_max': 13.0,   # Above 13% Pb concentrate
                'confidence_min': 0.7,        # Below 70% confidence
                'trend_threshold': -2.0       # Declining by more than 2%
            },
            'info': {
                'pb_concentrate_min': 9.0,    # Below 9% Pb concentrate
                'pb_concentrate_max': 12.0,   # Above 12% Pb concentrate
                'confidence_min': 0.8,        # Below 80% confidence
                'trend_threshold': -1.0       # Declining by more than 1%
            }
        }
        
        # Target ranges
        self.target_ranges = {
            'optimal_min': 9.5,
            'optimal_max': 11.5,
            'acceptable_min': 8.0,
            'acceptable_max': 13.0
        }
        
        # Alert history
        self.alert_history = deque(maxlen=1000)  # Keep last 1000 alerts
        self.active_alerts = {}  # alert_id -> Alert
        
        # Accuracy tracking
        self.accuracy_history = deque(maxlen=100)  # Keep last 100 accuracy measurements
        self.prediction_history = deque(maxlen=50)  # Keep last 50 predictions for validation
        
        logger.info("Predictive Alerts service initialized")
    
    def monitor_predictions(self, current_data: Dict[str, float]) -> List[Alert]:
        """
        Monitor future predictions and generate alerts if needed.
        
        Args:
            current_data: Current process data
            
        Returns:
            List of generated alerts
        """
        try:
            logger.info("Monitoring predictions for alerts...")
            
            alerts = []
            
            # Get future predictions using proper data preparation
            current_data_df = self.ml_service._prepare_data_for_future_prediction(current_data)
            future_predictions = self.future_predictor.predict_future(
                current_data_df, 
                horizons=[5, 15, 30, 60]  # Only use available models
            )
            
            # Check each horizon for potential issues
            for horizon_key, prediction in future_predictions.items():
                horizon_alerts = self._check_horizon_predictions(
                    horizon_key, prediction, current_data
                )
                alerts.extend(horizon_alerts)
            
            # Check for trend-based alerts
            trend_alerts = self._check_trend_alerts(future_predictions, current_data)
            alerts.extend(trend_alerts)
            
            # Check for confidence-based alerts
            confidence_alerts = self._check_confidence_alerts(future_predictions)
            alerts.extend(confidence_alerts)
            
            # Add alerts to history and active alerts
            for alert in alerts:
                self.alert_history.append(alert)
                self.active_alerts[alert.alert_id] = alert
            
            # Store prediction for accuracy tracking
            self.prediction_history.append({
                'timestamp': datetime.now(),
                'predictions': future_predictions,
                'current_data': current_data
            })
            
            logger.info(f"Generated {len(alerts)} alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"Prediction monitoring failed: {e}")
            return []
    
    def suggest_preventive_actions(self, alert: Alert) -> List[str]:
        """
        Suggest preventive actions based on alert type and severity.
        
        Args:
            alert: The alert to generate suggestions for
            
        Returns:
            List of suggested preventive actions
        """
        suggestions = []
        
        try:
            if alert.alert_type == 'low_concentrate':
                if alert.severity == 'critical':
                    suggestions.extend([
                        "🚨 IMMEDIATE ACTION REQUIRED: Increase KEX flow rate by 10-15 L/min",
                        "🚨 Increase SIPX flow rate by 5-8 L/min",
                        "🚨 Check feed grade and adjust if necessary",
                        "🚨 Monitor air flow and reduce if too high"
                    ])
                elif alert.severity == 'warning':
                    suggestions.extend([
                        "⚠️ Increase KEX flow rate by 5-10 L/min",
                        "⚠️ Increase SIPX flow rate by 2-5 L/min",
                        "⚠️ Check recent feed composition changes"
                    ])
                else:  # info
                    suggestions.extend([
                        "ℹ️ Consider increasing KEX flow rate by 2-5 L/min",
                        "ℹ️ Monitor trend for further deterioration"
                    ])
            
            elif alert.alert_type == 'high_concentrate':
                if alert.severity == 'critical':
                    suggestions.extend([
                        "🚨 IMMEDIATE ACTION REQUIRED: Decrease KEX flow rate by 10-15 L/min",
                        "🚨 Decrease SIPX flow rate by 5-8 L/min",
                        "🚨 Check for feed grade changes",
                        "🚨 Increase air flow if necessary"
                    ])
                elif alert.severity == 'warning':
                    suggestions.extend([
                        "⚠️ Decrease KEX flow rate by 5-10 L/min",
                        "⚠️ Decrease SIPX flow rate by 2-5 L/min",
                        "⚠️ Monitor for over-recovery conditions"
                    ])
                else:  # info
                    suggestions.extend([
                        "ℹ️ Consider decreasing KEX flow rate by 2-5 L/min",
                        "ℹ️ Monitor trend for further improvement"
                    ])
            
            elif alert.alert_type == 'low_confidence':
                suggestions.extend([
                    "🔍 Verify sensor readings and data quality",
                    "🔍 Check for unusual process conditions",
                    "🔍 Consider manual verification of predictions",
                    "🔍 Review recent model performance"
                ])
            
            elif alert.alert_type == 'trend_decline':
                suggestions.extend([
                    "📉 Investigate root cause of declining trend",
                    "📉 Check feed composition and quality",
                    "📉 Review reagent effectiveness",
                    "📉 Consider process parameter adjustments"
                ])
            
            # Add general suggestions based on severity
            if alert.severity == 'critical':
                suggestions.append("🚨 CRITICAL: Immediate operator intervention required")
            elif alert.severity == 'warning':
                suggestions.append("⚠️ WARNING: Monitor closely and prepare for action")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate preventive actions: {e}")
            return ["Error generating suggestions - check system logs"]
    
    def track_prediction_accuracy(self, actual_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Track prediction accuracy by comparing predictions with actual values.
        
        Args:
            actual_data: Actual process data for comparison
            
        Returns:
            Dictionary with accuracy metrics
        """
        try:
            if not self.prediction_history:
                return {'error': 'No prediction history available'}
            
            # Find the most recent prediction that's old enough to validate
            current_time = datetime.now()
            validation_window = 30  # minutes
            
            accuracy_results = {}
            
            for prediction_entry in reversed(list(self.prediction_history)):
                prediction_age = (current_time - prediction_entry['timestamp']).total_seconds() / 60
                
                if prediction_age >= validation_window:
                    # This prediction is old enough to validate
                    predictions = prediction_entry['predictions']
                    actual_pb = actual_data.get('Actual_Pb_Concentrate', 0)
                    
                    if actual_pb > 0:
                        # Calculate accuracy for each horizon
                        for horizon_key, prediction in predictions.items():
                            predicted_pb = prediction['prediction']
                            error = abs(predicted_pb - actual_pb)
                            percentage_error = (error / actual_pb) * 100 if actual_pb > 0 else 0
                            
                            accuracy_results[horizon_key] = {
                                'predicted': predicted_pb,
                                'actual': actual_pb,
                                'error': error,
                                'percentage_error': percentage_error,
                                'accuracy': max(0, 100 - percentage_error),
                                'prediction_age_minutes': prediction_age
                            }
                    
                    break  # Use the most recent valid prediction
            
            if accuracy_results:
                # Calculate overall accuracy metrics
                avg_accuracy = np.mean([r['accuracy'] for r in accuracy_results.values()])
                avg_error = np.mean([r['percentage_error'] for r in accuracy_results.values()])
                
                # Store accuracy measurement
                accuracy_measurement = {
                    'timestamp': datetime.now(),
                    'overall_accuracy': avg_accuracy,
                    'overall_error': avg_error,
                    'horizon_accuracies': accuracy_results
                }
                
                self.accuracy_history.append(accuracy_measurement)
                
                return {
                    'overall_accuracy': avg_accuracy,
                    'overall_error': avg_error,
                    'horizon_accuracies': accuracy_results,
                    'measurements_count': len(self.accuracy_history)
                }
            else:
                return {'message': 'No predictions available for validation'}
                
        except Exception as e:
            logger.error(f"Accuracy tracking failed: {e}")
            return {'error': str(e)}
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """
        Get summary of current alerts and alert history.
        
        Returns:
            Dictionary with alert summary
        """
        try:
            # Count alerts by severity
            severity_counts = {'critical': 0, 'warning': 0, 'info': 0}
            type_counts = {}
            
            for alert in self.active_alerts.values():
                severity_counts[alert.severity] += 1
                type_counts[alert.alert_type] = type_counts.get(alert.alert_type, 0) + 1
            
            # Get recent alerts (last 24 hours)
            recent_alerts = [
                alert for alert in self.alert_history
                if (datetime.now() - alert.timestamp).total_seconds() < 86400  # 24 hours
            ]
            
            # Calculate accuracy trends
            accuracy_trend = self._calculate_accuracy_trend()
            
            return {
                'active_alerts_count': len(self.active_alerts),
                'severity_distribution': severity_counts,
                'type_distribution': type_counts,
                'recent_alerts_count': len(recent_alerts),
                'total_alerts_history': len(self.alert_history),
                'accuracy_trend': accuracy_trend,
                'last_accuracy_measurement': len(self.accuracy_history)
            }
            
        except Exception as e:
            logger.error(f"Alert summary generation failed: {e}")
            return {'error': str(e)}
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: ID of the alert to acknowledge
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].acknowledged = True
                logger.info(f"Alert {alert_id} acknowledged")
                return True
            else:
                logger.warning(f"Alert {alert_id} not found")
                return False
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        Mark an alert as resolved.
        
        Args:
            alert_id: ID of the alert to resolve
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].resolved = True
                # Remove from active alerts
                del self.active_alerts[alert_id]
                logger.info(f"Alert {alert_id} resolved")
                return True
            else:
                logger.warning(f"Alert {alert_id} not found")
                return False
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False
    
    def _check_horizon_predictions(self, horizon_key: str, prediction: Dict[str, Any], current_data: Dict[str, float]) -> List[Alert]:
        """Check predictions for a specific horizon and generate alerts if needed."""
        alerts = []
        
        try:
            predicted_pb = prediction['prediction']
            confidence = prediction['model_performance']['r2_score']
            
            # Check for low concentrate alerts
            if predicted_pb < self.alert_thresholds['critical']['pb_concentrate_min']:
                alerts.append(Alert(
                    'low_concentrate',
                    'critical',
                    f"CRITICAL: {horizon_key} prediction shows critically low Pb concentrate ({predicted_pb:.1f}%)",
                    prediction
                ))
            elif predicted_pb < self.alert_thresholds['warning']['pb_concentrate_min']:
                alerts.append(Alert(
                    'low_concentrate',
                    'warning',
                    f"WARNING: {horizon_key} prediction shows low Pb concentrate ({predicted_pb:.1f}%)",
                    prediction
                ))
            elif predicted_pb < self.alert_thresholds['info']['pb_concentrate_min']:
                alerts.append(Alert(
                    'low_concentrate',
                    'info',
                    f"INFO: {horizon_key} prediction shows below-target Pb concentrate ({predicted_pb:.1f}%)",
                    prediction
                ))
            
            # Check for high concentrate alerts
            if predicted_pb > self.alert_thresholds['critical']['pb_concentrate_max']:
                alerts.append(Alert(
                    'high_concentrate',
                    'critical',
                    f"CRITICAL: {horizon_key} prediction shows critically high Pb concentrate ({predicted_pb:.1f}%)",
                    prediction
                ))
            elif predicted_pb > self.alert_thresholds['warning']['pb_concentrate_max']:
                alerts.append(Alert(
                    'high_concentrate',
                    'warning',
                    f"WARNING: {horizon_key} prediction shows high Pb concentrate ({predicted_pb:.1f}%)",
                    prediction
                ))
            elif predicted_pb > self.alert_thresholds['info']['pb_concentrate_max']:
                alerts.append(Alert(
                    'high_concentrate',
                    'info',
                    f"INFO: {horizon_key} prediction shows above-target Pb concentrate ({predicted_pb:.1f}%)",
                    prediction
                ))
            
            return alerts
            
        except Exception as e:
            logger.error(f"Horizon prediction check failed: {e}")
            return []
    
    def _check_trend_alerts(self, predictions: Dict[str, Any], current_data: Dict[str, float]) -> List[Alert]:
        """Check for trend-based alerts."""
        alerts = []
        
        try:
            # Get current Pb concentrate
            current_pb = current_data.get('Actual_Pb_Concentrate', 0)
            
            if current_pb > 0:
                # Check 5-minute prediction for trend
                if '5min' in predictions:
                    predicted_5min = predictions['5min']['prediction']
                    change_5min = predicted_5min - current_pb
                    
                    if change_5min < self.alert_thresholds['critical']['trend_threshold']:
                        alerts.append(Alert(
                            'trend_decline',
                            'critical',
                            f"CRITICAL: Rapid decline predicted in 5 minutes ({change_5min:.1f}% change)",
                            predictions['5min']
                        ))
                    elif change_5min < self.alert_thresholds['warning']['trend_threshold']:
                        alerts.append(Alert(
                            'trend_decline',
                            'warning',
                            f"WARNING: Decline predicted in 5 minutes ({change_5min:.1f}% change)",
                            predictions['5min']
                        ))
            
            return alerts
            
        except Exception as e:
            logger.error(f"Trend alert check failed: {e}")
            return []
    
    def _check_confidence_alerts(self, predictions: Dict[str, Any]) -> List[Alert]:
        """Check for confidence-based alerts."""
        alerts = []
        
        try:
            for horizon_key, prediction in predictions.items():
                confidence = prediction['model_performance']['r2_score']
                
                if confidence < self.alert_thresholds['critical']['confidence_min']:
                    alerts.append(Alert(
                        'low_confidence',
                        'critical',
                        f"CRITICAL: Low prediction confidence for {horizon_key} ({confidence:.1%})",
                        prediction
                    ))
                elif confidence < self.alert_thresholds['warning']['confidence_min']:
                    alerts.append(Alert(
                        'low_confidence',
                        'warning',
                        f"WARNING: Reduced prediction confidence for {horizon_key} ({confidence:.1%})",
                        prediction
                    ))
            
            return alerts
            
        except Exception as e:
            logger.error(f"Confidence alert check failed: {e}")
            return []
    
    def _calculate_accuracy_trend(self) -> Dict[str, Any]:
        """Calculate accuracy trend from recent measurements."""
        try:
            if len(self.accuracy_history) < 2:
                return {'trend': 'insufficient_data', 'message': 'Need more accuracy measurements'}
            
            # Get recent accuracy measurements
            recent_accuracies = [m['overall_accuracy'] for m in list(self.accuracy_history)[-10:]]
            
            if len(recent_accuracies) < 2:
                return {'trend': 'insufficient_data', 'message': 'Need more recent measurements'}
            
            # Calculate trend
            trend_slope = np.polyfit(range(len(recent_accuracies)), recent_accuracies, 1)[0]
            avg_accuracy = np.mean(recent_accuracies)
            
            if trend_slope > 1.0:
                trend = 'improving'
            elif trend_slope < -1.0:
                trend = 'declining'
            else:
                trend = 'stable'
            
            return {
                'trend': trend,
                'trend_slope': trend_slope,
                'average_accuracy': avg_accuracy,
                'measurements_count': len(recent_accuracies)
            }
            
        except Exception as e:
            logger.error(f"Accuracy trend calculation failed: {e}")
            return {'trend': 'error', 'error': str(e)}
