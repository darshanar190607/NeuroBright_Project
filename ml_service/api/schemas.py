"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel
from typing import Dict, List, Optional


class BandPowers(BaseModel):
    """EEG frequency band powers."""
    delta: float
    theta: float
    alpha: float
    beta: float
    gamma: float


class BrainStateResponse(BaseModel):
    """Real-time brain state response."""
    state: str
    confidence: float
    action: str
    difficulty: float
    band_powers: Dict[str, float]
    timestamp: float


class StatusResponse(BaseModel):
    """System status response."""
    hardware_connected: bool
    model_loaded: bool
    current_state: str
    uptime: float


class PredictionRecord(BaseModel):
    """Single prediction record."""
    timestamp: float
    state: str
    confidence: float


class HistoryResponse(BaseModel):
    """Prediction history response."""
    predictions: List[PredictionRecord]
    total_count: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
