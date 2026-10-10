from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class PayPalWebhookEvent(BaseModel):
    id: str = Field(..., description="Unique event identifier from PayPal (WH-...)")
    event_version: str = Field(default="1.0")
    create_time: str
    event_type: str = Field(..., description="e.g. PAYMENT.CAPTURE.COMPLETED, CHECKOUT.ORDER.APPROVED")
    summary: str
    resource_type: str = Field(default="capture")
    resource: Dict[str, Any] = Field(default_factory=dict)
    links: list = Field(default_factory=list)


class WebhookVerificationRequest(BaseModel):
    transmission_id: str
    transmission_time: str
    cert_url: str
    auth_algo: str
    transmission_sig: str
    webhook_id: Optional[str] = "WH-SIMULATED-PAYAGENT-01"
    webhook_event: Dict[str, Any]


class WebhookVerificationResponse(BaseModel):
    verification_status: str = Field(..., description="'SUCCESS' or 'FAILURE'")
    is_verified: bool
    event_type: str
    processed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    action_taken: str
