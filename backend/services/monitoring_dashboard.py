"""
Monitoring Dashboard API
========================

Provides API endpoints for monitoring dashboard functionality.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any
from monitoring_service import (
    prediction_monitor, 
    system_monitor, 
    alert_manager, 
    get_monitoring_status
)

app = FastAPI(
    title="Flotation Monitoring Dashboard API",
    description="API for monitoring the froth flotation prediction system",
    version="4.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Flotation Monitoring Dashboard",
        "version": "4.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/monitoring/status")
async def get_status():
    """Get comprehensive monitoring status."""
    try:
        return get_monitoring_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/predictions")
async def get_prediction_metrics():
    """Get prediction performance metrics."""
    try:
        return prediction_monitor.get_performance_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/system")
async def get_system_metrics():
    """Get system performance metrics."""
    try:
        return system_monitor.get_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/alerts")
async def get_alerts():
    """Get active alerts."""
    try:
        return {
            "active_alerts": alert_manager.get_active_alerts(),
            "total_active": len(alert_manager.get_active_alerts())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/monitoring/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert."""
    try:
        alert_manager.acknowledge_alert(alert_id)
        return {"message": f"Alert {alert_id} acknowledged", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/monitoring/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve an alert."""
    try:
        alert_manager.resolve_alert(alert_id)
        return {"message": f"Alert {alert_id} resolved", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/health")
async def health_check():
    """Health check endpoint."""
    try:
        services_status = system_monitor.system_stats.get('service_health', {})
        healthy_services = sum(1 for s in services_status.values() if s.get('status') == 'healthy')
        total_services = len(services_status)
        
        overall_health = "healthy" if healthy_services == total_services else "degraded"
        
        return {
            "status": overall_health,
            "services": {
                "healthy": healthy_services,
                "total": total_services,
                "details": services_status
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/performance")
async def get_performance_history():
    """Get performance history for charts."""
    try:
        # Get recent performance data
        history = {
            "cpu_usage": system_monitor.system_stats.get('cpu_usage', [])[-100:],
            "memory_usage": system_monitor.system_stats.get('memory_usage', [])[-100:],
            "prediction_performance": prediction_monitor.performance_history[-100:],
            "timeframe": "last_100_samples"
        }
        
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/monitoring/test-alert")
async def send_test_alert():
    """Send a test alert (for testing purposes)."""
    try:
        alert_id = alert_manager.send_alert(
            alert_type="test",
            message="This is a test alert from the monitoring system",
            severity="INFO"
        )
        return {
            "message": "Test alert sent",
            "alert_id": alert_id,
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🖥️ Starting Monitoring Dashboard API...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8052,
        log_level="info"
    )
