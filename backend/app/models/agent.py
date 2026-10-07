from enum import Enum
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class AgentPersonality(str, Enum):
    FRUGAL_VAULT = "FRUGAL_VAULT"                # Cimri / Kasa (Sadece CRITICAL durumda kota verir)
    GROWTH_EXPLORER = "GROWTH_EXPLORER"          # Büyüme & Ar-Ge (İnovasyon ve deneyler için cömert)
    BALANCED_COORDINATOR = "BALANCED_COORDINATOR"# Dengeli Hazine (Rasyonel ve çıktı odaklı)


class AgentPolicy(BaseModel):
    max_per_transaction: float = Field(default=50.0, description="Max amount agent can spend in a single call without HITL")
    daily_budget: float = Field(default=250.0, description="Max rolling 24h budget")
    allowed_vendors: List[str] = Field(default_factory=lambda: ["OpenAI", "AWS", "HuggingFace", "GitHub", "Cloudflare", "Anthropic"])
    allow_unlisted_vendors: bool = Field(default=False, description="If false, unlisted vendors require human approval")
    auto_approval_enabled: bool = Field(default=True, description="Enable autonomous policy execution")
    min_lending_urgency: str = Field(default="HIGH", description="LOW, MEDIUM, HIGH, CRITICAL required to share budget")


class AgentCreate(BaseModel):
    name: str = Field(..., examples=["DevOps Provisioner Agent"])
    description: str = Field(default="", examples=["Manages compute instances and GPU API quotas"])
    wallet_balance: float = Field(default=500.0, description="Starting allocated balance")
    currency: str = Field(default="USD")
    personality: AgentPersonality = AgentPersonality.BALANCED_COORDINATOR
    personality_description: str = Field(default="Dengeli harcama ve rasyonel kota takası")
    policy: Optional[AgentPolicy] = None


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    wallet_balance: Optional[float] = None
    personality: Optional[AgentPersonality] = None
    personality_description: Optional[str] = None
    policy: Optional[AgentPolicy] = None


class Agent(BaseModel):
    id: str
    name: str
    description: str
    wallet_balance: float
    spent_today: float = 0.0
    currency: str = "USD"
    personality: AgentPersonality = AgentPersonality.BALANCED_COORDINATOR
    personality_description: str = "Dengeli harcama ve rasyonel kota takası"
    policy: AgentPolicy
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

