from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class NegotiationRequest(BaseModel):
    requester_agent_id: str = Field(..., description="ID of the agent needing additional budget")
    target_agent_id: str = Field(..., description="ID of the agent with surplus budget to request from")
    amount: float = Field(..., gt=0, description="Amount of daily budget quota to transfer")
    currency: str = Field(default="USD")
    justification: str = Field(..., description="Agent reasoning for why surplus budget is needed")
    urgency: str = Field(default="HIGH", description="LOW, MEDIUM, HIGH, CRITICAL")


class NegotiationRecord(BaseModel):
    id: str
    requester_agent_id: str
    requester_name: str
    target_agent_id: str
    target_name: str
    amount: float
    currency: str
    justification: str
    urgency: str
    accepted: bool
    transcript: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
