"""WebSocket connection manager."""

from fastapi import WebSocket
from typing import List
import json
from utils.logger import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasting."""
    
    def __init__(self):
        """Initialize manager."""
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """
        Accept new WebSocket connection.
        
        Args:
            websocket (WebSocket): WebSocket connection
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """
        Remove WebSocket connection.
        
        Args:
            websocket (WebSocket): WebSocket connection
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, data: dict):
        """
        Broadcast data to all connected clients.
        
        Args:
            data (dict): Data to broadcast
        """
        if not self.active_connections:
            return
        
        message = json.dumps(data)
        
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                self.disconnect(connection)
    
    async def broadcast_error(self, error_message: str):
        """
        Broadcast error to all clients.
        
        Args:
            error_message (str): Error message
        """
        await self.broadcast({
            'type': 'error',
            'message': error_message
        })
