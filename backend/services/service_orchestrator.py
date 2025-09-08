"""
Service Orchestrator
===================

This module orchestrates all the backend services following SOLID principles.
"""

import asyncio
import logging
import time
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
        
        # Initialize lightweight services immediately
        self.data_generator: IDataGenerator = FlotationDataGenerator(logger)
        self.historical_manager: IHistoricalDataManager = HistoricalDataManager(logger=logger)
        self.status_analyzer: IProcessStatusAnalyzer = ProcessStatusAnalyzer(logger)
        self.websocket_manager: IWebSocketManager = WebSocketConnectionManager(logger)
        self.recovery_calculator = RecoveryCalculator()
        
        # Initialize heavy services lazily
        self.ml_model: Optional[IMLModel] = None
        self._ml_model_initialized = False
        self.optimizer = None
        self._optimizer_initialized = False
        
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
    
    def _initialize_ml_model(self):
        """Lazy initialization of ML model service to improve startup performance"""
        if not self._ml_model_initialized:
            try:
                self.logger.info("Initializing ML model service...")
                self.ml_model = MLModelService()
                self._ml_model_initialized = True
                self.logger.info("ML model service initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize ML model service: {e}")
                raise
    
    def _initialize_optimizer(self):
        """Lazy initialization of optimizer service to improve startup performance"""
        if not self._optimizer_initialized:
            try:
                self.logger.info("Initializing optimizer service...")
                from services.optimization_service import FlotationOptimizer
                self.optimizer = FlotationOptimizer()
                self._optimizer_initialized = True
                self.logger.info("Optimizer service initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize optimizer service: {e}")
                raise
        
        self.logger.info("Flotation Service Orchestrator initialized with database, RES table timing, and optimizer")
    
    async def generate_and_process_data(self, use_cache: bool = True) -> Dict[str, Any]:
        """Generate data point and process it through the ML pipeline"""
        try:
            # Check cache first if requested
            if use_cache and hasattr(self, 'last_cached_data') and self.last_cached_data is not None:
                current_time = time.time()
                if (hasattr(self, 'last_cache_time') and 
                    self.last_cache_time is not None and 
                    current_time - self.last_cache_time < 4):  # 4 second cache
                    return self.last_cached_data
            # Generate new data point
            raw_data = self.data_generator.generate_data_point()
            
            # Add to historical data
            self.historical_manager.add_data_point(raw_data)
            
            # Get lag features
            lag_features = self.historical_manager.get_lag_features(raw_data)
            
            # Combine raw data with lag features
            combined_data = {**raw_data, **lag_features}
            
            # Make ML prediction using the future prediction service
            try:
                # Initialize ML model if needed
                self._initialize_ml_model()
                
                # Get future predictions (5min, 15min, 30min, 60min)
                future_predictions = self.ml_model.predict_future_pb_concentrate(combined_data, [5, 15, 30, 60])
                
                # Use 5-minute prediction as current prediction
                predicted_pb_concentrate = future_predictions['future_predictions']['5min']['prediction']
                
                # Store future predictions for the dashboard
                self.current_future_predictions = future_predictions
                
                # Calculate predicted recovery rate (returns percentage)
                predicted_recovery_rate_pct = self.ml_model.calculate_recovery_rate(raw_data, predicted_pb_concentrate)
                
            except Exception as e:
                # Fallback to a reasonable default if future prediction fails
                self.logger.warning(f"Future prediction failed, using fallback: {e}")
                predicted_pb_concentrate = 20.0  # Default reasonable value
                predicted_recovery_rate_pct = 85.0  # Default reasonable recovery rate
                self.current_future_predictions = None
            
            # Generate actual Pb concentrate (with realistic variation from prediction)
            import numpy as np
            # Actual values should be close to predicted but with realistic process variation
            actual_pb_concentrate = predicted_pb_concentrate + np.random.normal(0, 1.5)  # ±1.5% variation
            
            # Generate actual recovery rate (with realistic variation)
            actual_recovery_rate_pct = predicted_recovery_rate_pct + np.random.normal(0, 2.0)  # ±2% variation
            
            # Apply the same bounds logic as predicted values based on reagent levels
            kex_value = raw_data.get('Pb_Conditioner_KEX_Flowrate', 60.0)
            sipx_value = raw_data.get('Pb_Rougher1_SIPX_Flowrate', 30.0)
            
            # Use the same percentile-based logic as the data generator
            # Industry realistic ranges: KEX 20-100 L/min, SIPX 10-50 L/min
            # Calculate percentiles from these realistic ranges
            
            # KEX percentiles from realistic range (20-100)
            kex_q25 = 20 + (100-20) * 0.25  # 40 L/min (low)
            kex_q75 = 20 + (100-20) * 0.75  # 80 L/min (optimal max)
            kex_q95 = 20 + (100-20) * 0.95  # 96 L/min (excessive)
            
            # SIPX percentiles from realistic range (10-50)
            sipx_q25 = 10 + (50-10) * 0.25   # 20 L/min (low)
            sipx_q75 = 10 + (50-10) * 0.75   # 40 L/min (optimal max)
            sipx_q95 = 10 + (50-10) * 0.95   # 48 L/min (excessive)
            
            # Clamp actual Pb concentrate based on reagent levels (same logic as predicted)
            if kex_value == 0 and sipx_value == 0:
                actual_pb_concentrate = max(0.5, min(2.5, actual_pb_concentrate))  # Feed grade range
            elif kex_value <= kex_q25 and sipx_value <= sipx_q25:
                actual_pb_concentrate = max(5.0, min(15.0, actual_pb_concentrate))  # Low reagent range
            elif kex_value >= kex_q95 or sipx_value >= sipx_q95:
                actual_pb_concentrate = max(30.0, min(40.0, actual_pb_concentrate))  # Excessive reagent range
            elif kex_value > kex_q75 or sipx_value > sipx_q75:
                actual_pb_concentrate = max(25.0, min(35.0, actual_pb_concentrate))  # High reagent range
            else:
                actual_pb_concentrate = max(15.0, min(25.0, actual_pb_concentrate))  # Normal range
            
            # Clamp actual recovery based on reagent levels (same logic as predicted)
            if kex_value == 0 and sipx_value == 0:
                actual_recovery_rate_pct = max(0.0, min(10.0, actual_recovery_rate_pct))  # Very low recovery
            elif kex_value <= kex_q25 and sipx_value <= sipx_q25:
                actual_recovery_rate_pct = max(20.0, min(50.0, actual_recovery_rate_pct))  # Low recovery
            elif kex_value >= kex_q95 or sipx_value >= sipx_q95:
                actual_recovery_rate_pct = max(90.0, min(98.0, actual_recovery_rate_pct))  # Excessive recovery (unstable)
            elif kex_value > kex_q75 or sipx_value > sipx_q75:
                actual_recovery_rate_pct = max(80.0, min(95.0, actual_recovery_rate_pct))  # High recovery
            else:
                actual_recovery_rate_pct = max(75.0, min(90.0, actual_recovery_rate_pct))  # Normal recovery
            
            # Analyze process status using predicted values
            predictions = {
                'pb_concentrate': predicted_pb_concentrate,
                'recovery_rate': predicted_recovery_rate_pct
            }
            
            status = self.status_analyzer.analyze_status(predictions, raw_data)
            
            # Track prediction accuracy (compare predicted vs actual from previous cycle)
            if hasattr(self, 'last_predictions') and self.last_predictions:
                # Initialize optimizer if needed
                self._initialize_optimizer()
                self.optimizer.track_prediction_accuracy(self.last_predictions, {
                    'pb_concentrate': actual_pb_concentrate,
                    'recovery_rate': actual_recovery_rate_pct
                })
            
            # Store current predictions for next cycle
            self.last_predictions = {
                'pb_concentrate': predicted_pb_concentrate,
                'recovery_rate': predicted_recovery_rate_pct
            }
            
            # Run optimization using the instance optimizer
            self._initialize_optimizer()
            optimization_result = self.optimizer.optimize_reagent_rates(raw_data)
            recommendations = self.optimizer.generate_recommendations(optimization_result)
            self.logger.debug(f"Generated {len(recommendations)} optimization-based recommendations")
            
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
                    self.logger.debug(f"Saved to RES1 - ID: {res1_id}")
                
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
                    self.logger.debug(f"Saved to RES2 - ID: {res2_id}")
                
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
                    
                    # Get optimization data for RES3 using the instance optimizer
                    self._initialize_optimizer()
                    optimization_result = self.optimizer.optimize_reagent_rates(raw_data)
                    
                    if optimization_result.get('success', False):
                        optimal_settings = optimization_result['optimal_settings']
                        recommended_kex = optimal_settings.get('KEX', current_kex)
                        recommended_sipx = optimal_settings.get('SIPX', current_sipx)
                        optimization_confidence = self.optimizer.get_prediction_accuracy()
                        external_factors_changed = self.optimizer.detect_external_changes(raw_data)
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
                    self.logger.debug(f"Saved to RES3 - ID: {res3_id}")
                
                # Log save status
                saved_tables = []
                if res1_id: saved_tables.append(f"RES1({res1_id})")
                if res2_id: saved_tables.append(f"RES2({res2_id})")
                if res3_id: saved_tables.append(f"RES3({res3_id})")
                
                if saved_tables:
                    self.logger.debug(f"Data saved to: {', '.join(saved_tables)}")
                else:
                    self.logger.debug("No RES tables saved this cycle (timing intervals not met)")
                
            except Exception as e:
                self.logger.error(f"Failed to save data to RES tables: {e}")
            
            self.logger.debug(f"Generated data point - Status: {status}, Pb: {predicted_pb_concentrate:.2f}, Recovery: {predicted_recovery_rate_pct:.1f}%")
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error in data generation and processing: {e}")
            return self._create_error_data_point(str(e))
    
    def _create_error_data_point(self, error_message: str) -> Dict[str, Any]:
        """Create an error data point when processing fails"""
        # Initialize ML model if needed
        self._initialize_ml_model()
        
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
        # Initialize ML model if needed
        self._initialize_ml_model()
        
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
            self.logger.info(f"Attempting to update control settings: {controls}")
            
            if hasattr(self.data_generator, 'update_control_settings'):
                self.logger.info("Calling data_generator.update_control_settings")
                self.data_generator.update_control_settings(controls)
                self.logger.info("data_generator.update_control_settings completed")
            else:
                self.logger.error("data_generator does not have update_control_settings method")
            
            # Clear the data cache to force regeneration with new controls
            self.last_cached_data = None
            self.last_cache_time = None
            
            # Log the control settings update
            self.logger.info(f"Control settings updated: {controls}")
            
        except Exception as e:
            self.logger.error(f"Error updating control settings: {e}")
            raise
    
    def validate_system_health(self) -> Dict[str, Any]:
        """Validate the health of all system components"""
        # Initialize ML model if needed
        self._initialize_ml_model()
        
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
            test_prediction = self.ml_model.predict_future_pb_concentrate({'Feed_Pb': 2.5, 'Feed_Zn': 10.0, 'Pb_Conditioner_KEX_Flowrate': 60.0, 'Pb_Rougher1_SIPX_Flowrate': 30.0, 'Pb_Rougher1_AirFlow': 10.0, 'Pb_Rougher1_Level': 40.0}, [5])
            if test_prediction and 'future_predictions' in test_prediction:
                health_status['components']['ml_model_service'] = 'healthy'
            else:
                health_status['components']['ml_model_service'] = 'unhealthy'
                health_status['overall_status'] = 'degraded'
        except Exception as e:
            health_status['components']['ml_model_service'] = f'unhealthy: {str(e)}'
            health_status['overall_status'] = 'degraded'
        
        return health_status
    
    async def run_data_generation_loop(self, interval_seconds: int = 4) -> None:  # Optimized for 4-second updates for better stability
        """Run continuous data generation loop with optimized resource usage"""
        self.logger.info(f"Starting data generation loop with {interval_seconds}s interval")
        
        # Cache the last data point to avoid regenerating on every request
        self.last_cached_data = None
        self.last_cache_time = None
        cache_duration = 3  # Cache data for 3 seconds to reduce processing load
        
        while True:
            try:
                current_time = time.time()
                
                # Only generate new data if cache is expired or doesn't exist
                if (self.last_cached_data is None or 
                    self.last_cache_time is None or 
                    current_time - self.last_cache_time > cache_duration):
                    
                    # Generate and process data
                    data_point = await self.generate_and_process_data()
                    
                    # Cache the data
                    self.last_cached_data = data_point
                    self.last_cache_time = current_time
                    
                    # Broadcast to WebSocket clients
                    await self.broadcast_data(data_point)
                else:
                    # Use cached data for WebSocket broadcast
                    await self.broadcast_data(self.last_cached_data)
                
                # Wait for next iteration
                await asyncio.sleep(interval_seconds)
                
            except asyncio.CancelledError:
                self.logger.info("Data generation loop cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in data generation loop: {e}")
                await asyncio.sleep(interval_seconds)  # Continue despite errors
