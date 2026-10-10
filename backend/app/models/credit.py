from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class FICOConfig(BaseModel):
    on_time_repayment_bonus: int = 45
    budget_discipline_bonus: int = 25
    policy_anomaly_penalty: int = 40
    high_risk_penalty: int = 75
    prime_threshold: int = 800
    trusted_threshold: int = 740
    monitored_threshold: int = 670


class AgentCreditScore(BaseModel):
    agent_id: str
    agent_name: str
    fico_score: int = Field(..., ge=300, le=850, description="FICO score range 300 to 850")
    tier: str  # Prime, Trusted, Monitored, Restricted
    color_accent: str = "#10b981"
    dynamic_daily_limit: float
    total_settled_debts: int = 0
    anomalies_count: int = 0
    last_adjusted_at: str


class FICOUpdateResponse(BaseModel):
    agent_id: str
    old_score: int
    new_score: int
    old_limit: float
    new_limit: float
    tier: str
    reason: str
