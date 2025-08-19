"""
Backend Service Interfaces
=========================

This module defines interfaces following SOLID principles for the froth flotation
digital twin backend services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio

# ============================================================================
# DATA GENERATION INTERFACES
# ============================================================================

class IDataGenerator(ABC):
    """Interface for data generation services"""
    
    @abstractmethod
    def generate_data_point(self) -> Dict[str, Any]:
        """Generate a single data point"""
        pass
    
    @abstractmethod
    def get_parameter_ranges(self) -> Dict[str, Tuple[float, float]]:
        """Get the valid ranges for all parameters"""
        pass
    
    @abstractmethod
    def validate_parameters(self, params: Dict[str, float]) -> bool:
        """Validate if parameters are within acceptable ranges"""
        pass

class IHistoricalDataManager(ABC):
    """Interface for managing historical data"""
    
    @abstractmethod
    def add_data_point(self, data_point: Dict[str, Any]) -> None:
        """Add a new data point to historical data"""
        pass
    
    @abstractmethod
    def get_recent_data(self, count: int) -> List[Dict[str, Any]]:
        """Get the most recent data points"""
        pass
    
    @abstractmethod
    def get_lag_features(self, current_data: Dict[str, float]) -> Dict[str, float]:
        """Calculate lag features from historical data"""
        pass

# ============================================================================
# ML MODEL INTERFACES
# ============================================================================

class IMLModel(ABC):
    """Interface for ML model operations"""
    
    @abstractmethod
    def predict(self, features: Dict[str, float]) -> float:
        """Make a prediction using the model"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        pass
    
    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if the model is loaded"""
        pass

class IFeatureProcessor(ABC):
    """Interface for feature processing"""
    
    @abstractmethod
    def prepare_features(self, raw_data: Dict[str, float]) -> Dict[str, float]:
        """Prepare features for model prediction"""
        pass
    
    @abstractmethod
    def get_feature_names(self) -> List[str]:
        """Get the list of feature names"""
        pass
    
    @abstractmethod
    def validate_features(self, features: Dict[str, float]) -> bool:
        """Validate if all required features are present"""
        pass

class IProcessStatusAnalyzer(ABC):
    """Interface for process status analysis"""
    
    @abstractmethod
    def analyze_status(self, predictions: Dict[str, float]) -> str:
        """Analyze process status based on predictions"""
        pass
    
    @abstractmethod
    def get_target_ranges(self) -> Dict[str, Tuple[float, float]]:
        """Get target ranges for status analysis"""
        pass
    
    @abstractmethod
    def get_recommendations(self, status: str, predictions: Dict[str, float]) -> List[str]:
        """Get recommendations based on status and predictions"""
        pass

# ============================================================================
# DATABASE INTERFACES
# ============================================================================

class IDatabaseManager(ABC):
    """Interface for database operations"""
    
    @abstractmethod
    def save_data_point(self, data_point: Dict[str, Any]) -> bool:
        """Save a data point to the database"""
        pass
    
    @abstractmethod
    def get_recent_data(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent data from the database"""
        pass
    
    @abstractmethod
    def get_data_by_timerange(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get data within a time range"""
        pass

# ============================================================================
# WEBSOCKET INTERFACES
# ============================================================================

class IWebSocketManager(ABC):
    """Interface for WebSocket connection management"""
    
    @abstractmethod
    async def connect(self, websocket) -> None:
        """Connect a new WebSocket client"""
        pass
    
    @abstractmethod
    async def disconnect(self, websocket) -> None:
        """Disconnect a WebSocket client"""
        pass
    
    @abstractmethod
    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connected clients"""
        pass
    
    @abstractmethod
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        pass

# ============================================================================
# LOGGING INTERFACES
# ============================================================================

class ILogger(ABC):
    """Interface for logging operations"""
    
    @abstractmethod
    def info(self, message: str) -> None:
        """Log info message"""
        pass
    
    @abstractmethod
    def warning(self, message: str) -> None:
        """Log warning message"""
        pass
    
    @abstractmethod
    def error(self, message: str) -> None:
        """Log error message"""
        pass
    
    @abstractmethod
    def debug(self, message: str) -> None:
        """Log debug message"""
        pass

# ============================================================================
# CONFIGURATION INTERFACES
# ============================================================================

class IConfigurationManager(ABC):
    """Interface for configuration management"""
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        pass
    
    @abstractmethod
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value"""
        pass
    
    @abstractmethod
    def load_config(self) -> None:
        """Load configuration from file"""
        pass
    
    @abstractmethod
    def save_config(self) -> None:
        """Save configuration to file"""
        pass

# ============================================================================
# SERVICE FACTORY INTERFACES
# ============================================================================

class IServiceFactory(ABC):
    """Interface for service factory"""
    
    @abstractmethod
    def create_data_generator(self) -> IDataGenerator:
        """Create a data generator instance"""
        pass
    
    @abstractmethod
    def create_ml_model(self) -> IMLModel:
        """Create an ML model instance"""
        pass
    
    @abstractmethod
    def create_websocket_manager(self) -> IWebSocketManager:
        """Create a WebSocket manager instance"""
        pass
    
    @abstractmethod
    def create_database_manager(self) -> IDatabaseManager:
        """Create a database manager instance"""
        pass
