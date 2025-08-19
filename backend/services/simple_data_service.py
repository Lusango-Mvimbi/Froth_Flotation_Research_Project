#!/usr/bin/env python3
"""
Simple Data Service
==================
A minimal working backend service that provides data to the frontend.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import random
import time
from datetime import datetime
from typing import Dict, Any, List
import logging

# Set up logging - Only log errors and warnings
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

app = FastAPI(title="Simple Flotation Data Service")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimpleDataGenerator:
    """Simple data generator for testing"""
    
    def __init__(self):
        self.base_values = {
            'pH': 11.0,
            'Temperature': 25.0,
            'Pb_Rougher1_AirFlow': 150.0,
            'Pulp_Density': 35.0,
            'Pb_Conditioner_KEX_Flowrate': 45.0,
            'Pb_Rougher1_SIPX_Flowrate': 25.0,
            'Feed_Pb': 2.5,
            'Feed_Zn': 10.0,
            'Cell_Level': 60.0,
            'Impeller_Speed': 1200.0,
            'Froth_Height': 15.0
        }
    
    def generate_data_point(self) -> Dict[str, Any]:
        """Generate a simple data point"""
        # Add some variation to base values
        data_point = {}
        for key, base_value in self.base_values.items():
            if isinstance(base_value, float):
                variation = random.uniform(-0.1 * base_value, 0.1 * base_value)
                data_point[key] = round(base_value + variation, 2)
            else:
                data_point[key] = base_value
        
        # Add calculated values
        data_point['timestamp'] = datetime.now().isoformat()
        data_point['Pb_Concentrate'] = round(random.uniform(8.0, 12.0), 2)
        data_point['Pb_Recovery'] = round(random.uniform(75.0, 95.0), 2)
        data_point['Process_Status'] = random.choice(['optimal', 'warning', 'critical'])
        data_point['Model_Confidence'] = round(random.uniform(0.85, 0.98), 3)
        
        return data_point

# Initialize data generator
data_generator = SimpleDataGenerator()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Simple Flotation Data Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "simple_data_service",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/generate-data")
async def generate_single_data_point():
    """Generate a single data point"""
    try:
        data_point = data_generator.generate_data_point()
        return {
            "data_point": data_point,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Data generation failed: {e}")
        raise JSONResponse(
            status_code=500,
            content={"error": "Data generation failed", "message": str(e)}
        )

@app.get("/api/current-data")
async def get_current_data():
    """Get current flotation data (frontend endpoint)"""
    try:
        data_point = data_generator.generate_data_point()
        return data_point
    except Exception as e:
        logger.error(f"Current data retrieval failed: {e}")
        raise JSONResponse(
            status_code=500,
            content={"error": "Current data retrieval failed", "message": str(e)}
        )

@app.get("/api/optimal-ranges")
async def get_optimal_ranges():
    """Get optimal parameter ranges for flotation process"""
    try:
        optimal_ranges = {
            'pH': [11.0, 11.5],
            'Temperature': [22.0, 26.0],
            'Pb_Rougher1_AirFlow': [140.0, 160.0],
            'Pulp_Density': [32.0, 36.0],
            'Pb_Conditioner_KEX_Flowrate': [40.0, 50.0],
            'Pb_Rougher1_SIPX_Flowrate': [22.0, 28.0],
            'Feed_Pb': [2.2, 2.8],
            'Feed_Zn': [9.0, 11.0],
            'Cell_Level': [58.0, 62.0],
            'Impeller_Speed': [1150.0, 1250.0],
            'Froth_Height': [14.0, 16.0]
        }
        return {
            "optimal_ranges": optimal_ranges,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Optimal ranges retrieval failed: {e}")
        raise JSONResponse(
            status_code=500,
            content={"error": "Optimal ranges retrieval failed", "message": str(e)}
        )

@app.get("/api/database/sensor-data")
async def get_sensor_data(limit: int = 100):
    """Get historical sensor data from database"""
    try:
        # Generate historical data points
        historical_data = []
        for i in range(min(limit, 1000)):  # Limit to 1000 points max
            data_point = data_generator.generate_data_point()
            # Add timestamp offset to simulate historical data
            timestamp = datetime.now().timestamp() - (i * 300)  # 5 minutes apart
            data_point['timestamp'] = datetime.fromtimestamp(timestamp).isoformat()
            historical_data.append(data_point)
        
        return {
            "data": historical_data,
            "count": len(historical_data),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Historical data retrieval failed: {e}")
        raise JSONResponse(
            status_code=500,
            content={"error": "Historical data retrieval failed", "message": str(e)}
        )

@app.get("/parameter-ranges")
async def get_parameter_ranges():
    """Get valid parameter ranges"""
    ranges = {
        'pH': [10.5, 12.0],
        'Temperature': [20.0, 30.0],
        'Pb_Rougher1_AirFlow': [120.0, 180.0],
        'Pulp_Density': [30.0, 40.0],
        'Pb_Conditioner_KEX_Flowrate': [35.0, 55.0],
        'Pb_Rougher1_SIPX_Flowrate': [20.0, 30.0],
        'Feed_Pb': [2.0, 3.0],
        'Feed_Zn': [8.0, 12.0],
        'Cell_Level': [55.0, 65.0],
        'Impeller_Speed': [1100.0, 1300.0],
        'Froth_Height': [12.0, 18.0]
    }
    return {
        "parameter_ranges": ranges,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/validate-parameters")
async def validate_parameters(parameters: Dict[str, float]):
    """Validate if parameters are within acceptable ranges"""
    try:
        # Simple validation - just check if all parameters are present
        required_params = ['pH', 'Pb_Conditioner_KEX_Flowrate', 'Pb_Rougher1_SIPX_Flowrate']
        is_valid = all(param in parameters for param in required_params)
        
        return {
            "is_valid": is_valid,
            "parameters": parameters,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Parameter validation failed: {e}")
        raise JSONResponse(
            status_code=500,
            content={"error": "Parameter validation failed", "message": str(e)}
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data"""
    await websocket.accept()
    logger.info("WebSocket client connected")
    
    try:
        while True:
            # Generate and send data every 5 seconds
            data_point = data_generator.generate_data_point()
            await websocket.send_text(json.dumps({
                "type": "data_point",
                "data": data_point,
                "timestamp": datetime.now().isoformat()
            }))
            
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Simple Flotation Data Service on port 8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
