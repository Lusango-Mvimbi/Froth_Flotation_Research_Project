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

from services.service_orchestrator import FlotationServiceOrchestrator

# Set up comprehensive logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'flotation_data_service_refactored.log')

# Configure logging - Only log errors and warnings
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Log service startup (WARNING level for important startup info)
logger.warning("Starting Refactored Froth Flotation Data Service")
logger.warning(f"Log file: {log_file}")
logger.warning(f"Service: FastAPI WebSocket Server (SOLID Architecture)")
logger.warning(f"Port: 8000")

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
    logger.warning("Starting background data generation task")
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
    logger.warning("Service shutdown complete")

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

@app.get("/api/target-ranges")
async def get_target_ranges():
    """Get target ranges for prediction cards (frontend endpoint)"""
    try:
        target_ranges = orchestrator.data_generator.get_target_ranges()
        return {
            "target_ranges": target_ranges,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Target ranges retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Target ranges retrieval failed")

@app.get("/api/optimization")
async def get_optimization_results():
    """Get optimization results and recommendations (frontend endpoint)"""
    try:
        import asyncio
        
        # Get current data for optimization
        current_data = await orchestrator.generate_and_process_data()
        
        # Run optimization with timeout (30 seconds)
        loop = asyncio.get_event_loop()
        optimization_result = await loop.run_in_executor(
            None, 
            lambda: orchestrator.ml_model.optimize_reagent_rates(current_data)
        )
        
        return {
            "optimization": optimization_result,
            "timestamp": datetime.now().isoformat()
        }
    except asyncio.TimeoutError:
        logger.error("Optimization timed out after 30 seconds")
        raise HTTPException(status_code=408, detail="Optimization timed out")
    except Exception as e:
        logger.error(f"Optimization results retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Optimization results retrieval failed")

@app.get("/api/optimization-data")
async def get_optimization_data():
    """Get optimization data for visualization (frontend endpoint)"""
    try:
        import asyncio
        
        # Get current data for optimization
        current_data = await orchestrator.generate_and_process_data()
        
        # Get optimization visualization data with timeout (30 seconds)
        loop = asyncio.get_event_loop()
        optimization_data = await loop.run_in_executor(
            None, 
            lambda: orchestrator.ml_model.get_optimization_data(current_data)
        )
        
        return {
            "optimization_data": optimization_data,
            "timestamp": datetime.now().isoformat()
        }
    except asyncio.TimeoutError:
        logger.error("Optimization data retrieval timed out after 30 seconds")
        raise HTTPException(status_code=408, detail="Optimization data retrieval timed out")
    except Exception as e:
        logger.error(f"Optimization data retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Optimization data retrieval failed")

@app.get("/api/control-settings")
async def get_control_settings():
    """Get current control settings (frontend endpoint)"""
    try:
        # Get current control settings from the orchestrator
        current_data = await orchestrator.generate_and_process_data()
        
        current_controls = {
            "kex": current_data.get('Pb_Conditioner_KEX_Flowrate', 45.0),
            "sipx": current_data.get('Pb_Rougher1_SIPX_Flowrate', 25.0)
        }
        
        logger.info(f"Current control settings retrieved: KEX={current_controls['kex']}, SIPX={current_controls['sipx']}")
        
        return {
            "controls": current_controls,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Control settings retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Control settings retrieval failed")

@app.post("/api/control-settings")
async def update_control_settings(controls: Dict[str, float]):
    """Update control settings (frontend endpoint)"""
    try:
        # Validate control parameters
        if 'kex' not in controls or 'sipx' not in controls:
            raise HTTPException(status_code=400, detail="Missing required control parameters: kex, sipx")
        
        # Update the orchestrator's control settings
        orchestrator.update_control_settings(controls)
        
        logger.warning(f"Control settings updated: KEX={controls.get('kex')}, SIPX={controls.get('sipx')}")
        
        return {
            "message": "Control settings updated successfully",
            "controls": controls,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Control settings update failed: {e}")
        raise HTTPException(status_code=500, detail="Control settings update failed")

@app.get("/api/connections")
async def get_connections():
    """Get system connections status (frontend endpoint)"""
    try:
        # Get WebSocket connection status
        ws_status = orchestrator.websocket_manager.get_connection_status()
        
        return {
            "active_connections": ws_status.get("active_connections", 0),
            "total_connections": ws_status.get("total_connections", 0),
            "status": "operational" if ws_status.get("active_connections", 0) > 0 else "disconnected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Connections status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Connections status retrieval failed")

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

@app.get("/api/res1-data")
async def get_res1_data(limit: int = 100):
    """Get latest RES1 data (real-time flotation data)"""
    try:
        data = orchestrator.database.get_latest_res1_data(limit)
        logger.info(f"Retrieved {len(data)} records from RES1")
        return {
            "data": data,
            "count": len(data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to retrieve RES1 data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve RES1 data")

@app.get("/api/res2-data")
async def get_res2_data(limit: int = 100):
    """Get latest RES2 data (ML predictions and actual values)"""
    try:
        data = orchestrator.database.get_latest_res2_data(limit)
        logger.info(f"Retrieved {len(data)} records from RES2")
        return {
            "data": data,
            "count": len(data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to retrieve RES2 data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve RES2 data")

@app.get("/api/res3-data")
async def get_res3_data(limit: int = 100):
    """Get latest RES3 data (optimization recommendations and control settings)"""
    try:
        data = orchestrator.database.get_latest_res3_data(limit)
        logger.info(f"Retrieved {len(data)} records from RES3")
        return {
            "data": data,
            "count": len(data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to retrieve RES3 data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve RES3 data")

@app.get("/api/res-tables-summary")
async def get_res_tables_summary():
    """Get summary of all RES tables"""
    try:
        res1_data = orchestrator.database.get_latest_res1_data(1)
        res2_data = orchestrator.database.get_latest_res2_data(1)
        res3_data = orchestrator.database.get_latest_res3_data(1)
        
        summary = {
            "RES1": {
                "latest_record": res1_data[0] if res1_data else None,
                "description": "Real-time flotation data (sensor readings and process parameters)"
            },
            "RES2": {
                "latest_record": res2_data[0] if res2_data else None,
                "description": "ML predictions and actual values"
            },
            "RES3": {
                "latest_record": res3_data[0] if res3_data else None,
                "description": "Optimization recommendations and control settings"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("Retrieved RES tables summary")
        return summary
    except Exception as e:
        logger.error(f"Failed to retrieve RES tables summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve RES tables summary")

@app.get("/api/res-tables-timing")
async def get_res_tables_timing():
    """Get RES tables save timing status"""
    try:
        current_time = datetime.now()
        
        # Calculate time since last saves
        time_since_res1 = (current_time - orchestrator.last_res1_save).total_seconds() / 60
        time_since_res2 = (current_time - orchestrator.last_res2_save).total_seconds() / 60
        time_since_res3 = (current_time - orchestrator.last_res3_save).total_seconds() / 60
        
        # Calculate time until next saves
        time_until_res1 = max(0, orchestrator.res1_interval - time_since_res1)
        time_until_res2 = max(0, orchestrator.res2_interval - time_since_res2)
        time_until_res3 = max(0, orchestrator.res3_interval - time_since_res3)
        
        timing_status = {
            "RES1": {
                "interval_minutes": orchestrator.res1_interval,
                "last_save": orchestrator.last_res1_save.isoformat(),
                "minutes_since_last_save": round(time_since_res1, 2),
                "minutes_until_next_save": round(time_until_res1, 2),
                "ready_to_save": time_since_res1 >= orchestrator.res1_interval
            },
            "RES2": {
                "interval_minutes": orchestrator.res2_interval,
                "last_save": orchestrator.last_res2_save.isoformat(),
                "minutes_since_last_save": round(time_since_res2, 2),
                "minutes_until_next_save": round(time_until_res2, 2),
                "ready_to_save": time_since_res2 >= orchestrator.res2_interval
            },
            "RES3": {
                "interval_minutes": orchestrator.res3_interval,
                "last_save": orchestrator.last_res3_save.isoformat(),
                "minutes_since_last_save": round(time_since_res3, 2),
                "minutes_until_next_save": round(time_until_res3, 2),
                "ready_to_save": time_since_res3 >= orchestrator.res3_interval
            },
            "current_time": current_time.isoformat()
        }
        
        logger.info("Retrieved RES tables timing status")
        return timing_status
    except Exception as e:
        logger.error(f"Failed to retrieve RES tables timing status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve RES tables timing status")


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
