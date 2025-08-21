"""
Service Orchestrator
===================

This module orchestrates all the backend services following SOLID principles.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from services.interfaces import (
    IDataGenerator, IMLModel, IFeatureProcessor, IProcessStatusAnalyzer,
    IWebSocketManager, IHistoricalDataManager
)
from models.database_manager import FlotationDatabase
from services.data_generator import FlotationDataGenerator, HistoricalDataManager
from services.ml_model_implementation import (
    ProcessStatusAnalyzer, RecoveryCalculator
)
from services.ml_model_service import MLModelService
from services.websocket_manager import WebSocketConnectionManager

class FlotationServiceOrchestrator:
    """Orchestrates all flotation services"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
        # Initialize all services
        self.data_generator: IDataGenerator = FlotationDataGenerator(logger)
        self.historical_manager: IHistoricalDataManager = HistoricalDataManager(logger=logger)
        self.ml_model: IMLModel = MLModelService()
        self.status_analyzer: IProcessStatusAnalyzer = ProcessStatusAnalyzer(logger)
        self.websocket_manager: IWebSocketManager = WebSocketConnectionManager(logger)
        self.recovery_calculator = RecoveryCalculator()
        
        # Initialize database manager
        self.database = FlotationDatabase()
        
        # Initialize timing for RES table saves
        self.last_res1_save = datetime.now()
        self.last_res2_save = datetime.now()
        self.last_res3_save = datetime.now()
        
        # Save intervals in minutes
        self.res1_interval = 2  # 2 minutes
        self.res2_interval = 5  # 5 minutes
        self.res3_interval = 10  # 10 minutes
        
        self.logger.warning("Flotation Service Orchestrator initialized with database and RES table timing")
    
    async def generate_and_process_data(self) -> Dict[str, Any]:
        """Generate data point and process it through the ML pipeline"""
        try:
            # Generate new data point
            raw_data = self.data_generator.generate_data_point()
            
            # Add to historical data
            self.historical_manager.add_data_point(raw_data)
            
            # Get lag features
            lag_features = self.historical_manager.get_lag_features(raw_data)
            
            # Combine raw data with lag features
            combined_data = {**raw_data, **lag_features}
            
            # Make ML prediction using the new service
            predicted_pb_concentrate = self.ml_model.predict_pb_concentrate(combined_data)
            
            # Generate actual Pb concentrate (with realistic variation from prediction)
            import numpy as np
            # Actual values should be close to predicted but with realistic process variation
            actual_pb_concentrate = predicted_pb_concentrate + np.random.normal(0, 1.5)  # ±1.5% variation
            actual_pb_concentrate = max(10.0, min(40.0, actual_pb_concentrate))  # Realistic bounds
            
            # Calculate predicted recovery rate (returns percentage)
            predicted_recovery_rate_pct = self.ml_model.calculate_recovery_rate(raw_data, predicted_pb_concentrate)
            
            # Generate actual recovery rate (with realistic variation)
            actual_recovery_rate_pct = predicted_recovery_rate_pct + np.random.normal(0, 2.0)  # ±2% variation
            actual_recovery_rate_pct = max(75.0, min(95.0, actual_recovery_rate_pct))  # Realistic bounds
            
            # Analyze process status using predicted values
            predictions = {
                'pb_concentrate': predicted_pb_concentrate,
                'recovery_rate': predicted_recovery_rate_pct
            }
            
            status = self.status_analyzer.analyze_status(predictions)
            
            # Get optimization-based recommendations
            from services.optimization_service import FlotationOptimizer
            optimizer = FlotationOptimizer()
            
            # Track prediction accuracy (compare predicted vs actual from previous cycle)
            if hasattr(self, 'last_predictions') and self.last_predictions:
                optimizer.track_prediction_accuracy(self.last_predictions, {
                    'pb_concentrate': actual_pb_concentrate,
                    'recovery_rate': actual_recovery_rate_pct
                })
            
            # Store current predictions for next cycle
            self.last_predictions = {
                'pb_concentrate': predicted_pb_concentrate,
                'recovery_rate': predicted_recovery_rate_pct
            }
            
            # Run optimization
            optimization_result = optimizer.optimize_reagent_rates(raw_data)
            recommendations = optimizer.generate_recommendations(optimization_result)
            self.logger.info(f"Generated {len(recommendations)} optimization-based recommendations")
            
            # Prepare final data point with both predicted and actual values
            processed_data = {
                **raw_data,
                # Predicted values (from ML model)
                'Predicted_Pb_Concentrate': predicted_pb_concentrate,
                'Predicted_Pb_Recovery': predicted_recovery_rate_pct / 100.0,  # Convert to decimal
                # Actual values (simulated process measurements)
                'Actual_Pb_Concentrate': actual_pb_concentrate,
                'Actual_Pb_Recovery': actual_recovery_rate_pct / 100.0,  # Convert to decimal
                # Legacy fields for backward compatibility
                'Pb_Concentrate': predicted_pb_concentrate,  # Keep for existing frontend
                'Pb_Recovery': predicted_recovery_rate_pct / 100.0,  # Keep for existing frontend
                'Process_Status': status,
                'Recommendations': recommendations,
                'model_info': self.ml_model.get_model_info()
            }
            
            # Save data to RES tables with timing controls
            try:
                current_time = datetime.now()
                res1_id = None
                res2_id = None
                res3_id = None
                
                # Check if it's time to save to RES1 (every 2 minutes)
                if (current_time - self.last_res1_save).total_seconds() >= self.res1_interval * 60:
                    res1_id = self.database.save_to_res1(raw_data)
                    self.last_res1_save = current_time
                    self.logger.info(f"Saved to RES1 - ID: {res1_id}")
                
                # Check if it's time to save to RES2 (every 5 minutes)
                if (current_time - self.last_res2_save).total_seconds() >= self.res2_interval * 60:
                    res2_id = self.database.save_to_res2({
                        'Predicted_Pb_Concentrate': predicted_pb_concentrate,
                        'Actual_Pb_Concentrate': actual_pb_concentrate,
                        'Predicted_Pb_Recovery': predicted_recovery_rate_pct / 100.0,
                        'Actual_Pb_Recovery': actual_recovery_rate_pct / 100.0,
                        'Process_Status': status,
                        'model_confidence': 0.85
                    })
                    self.last_res2_save = current_time
                    self.logger.info(f"Saved to RES2 - ID: {res2_id}")
                
                # Check if it's time to save to RES3 (every 10 minutes)
                if (current_time - self.last_res3_save).total_seconds() >= self.res3_interval * 60:
                    # Get current control settings and optimization data for RES3
                    current_kex = raw_data.get('Pb_Conditioner_KEX_Flowrate', 45.0)
                    current_sipx = raw_data.get('Pb_Rougher1_SIPX_Flowrate', 25.0)
                    
                    # Extract optimization recommendations if available
                    recommended_kex = current_kex  # Default to current if no optimization
                    recommended_sipx = current_sipx
                    optimization_confidence = 0.8
                    external_factors_changed = False
                    
                    # Get optimization data for RES3
                    from services.optimization_service import FlotationOptimizer
                    optimizer = FlotationOptimizer()
                    optimization_result = optimizer.optimize_reagent_rates(raw_data)
                    
                    if optimization_result.get('success', False):
                        optimal_settings = optimization_result['optimal_settings']
                        recommended_kex = optimal_settings.get('KEX', current_kex)
                        recommended_sipx = optimal_settings.get('SIPX', current_sipx)
                        optimization_confidence = optimizer.get_prediction_accuracy()
                        external_factors_changed = optimizer.detect_external_changes(raw_data)
                    else:
                        # If optimization fails, use current settings
                        recommended_kex = current_kex
                        recommended_sipx = current_sipx
                        optimization_confidence = 0.5
                        external_factors_changed = False
                    
                    # Save to RES3 - Optimization recommendations and control settings
                    res3_id = self.database.save_to_res3({
                        'current_kex': current_kex,
                        'current_sipx': current_sipx,
                        'recommended_kex': recommended_kex,
                        'recommended_sipx': recommended_sipx,
                        'optimization_confidence': optimization_confidence,
                        'recommendations': recommendations,
                        'external_factors_changed': external_factors_changed
                    })
                    self.last_res3_save = current_time
                    self.logger.info(f"Saved to RES3 - ID: {res3_id}")
                
                # Log save status
                saved_tables = []
                if res1_id: saved_tables.append(f"RES1({res1_id})")
                if res2_id: saved_tables.append(f"RES2({res2_id})")
                if res3_id: saved_tables.append(f"RES3({res3_id})")
                
                if saved_tables:
                    self.logger.info(f"Data saved to: {', '.join(saved_tables)}")
                else:
                    self.logger.debug("No RES tables saved this cycle (timing intervals not met)")
                
            except Exception as e:
                self.logger.error(f"Failed to save data to RES tables: {e}")
            
            self.logger.info(f"Generated data point - Status: {status}, Pb: {predicted_pb_concentrate:.2f}, Recovery: {predicted_recovery_rate_pct:.1f}%")
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error in data generation and processing: {e}")
            return self._create_error_data_point(str(e))
    
    def _create_error_data_point(self, error_message: str) -> Dict[str, Any]:
        """Create an error data point when processing fails"""
        return {
            'timestamp': datetime.now().isoformat(),
            'Pb_Concentrate': None,
            'Pb_Recovery': None,
            'Process_Status': 'error',
            'Recommendations': [f"System error: {error_message}"],
            'model_info': self.ml_model.get_model_info(),
            'error': error_message
        }
    
    async def broadcast_data(self, data_point: Dict[str, Any]) -> None:
        """Broadcast data point to all connected WebSocket clients"""
        try:
            await self.websocket_manager.broadcast_data_point(data_point)
        except Exception as e:
            self.logger.error(f"Error broadcasting data: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'websocket_connections': self.websocket_manager.get_connection_count(),
            'model_status': self.ml_model.get_model_info(),
            'data_generator_status': 'running',
            'historical_data_count': len(self.historical_manager.historical_data)
        }
    
    async def update_control_settings(self, controls: Dict[str, float]) -> None:
        """Update control settings for the flotation process"""
        try:
            # Update the data generator with new control settings
            if hasattr(self.data_generator, 'update_control_settings'):
                self.data_generator.update_control_settings(controls)
            
            # Log the control settings update
            self.logger.info(f"Control settings updated: {controls}")
            
        except Exception as e:
            self.logger.error(f"Error updating control settings: {e}")
            raise
    
    def validate_system_health(self) -> Dict[str, Any]:
        """Validate the health of all system components"""
        health_status = {
            'overall_status': 'healthy',
            'components': {}
        }
        
        # Check ML model
        if self.ml_model.is_loaded():
            health_status['components']['ml_model'] = 'healthy'
        else:
            health_status['components']['ml_model'] = 'unhealthy'
            health_status['overall_status'] = 'degraded'
        
        # Check data generator
        try:
            test_data = self.data_generator.generate_data_point()
            if test_data:
                health_status['components']['data_generator'] = 'healthy'
            else:
                health_status['components']['data_generator'] = 'unhealthy'
                health_status['overall_status'] = 'degraded'
        except Exception as e:
            health_status['components']['data_generator'] = f'unhealthy: {str(e)}'
            health_status['overall_status'] = 'degraded'
        
        # Check ML model service
        try:
            test_prediction = self.ml_model.predict_pb_concentrate({'pH': 11.0})
            if test_prediction is not None:
                health_status['components']['ml_model_service'] = 'healthy'
            else:
                health_status['components']['ml_model_service'] = 'unhealthy'
                health_status['overall_status'] = 'degraded'
        except Exception as e:
            health_status['components']['ml_model_service'] = f'unhealthy: {str(e)}'
            health_status['overall_status'] = 'degraded'
        
        return health_status
    
    async def run_data_generation_loop(self, interval_seconds: int = 5) -> None:
        """Run continuous data generation loop"""
        self.logger.warning(f"Starting data generation loop with {interval_seconds}s interval")
        
        while True:
            try:
                # Generate and process data
                data_point = await self.generate_and_process_data()
                
                # Broadcast to WebSocket clients
                await self.broadcast_data(data_point)
                
                # Wait for next iteration
                await asyncio.sleep(interval_seconds)
                
            except asyncio.CancelledError:
                self.logger.warning("Data generation loop cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in data generation loop: {e}")
                await asyncio.sleep(interval_seconds)  # Continue despite errors
