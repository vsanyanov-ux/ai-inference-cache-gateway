from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MockMLResult(BaseModel):
    label: str
    score: float

class PredictionRequest(BaseModel):
    text: str

class PredictionResponse(BaseModel):
    text: str
    label: str
    score: float
    latency: float
    cached: bool
    timestamp: datetime
