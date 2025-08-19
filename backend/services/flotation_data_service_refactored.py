"""
Refactored FastAPI WebSocket Server for Real-time Flotation Data
===============================================================

This server provides real-time data updates to the React frontend
via WebSocket connections, using SOLID principles.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import time
from datetime import datetime
import logging
import os
import sys
from typing import Dict, Any

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from service_orchestrator import FlotationServiceOrchestrator

# Set up comprehensive logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'flotation_data_service_refactored.log')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Log service startup
logger.info("Starting Refactored Froth Flotation Data Service")
logger.info(f"Log file: {log_file}")
logger.info(f"Service: FastAPI WebSocket Server (SOLID Architecture)")
logger.info(f"Port: 8000")

# Create FastAPI app
app = FastAPI(
    title="Froth Flotation Digital Twin API",
    description="Real-time flotation data service with ML predictions",
    version="2.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service orchestrator
orchestrator = FlotationServiceOrchestrator(logger)

# Background task for data generation
data_generation_task = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global data_generation_task
    logger.info("Starting background data generation task")
    data_generation_task = asyncio.create_task(
        orchestrator.run_data_generation_loop(interval_seconds=5)
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global data_generation_task
    if data_generation_task:
        data_generation_task.cancel()
        try:
            await data_generation_task
        except asyncio.CancelledError:
            pass
    logger.info("Service shutdown complete")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Froth Flotation Digital Twin API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        health_status = orchestrator.validate_system_health()
        return {
            "status": "healthy",
            "service": "flotation_data_service",
            "timestamp": datetime.now().isoformat(),
            "health": health_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/status")
async def get_status():
    """Get system status"""
    try:
        status = await orchestrator.get_system_status()
        return status
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")

@app.get("/model-info")
async def get_model_info():
    """Get ML model information"""
    try:
        model_info = orchestrator.ml_model.get_model_info()
        return {
            "model_info": model_info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Model info retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Model info retrieval failed")

@app.get("/api/current-data")
async def get_current_data():
    """Get current flotation data (frontend endpoint)"""
    try:
        data_point = await orchestrator.generate_and_process_data()
        return data_point
    except Exception as e:
        logger.error(f"Current data retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Current data retrieval failed")

@app.get("/api/optimal-ranges")
async def get_optimal_ranges():
    """Get optimal parameter ranges (frontend endpoint)"""
    try:
        ranges = orchestrator.data_generator.get_parameter_ranges()
        return {
            "parameter_ranges": ranges,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Optimal ranges retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Optimal ranges retrieval failed")

@app.get("/api/database/sensor-data")
async def get_sensor_data(limit: int = 100):
    """Get historical sensor data (frontend endpoint)"""
    try:
        # Generate multiple data points for historical data
        historical_data = []
        for _ in range(min(limit, 1000)):  # Limit to 1000 points max
            data_point = await orchestrator.generate_and_process_data()
            historical_data.append(data_point)
        
        return {
            "data": historical_data,
            "count": len(historical_data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Historical data retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Historical data retrieval failed")

@app.get("/generate-data")
async def generate_single_data_point():
    """Generate a single data point"""
    try:
        data_point = await orchestrator.generate_and_process_data()
        return {
            "data_point": data_point,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Data generation failed: {e}")
        raise HTTPException(status_code=500, detail="Data generation failed")

@app.get("/parameter-ranges")
async def get_parameter_ranges():
    """Get valid parameter ranges"""
    try:
        ranges = orchestrator.data_generator.get_parameter_ranges()
        return {
            "parameter_ranges": ranges,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Parameter ranges retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Parameter ranges retrieval failed")

@app.post("/validate-parameters")
async def validate_parameters(parameters: Dict[str, float]):
    """Validate if parameters are within acceptable ranges"""
    try:
        is_valid = orchestrator.data_generator.validate_parameters(parameters)
        return {
            "is_valid": is_valid,
            "parameters": parameters,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Parameter validation failed: {e}")
        raise HTTPException(status_code=500, detail="Parameter validation failed")

@app.post("/api/control-settings")
async def update_control_settings(controls: Dict[str, float]):
    """Update control settings for the flotation process"""
    try:
        # Validate the control parameters
        is_valid = orchestrator.data_generator.validate_parameters(controls)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid control parameters")
        
        # Update the control settings in the orchestrator
        await orchestrator.update_control_settings(controls)
        
        return {
            "success": True,
            "message": "Control settings updated successfully",
            "controls": controls,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Control settings update failed: {e}")
        raise HTTPException(status_code=500, detail="Control settings update failed")

@app.get("/api/connections")
async def get_connections():
    """Get current connection status and statistics"""
    try:
        active_connections = len(orchestrator.websocket_manager.active_connections)
        total_connections = orchestrator.websocket_manager.total_connections
        
        return {
            "active_connections": active_connections,
            "total_connections": total_connections,
            "status": "operational" if active_connections > 0 else "idle",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Connections status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Connections status retrieval failed")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data"""
    try:
        # Connect to WebSocket manager
        await orchestrator.websocket_manager.connect(websocket)
        
        # Send initial data point
        data_point = await orchestrator.generate_and_process_data()
        await orchestrator.websocket_manager.broadcast_data_point(data_point)
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }))
                elif message.get("type") == "request_data":
                    data_point = await orchestrator.generate_and_process_data()
                    await orchestrator.websocket_manager.broadcast_data_point(data_point)
                elif message.get("type") == "request_status":
                    status = await orchestrator.get_system_status()
                    await websocket.send_text(json.dumps({
                        "type": "status",
                        "data": status,
                        "timestamp": datetime.now().isoformat()
                    }))
                else:
                    logger.warning(f"Unknown message type: {message.get('type')}")
                    
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected")
                break
            except json.JSONDecodeError:
                logger.warning("Invalid JSON received from WebSocket client")
                continue
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected during connection")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Ensure cleanup
        await orchestrator.websocket_manager.disconnect(websocket)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "flotation_data_service_refactored:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
