"""FastAPI application for NeuroBright backend."""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import time
from contextlib import asynccontextmanager

from .websocket_manager import WebSocketManager
from .schemas import BrainStateResponse, StatusResponse, HealthResponse
from pipeline.inference.realtime_engine import RealtimeEngine
from pipeline.adaptive.learning_engine import AdaptiveLearningEngine
from utils.logger import get_logger, log_pipeline_step
from utils.config_loader import load_config

logger = get_logger(__name__)

# Global state
config = load_config()
ws_manager = WebSocketManager()
inference_engine = None
adaptive_engine = None
is_running = False
start_time = time.time()
prediction_history = []  # Store recent predictions


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global inference_engine, adaptive_engine
    
    log_pipeline_step("FastAPI Server Startup")
    
    try:
        # Initialize engines
        inference_engine = RealtimeEngine(config)
        adaptive_engine = AdaptiveLearningEngine(config)  # Fixed: pass config
        logger.info("[OK] Engines initialized")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
    
    yield
    
    logger.info("Shutting down...")


app = FastAPI(
    title="NeuroBright API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        config['api']['frontend_url'],
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws/brain-state")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time brain state streaming.
    
    Sends JSON every 0.5 seconds:
    {
        "state": "focused",
        "confidence": 0.87,
        "action": "increase_difficulty",
        "difficulty": 6.0,
        "band_powers": {...},
        "timestamp": 1234567890
    }
    """
    await ws_manager.connect(websocket)
    
    try:
        while True:
            if inference_engine and inference_engine.current_state is not None:
                # Get current state
                state_info = inference_engine.get_current_state()
                
                # Get adaptive action
                action_info = adaptive_engine.update(state_info['state'], time.time())
                
                # Combine data
                ts = time.time()
                data = {
                    'state': state_info['state'],
                    'confidence': state_info['confidence'],
                    'action': action_info['action'],
                    'difficulty': action_info['difficulty'],
                    'band_powers': state_info['band_powers'],
                    'timestamp': ts
                }

                # Store in prediction history (keep last 200)
                prediction_history.append({
                    'timestamp': ts,
                    'state': state_info['state'],
                    'confidence': state_info['confidence']
                })
                if len(prediction_history) > 200:
                    prediction_history.pop(0)
                
                await websocket.send_json(data)
            
            await asyncio.sleep(config['api']['websocket_interval'])
            
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.get("/api/bci-state")
async def get_bci_state():
    """
    Get current BCI state for the frontend polling compatibility.
    
    Returns:
        dict: Emotion state and band power features.
    """
    global inference_engine
    if inference_engine and inference_engine.current_state is not None:
        state_info = inference_engine.get_current_state()
        band_powers = state_info.get('band_powers', {})
        features = [
            band_powers.get('delta', 0.2),
            band_powers.get('theta', 0.2),
            band_powers.get('alpha', 0.2),
            band_powers.get('beta', 0.2),
            band_powers.get('gamma', 0.2)
        ]
        return {
            "emotion": state_info['state'].upper(),
            "features": features
        }
    else:
        return {
            "emotion": "NEUTRAL",
            "features": [0.2, 0.2, 0.2, 0.2, 0.2]
        }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        'status': 'ok',
        'version': '1.0.0'
    }


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Get system status."""
    return {
        'hardware_connected': inference_engine is not None and inference_engine.reader.serial_conn is not None,
        'model_loaded': inference_engine is not None,
        'current_state': inference_engine.get_current_state()['state'] if inference_engine else 'unknown',
        'uptime': time.time() - start_time
    }


@app.post("/api/session/start")  # POST: changes server state
async def start_session():
    """Start inference session."""
    global is_running
    
    if is_running:
        return {'status': 'already_running'}
    
    try:
        inference_engine.reader.connect()
        is_running = True
        logger.info("[OK] Session started")
        return {'status': 'started'}
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        return {'status': 'error', 'message': str(e)}


@app.post("/api/session/stop")  # POST: changes server state
async def stop_session():
    """Stop inference session."""
    global is_running
    
    if not is_running:
        return {'status': 'not_running'}
    
    try:
        inference_engine.reader.disconnect()
        is_running = False
        logger.info("[OK] Session stopped")
        return {'status': 'stopped'}
    except Exception as e:
        logger.error(f"Failed to stop: {e}")
        return {'status': 'error', 'message': str(e)}


@app.get("/api/history")
async def get_history(limit: int = 50):
    """Get recent prediction history.
    
    Args:
        limit: Number of recent predictions to return (default 50, max 200)
    """
    limit = min(limit, 200)
    recent = prediction_history[-limit:] if len(prediction_history) > limit else prediction_history
    return {
        'predictions': list(reversed(recent)),  # Most recent first
        'total_count': len(prediction_history)
    }


def run_server():
    """Run FastAPI server with uvicorn."""
    import uvicorn
    
    uvicorn.run(
        app,
        host=config['api']['host'],
        port=config['api']['port'],
        log_level="info"
    )


if __name__ == '__main__':
    run_server()
