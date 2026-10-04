from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class AgentPolicy(BaseModel):
    max_per_transaction: float = Field(default=50.0, description="Max amount agent can spend in a single call without HITL")
    daily_budget: float = Field(default=250.0, description="Max rolling 24h budget")
    allowed_vendors: List[str] = Field(default_factory=lambda: ["OpenAI", "AWS", "HuggingFace", "GitHub", "Cloudflare", "Anthropic"])
    allow_unlisted_vendors: bool = Field(default=False, description="If false, unlisted vendors require human approval")
    auto_approval_enabled: bool = Field(default=True, description="Enable autonomous policy execution")


class AgentCreate(BaseModel):
    name: str = Field(..., examples=["DevOps Provisioner Agent"])
    description: str = Field(default="", examples=["Manages compute instances and GPU API quotas"])
    wallet_balance: float = Field(default=500.0, description="Starting allocated balance")
    currency: str = Field(default="USD")
    policy: Optional[AgentPolicy] = None


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    wallet_balance: Optional[float] = None
    policy: Optional[AgentPolicy] = None


class Agent(BaseModel):
    id: str
    name: str
    description: str
    wallet_balance: float
    spent_today: float = 0.0
    currency: str = "USD"
    policy: AgentPolicy
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
