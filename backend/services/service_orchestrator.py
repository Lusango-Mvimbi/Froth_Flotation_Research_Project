"""
Service Orchestrator
===================

This module orchestrates all the backend services following SOLID principles.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from interfaces import (
    IDataGenerator, IMLModel, IFeatureProcessor, IProcessStatusAnalyzer,
    IWebSocketManager, IHistoricalDataManager
)
from data_generator import FlotationDataGenerator, HistoricalDataManager
from ml_model_implementation import (
    GradientBoostingModel, FeatureProcessor, ProcessStatusAnalyzer, RecoveryCalculator
)
from websocket_manager import WebSocketConnectionManager

class FlotationServiceOrchestrator:
    """Orchestrates all flotation services"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
        # Initialize all services
        self.data_generator: IDataGenerator = FlotationDataGenerator(logger)
        self.historical_manager: IHistoricalDataManager = HistoricalDataManager(logger=logger)
        self.ml_model: IMLModel = GradientBoostingModel(logger)
        self.feature_processor: IFeatureProcessor = FeatureProcessor(logger)
        self.status_analyzer: IProcessStatusAnalyzer = ProcessStatusAnalyzer(logger)
        self.websocket_manager: IWebSocketManager = WebSocketConnectionManager(logger)
        self.recovery_calculator = RecoveryCalculator()
        
        self.logger.warning("Flotation Service Orchestrator initialized")
    
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
            
            # Prepare features for ML model
            features = self.feature_processor.prepare_features(combined_data)
            
            # Make ML prediction
            pb_concentrate = self.ml_model.predict(features)
            
            # Calculate recovery rate
            recovery_rate = self.recovery_calculator.calculate_recovery_rate({
                **raw_data,
                'pb_concentrate': pb_concentrate
            })
            
            # Analyze process status
            predictions = {
                'pb_concentrate': pb_concentrate,
                'recovery_rate': recovery_rate
            }
            
            status = self.status_analyzer.analyze_status(predictions)
            recommendations = self.status_analyzer.get_recommendations(status, predictions)
            
            # Prepare final data point
            processed_data = {
                **raw_data,
                'pb_concentrate': pb_concentrate,
                'recovery_rate': recovery_rate,
                'process_status': status,
                'recommendations': recommendations,
                'model_info': self.ml_model.get_model_info()
            }
            
            self.logger.info(f"Generated data point - Status: {status}, Pb: {pb_concentrate:.2f}, Recovery: {recovery_rate:.1f}%")
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error in data generation and processing: {e}")
            return self._create_error_data_point(str(e))
    
    def _create_error_data_point(self, error_message: str) -> Dict[str, Any]:
        """Create an error data point when processing fails"""
        return {
            'timestamp': datetime.now().isoformat(),
            'pb_concentrate': None,
            'recovery_rate': None,
            'process_status': 'error',
            'recommendations': [f"System error: {error_message}"],
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
        
        # Check feature processor
        try:
            test_features = self.feature_processor.prepare_features({'pH': 11.0})
            if test_features:
                health_status['components']['feature_processor'] = 'healthy'
            else:
                health_status['components']['feature_processor'] = 'unhealthy'
                health_status['overall_status'] = 'degraded'
        except Exception as e:
            health_status['components']['feature_processor'] = f'unhealthy: {str(e)}'
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
