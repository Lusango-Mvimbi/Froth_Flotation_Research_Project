"""
WebSocket Manager Implementation
==============================

This module implements the WebSocket connection management following SOLID principles.
"""

import asyncio
import json
from typing import Dict, Any, List, Set
from fastapi import WebSocket, WebSocketDisconnect

from services.interfaces import IWebSocketManager
from services.shared_logging import get_logger

class WebSocketConnectionManager(IWebSocketManager):
    """Manages WebSocket connections for real-time data broadcasting"""
    
    def __init__(self, logger=None):
        self.logger = logger or get_logger(__name__)
        self.active_connections: Set[WebSocket] = set()
        self.connection_count = 0
    
    async def connect(self, websocket: WebSocket) -> None:
        """Connect a new WebSocket client"""
        try:
            await websocket.accept()
            self.active_connections.add(websocket)
            self.connection_count += 1
            self.logger.info(f"WebSocket client connected. Total connections: {self.connection_count}")
            
            # Send welcome message
            welcome_message = {
                "type": "connection",
                "message": "Connected to Froth Flotation Digital Twin",
                "timestamp": asyncio.get_event_loop().time()
            }
            await websocket.send_text(json.dumps(welcome_message))
            
        except Exception as e:
            self.logger.error(f"Failed to connect WebSocket client: {e}")
            raise
    
    async def disconnect(self, websocket: WebSocket) -> None:
        """Disconnect a WebSocket client"""
        try:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                self.connection_count -= 1
                self.logger.info(f"WebSocket client disconnected. Total connections: {self.connection_count}")
        except Exception as e:
            self.logger.error(f"Error during WebSocket disconnect: {e}")
    
    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        # Convert message to JSON string
        try:
            message_json = json.dumps(message)
        except Exception as e:
            self.logger.error(f"Failed to serialize message: {e}")
            return
        
        # Send to all connected clients
        disconnected_clients = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except WebSocketDisconnect:
                disconnected_clients.add(connection)
            except Exception as e:
                self.logger.error(f"Failed to send message to client: {e}")
                disconnected_clients.add(connection)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            await self.disconnect(client)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return self.connection_count
    
    async def broadcast_data_point(self, data_point: Dict[str, Any]) -> None:
        """Broadcast a data point to all connected clients"""
        message = {
            "type": "data_point",
            "data": data_point,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(message)
    
    async def broadcast_status_update(self, status: str, message: str) -> None:
        """Broadcast a status update to all connected clients"""
        status_message = {
            "type": "status_update",
            "status": status,
            "message": message,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(status_message)
    
    async def broadcast_error(self, error_message: str) -> None:
        """Broadcast an error message to all connected clients"""
        error_data = {
            "type": "error",
            "message": error_message,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(error_data)
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get information about current connections"""
        return {
            "active_connections": self.connection_count,
            "status": "running" if self.connection_count > 0 else "idle"
        }
