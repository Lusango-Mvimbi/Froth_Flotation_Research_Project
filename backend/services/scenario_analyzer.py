"""
Scenario Analyzer Service for Froth Flotation Digital Twin
==========================================================

This service performs "what-if" analysis for different control settings,
risk assessment for parameter changes, and provides optimal control strategy recommendations.

Key Features:
- What-if analysis for different control settings
- Risk assessment for parameter changes
- Optimal control strategy recommendations
- Scenario comparison and ranking
- Uncertainty quantification

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

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.ml_model_service import MLModelService
from services.future_prediction_service import FuturePredictionService

logger = logging.getLogger(__name__)

class ScenarioAnalyzer:
    """
    Scenario analyzer for froth flotation process optimization.
    
    This analyzer performs what-if analysis, risk assessment, and provides
    optimal control strategy recommendations based on future predictions.
    """
    
    def __init__(self):
        """Initialize the scenario analyzer with ML and prediction services"""
        self.ml_service = MLModelService()
        self.future_predictor = FuturePredictionService()
        
        # Analysis parameters (only use available models)
        self.analysis_horizons = [5, 15, 30, 60]  # minutes - only horizons with trained models
        self.risk_thresholds = {
            'high_risk': 0.3,      # 30% probability of failure
            'medium_risk': 0.15,   # 15% probability of failure
            'low_risk': 0.05       # 5% probability of failure
        }
        
        # Target ranges for Pb concentrate
        self.target_ranges = {
            'optimal_min': 9.5,
            'optimal_max': 11.5,
            'acceptable_min': 8.0,
            'acceptable_max': 13.0
        }
        
        logger.info("Scenario Analyzer initialized")
    
    def analyze_scenario(self, 
                        base_data: Dict[str, float],
                        parameter_changes: Dict[str, float],
                        scenario_name: str = "Custom Scenario") -> Dict[str, Any]:
        """
        Analyze a specific scenario with parameter changes.
        
        Args:
            base_data: Base process data
            parameter_changes: Dictionary of parameter changes (e.g., {'KEX': +5, 'SIPX': -2})
            scenario_name: Name of the scenario
            
        Returns:
            Dictionary with scenario analysis results
        """
        try:
            logger.info(f"Analyzing scenario: {scenario_name}")
            
            # Create modified data with parameter changes
            modified_data = base_data.copy()
            for param, change in parameter_changes.items():
                if param in modified_data:
                    modified_data[param] += change
            
            # Get future predictions for both scenarios using proper data preparation
            base_data_df = self.ml_service._prepare_data_for_future_prediction(base_data)
            base_predictions = self.future_predictor.predict_future(
                base_data_df, 
                horizons=self.analysis_horizons
            )
            
            modified_data_df = self.ml_service._prepare_data_for_future_prediction(modified_data)
            modified_predictions = self.future_predictor.predict_future(
                modified_data_df, 
                horizons=self.analysis_horizons
            )
            
            # Analyze each horizon
            horizon_analysis = {}
            overall_risk_score = 0
            overall_benefit_score = 0
            
            for horizon in self.analysis_horizons:
                horizon_key = f'{horizon}min'
                
                if horizon_key in base_predictions and horizon_key in modified_predictions:
                    base_pred = base_predictions[horizon_key]
                    modified_pred = modified_predictions[horizon_key]
                    
                    # Calculate metrics
                    base_pb = base_pred['prediction']
                    modified_pb = modified_pred['prediction']
                    change = modified_pb - base_pb
                    
                    # Risk assessment
                    risk_score = self._calculate_risk_score(modified_pb, modified_pred['confidence_interval'])
                    
                    # Benefit assessment
                    benefit_score = self._calculate_benefit_score(modified_pb, base_pb)
                    
                    # Confidence assessment
                    confidence = modified_pred['model_performance']['r2_score']
                    
                    horizon_analysis[horizon_key] = {
                        'base_prediction': base_pb,
                        'modified_prediction': modified_pb,
                        'change': change,
                        'risk_score': risk_score,
                        'benefit_score': benefit_score,
                        'confidence': confidence,
                        'in_target_range': self._is_in_target_range(modified_pb),
                        'risk_level': self._get_risk_level(risk_score),
                        'recommendation': self._get_horizon_recommendation(change, risk_score, benefit_score)
                    }
                    
                    # Weight by horizon (shorter horizons more important)
                    horizon_weight = 1.0 / horizon
                    overall_risk_score += risk_score * horizon_weight
                    overall_benefit_score += benefit_score * horizon_weight
            
            # Calculate overall metrics
            avg_risk = overall_risk_score / len(self.analysis_horizons)
            avg_benefit = overall_benefit_score / len(self.analysis_horizons)
            
            # Generate overall recommendation
            overall_recommendation = self._get_overall_recommendation(
                avg_risk, avg_benefit, parameter_changes
            )
            
            return {
                'scenario_name': scenario_name,
                'parameter_changes': parameter_changes,
                'horizon_analysis': horizon_analysis,
                'overall_risk_score': avg_risk,
                'overall_benefit_score': avg_benefit,
                'overall_recommendation': overall_recommendation,
                'risk_level': self._get_risk_level(avg_risk),
                'success_probability': 1.0 - avg_risk,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Scenario analysis failed: {e}")
            return {
                'scenario_name': scenario_name,
                'error': str(e),
                'success': False
            }
    
    def compare_scenarios(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple scenarios and rank them.
        
        Args:
            scenarios: List of scenario analysis results
            
        Returns:
            Dictionary with comparison results
        """
        try:
            logger.info(f"Comparing {len(scenarios)} scenarios")
            
            # Filter out failed scenarios
            valid_scenarios = [s for s in scenarios if s.get('success', True) and 'error' not in s]
            
            if not valid_scenarios:
                return {
                    'error': 'No valid scenarios to compare',
                    'success': False
                }
            
            # Calculate composite scores for ranking
            for scenario in valid_scenarios:
                risk_score = scenario.get('overall_risk_score', 1.0)
                benefit_score = scenario.get('overall_benefit_score', 0.0)
                
                # Composite score: benefit - risk (higher is better)
                composite_score = benefit_score - risk_score
                scenario['composite_score'] = composite_score
            
            # Sort by composite score (descending)
            ranked_scenarios = sorted(valid_scenarios, key=lambda x: x['composite_score'], reverse=True)
            
            # Generate comparison summary
            comparison_summary = {
                'total_scenarios': len(scenarios),
                'valid_scenarios': len(valid_scenarios),
                'best_scenario': ranked_scenarios[0] if ranked_scenarios else None,
                'worst_scenario': ranked_scenarios[-1] if ranked_scenarios else None,
                'ranked_scenarios': ranked_scenarios,
                'recommendations': self._generate_comparison_recommendations(ranked_scenarios)
            }
            
            return comparison_summary
            
        except Exception as e:
            logger.error(f"Scenario comparison failed: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    def generate_what_if_scenarios(self, base_data: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generate common what-if scenarios for analysis.
        
        Args:
            base_data: Base process data
            
        Returns:
            List of scenario configurations
        """
        scenarios = []
        
        # KEX variations
        kex_variations = [-10, -5, +5, +10]
        for change in kex_variations:
            scenarios.append({
                'name': f"KEX {change:+d} L/min",
                'parameter_changes': {'Pb_Conditioner_KEX_Flowrate': change},
                'description': f"Change KEX flow rate by {change:+d} L/min"
            })
        
        # SIPX variations
        sipx_variations = [-5, -2, +2, +5]
        for change in sipx_variations:
            scenarios.append({
                'name': f"SIPX {change:+d} L/min",
                'parameter_changes': {'Pb_Rougher1_SIPX_Flowrate': change},
                'description': f"Change SIPX flow rate by {change:+d} L/min"
            })
        
        # Combined scenarios
        combined_scenarios = [
            {'KEX': 5, 'SIPX': 2},
            {'KEX': -5, 'SIPX': -2},
            {'KEX': 10, 'SIPX': 5},
            {'KEX': -10, 'SIPX': -5}
        ]
        
        for i, changes in enumerate(combined_scenarios):
            scenarios.append({
                'name': f"Combined Scenario {i+1}",
                'parameter_changes': {
                    'Pb_Conditioner_KEX_Flowrate': changes['KEX'],
                    'Pb_Rougher1_SIPX_Flowrate': changes['SIPX']
                },
                'description': f"KEX {changes['KEX']:+d}, SIPX {changes['SIPX']:+d} L/min"
            })
        
        return scenarios
    
    def assess_risk_for_changes(self, 
                               base_data: Dict[str, float],
                               parameter_changes: Dict[str, float]) -> Dict[str, Any]:
        """
        Assess risk for specific parameter changes.
        
        Args:
            base_data: Base process data
            parameter_changes: Parameter changes to assess
            
        Returns:
            Dictionary with risk assessment results
        """
        try:
            # Analyze the scenario
            scenario_result = self.analyze_scenario(base_data, parameter_changes, "Risk Assessment")
            
            if not scenario_result.get('success', True):
                return scenario_result
            
            # Extract risk information
            risk_assessment = {
                'overall_risk_score': scenario_result['overall_risk_score'],
                'risk_level': scenario_result['risk_level'],
                'success_probability': scenario_result['success_probability'],
                'recommendation': scenario_result['overall_recommendation'],
                'horizon_risks': {}
            }
            
            # Analyze risks for each horizon
            for horizon_key, analysis in scenario_result['horizon_analysis'].items():
                risk_assessment['horizon_risks'][horizon_key] = {
                    'risk_score': analysis['risk_score'],
                    'risk_level': analysis['risk_level'],
                    'prediction': analysis['modified_prediction'],
                    'confidence': analysis['confidence'],
                    'in_target_range': analysis['in_target_range']
                }
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    def _calculate_risk_score(self, prediction: float, confidence_interval: Dict[str, float]) -> float:
        """Calculate risk score based on prediction and confidence interval."""
        try:
            # Base risk: distance from target range
            target_center = (self.target_ranges['optimal_min'] + self.target_ranges['optimal_max']) / 2
            distance_from_target = abs(prediction - target_center)
            max_distance = 5.0  # Maximum expected distance
            base_risk = min(1.0, distance_from_target / max_distance)
            
            # Uncertainty risk: wider confidence interval = higher risk
            ci_width = confidence_interval['upper'] - confidence_interval['lower']
            uncertainty_risk = min(1.0, ci_width / 10.0)  # Normalize to 0-1
            
            # Combined risk score
            risk_score = 0.7 * base_risk + 0.3 * uncertainty_risk
            
            return min(1.0, max(0.0, risk_score))
            
        except Exception as e:
            logger.warning(f"Risk score calculation failed: {e}")
            return 0.5  # Default medium risk
    
    def _calculate_benefit_score(self, modified_prediction: float, base_prediction: float) -> float:
        """Calculate benefit score based on improvement over base prediction."""
        try:
            # Check if modified prediction is better than base
            target_center = (self.target_ranges['optimal_min'] + self.target_ranges['optimal_max']) / 2
            
            base_distance = abs(base_prediction - target_center)
            modified_distance = abs(modified_prediction - target_center)
            
            if modified_distance < base_distance:
                # Improvement: benefit based on how much closer to target
                improvement = base_distance - modified_distance
                benefit_score = min(1.0, improvement / 5.0)  # Normalize to 0-1
            else:
                # No improvement or worse
                benefit_score = 0.0
            
            return benefit_score
            
        except Exception as e:
            logger.warning(f"Benefit score calculation failed: {e}")
            return 0.0
    
    def _is_in_target_range(self, prediction: float) -> bool:
        """Check if prediction is in target range."""
        return (self.target_ranges['optimal_min'] <= prediction <= self.target_ranges['optimal_max'])
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level based on risk score."""
        if risk_score >= self.risk_thresholds['high_risk']:
            return 'high'
        elif risk_score >= self.risk_thresholds['medium_risk']:
            return 'medium'
        elif risk_score >= self.risk_thresholds['low_risk']:
            return 'low'
        else:
            return 'minimal'
    
    def _get_horizon_recommendation(self, change: float, risk_score: float, benefit_score: float) -> str:
        """Get recommendation for a specific horizon."""
        if benefit_score > 0.5 and risk_score < 0.2:
            return "Strongly recommended"
        elif benefit_score > 0.3 and risk_score < 0.3:
            return "Recommended"
        elif risk_score > 0.5:
            return "Not recommended - high risk"
        elif benefit_score < 0.1:
            return "No significant benefit"
        else:
            return "Consider with caution"
    
    def _get_overall_recommendation(self, avg_risk: float, avg_benefit: float, changes: Dict[str, float]) -> str:
        """Get overall recommendation for the scenario."""
        if avg_benefit > 0.5 and avg_risk < 0.2:
            return f"Strongly recommended: High benefit ({avg_benefit:.1%}) with low risk ({avg_risk:.1%})"
        elif avg_benefit > 0.3 and avg_risk < 0.3:
            return f"Recommended: Good benefit ({avg_benefit:.1%}) with acceptable risk ({avg_risk:.1%})"
        elif avg_risk > 0.5:
            return f"Not recommended: High risk ({avg_risk:.1%}) outweighs benefits ({avg_benefit:.1%})"
        elif avg_benefit < 0.1:
            return f"No significant benefit ({avg_benefit:.1%}) - consider alternatives"
        else:
            return f"Consider with caution: Moderate benefit ({avg_benefit:.1%}) and risk ({avg_risk:.1%})"
    
    def _generate_comparison_recommendations(self, ranked_scenarios: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on scenario comparison."""
        recommendations = []
        
        if not ranked_scenarios:
            return ["No scenarios to compare"]
        
        best_scenario = ranked_scenarios[0]
        worst_scenario = ranked_scenarios[-1]
        
        recommendations.append(f"🏆 Best scenario: {best_scenario['scenario_name']} (Score: {best_scenario['composite_score']:.3f})")
        recommendations.append(f"⚠️ Worst scenario: {worst_scenario['scenario_name']} (Score: {worst_scenario['composite_score']:.3f})")
        
        # Analyze top scenarios
        top_scenarios = ranked_scenarios[:3]
        if len(top_scenarios) > 1:
            recommendations.append("📊 Top scenarios:")
            for i, scenario in enumerate(top_scenarios, 1):
                recommendations.append(f"  {i}. {scenario['scenario_name']} - Risk: {scenario['overall_risk_score']:.1%}, Benefit: {scenario['overall_benefit_score']:.1%}")
        
        # General recommendations
        if best_scenario['overall_risk_score'] < 0.2:
            recommendations.append("✅ Low-risk scenario available - safe to implement")
        elif best_scenario['overall_risk_score'] > 0.5:
            recommendations.append("⚠️ All scenarios have significant risk - consider manual intervention")
        
        return recommendations
