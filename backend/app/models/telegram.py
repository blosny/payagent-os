from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TelegramSettings(BaseModel):
    connected_account: str = "@elena_cfo"
    hitl_approval_requests: bool = True
    blocked_risk_events: bool = True
    daily_treasury_summary: bool = False
    is_connected: bool = True


class TelegramAlertNotification(BaseModel):
    id: str
    recipient: str
    event_type: str  # HITL_PENDING, RISK_BLOCKED, DAILY_SUMMARY
    title: str
    message: str
    amount: Optional[float] = None
    vendor: Optional[str] = None
    action_url: Optional[str] = None
    sent_at: str
    delivered: bool = True
