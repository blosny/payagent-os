from enum import Enum
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class SubscriptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    UNUSED_WARNING = "UNUSED_WARNING"
    CANCELED = "CANCELED"
    FROZEN = "FROZEN"


class SaaSSubscription(BaseModel):
    id: str
    service_name: str
    plan_tier: str = "BUSINESS"
    monthly_cost: float
    currency: str = "USD"
    paypal_vault_id: str
    last_agent_call_at: str
    days_unused: int = 0
    inactivity_threshold_days: int = 14
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    savings_on_cancel: float = 0.0
    agent_subscribers: List[str] = Field(default_factory=list)
    created_at: str


class CancelSubscriptionRequest(BaseModel):
    subscription_id: str
    reason: str = "Unused by AI fleet"
    confirmed_by: str = "supervisor"
