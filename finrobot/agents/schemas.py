from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator

class MacroSignal(BaseModel):
    agent_id: str
    regime: Literal['risk_on', 'risk_off', 'neutral']
    confidence: float = Field(..., ge=0.0, le=1.0)
    rationale: str
    data_used: List[str] = []

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError(f'confidence must be in [0.0, 1.0], got {v}')
        return v

class SectorSignal(BaseModel):
    agent_id: str
    sector: str
    signal: Literal['bullish', 'bearish', 'neutral']
    confidence: float = Field(..., ge=0.0, le=1.0)
    rationale: str

class PhilosophySignal(BaseModel):
    agent_id: str
    philosophy: str  # e.g., 'Druckenmiller', 'Ackman'
    outlook: str
    conviction: float = Field(..., ge=0.0, le=1.0)
    rationale: str

class RiskAssessment(BaseModel):
    severity: float = Field(..., ge=0.0, le=1.0)
    risks: List[str]
    mitigations: List[str]
    block_execution: bool = False

class FinalDecision(BaseModel):
    action: Literal['buy', 'sell', 'hold']
    ticker: str
    size_pct: float = Field(..., ge=0.0, le=100.0)
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    rationale: str
