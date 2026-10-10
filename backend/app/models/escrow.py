from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EscrowStatus(str, Enum):
    PENDING_DEPOSIT = "PENDING_DEPOSIT"
    IN_ESCROW = "IN_ESCROW"
    MILESTONE_SUBMITTED = "MILESTONE_SUBMITTED"
    VERIFIED_RELEASED = "VERIFIED_RELEASED"
    DISPUTED = "DISPUTED"
    REFUNDED = "REFUNDED"


class EscrowContract(BaseModel):
    id: str
    buyer_agent_id: str
    provider_name: str
    total_amount: float
    currency: str = "USD"
    milestone_description: str
    deliverable_evidence: Optional[str] = None
    status: EscrowStatus = EscrowStatus.IN_ESCROW
    paypal_order_id: Optional[str] = None
    paypal_capture_id: Optional[str] = None
    created_at: str
    released_at: Optional[str] = None


class CarbonOffsetRecord(BaseModel):
    id: str
    agent_id: str
    compute_hours: float
    kwh_consumed: float
    kg_co2_offset: float
    offset_cost_usd: float
    paypal_order_id: str
    certificate_hash: str
    created_at: str
