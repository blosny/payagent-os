"""
PayAgent OS — Internal Debt & Settlement Models
Zero-interest internal peer-to-peer credit lines between autonomous agents.
"""

from enum import Enum
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class DebtStatus(str, Enum):
    OUTSTANDING = "OUTSTANDING"
    SETTLED = "SETTLED"
    PARTIALLY_SETTLED = "PARTIALLY_SETTLED"


class DebtRecord(BaseModel):
    id: str
    debtor_agent_id: str = Field(..., description="Agent who borrowed funds")
    debtor_name: str
    creditor_agent_id: str = Field(..., description="Agent who provided the loan")
    creditor_name: str
    principal_amount: float = Field(..., gt=0, description="Original borrowed amount in USD")
    remaining_balance: float = Field(..., ge=0, description="Unpaid balance remaining in USD")
    negotiation_id: Optional[str] = None
    reason: str
    interest_rate: float = Field(default=0.0, description="Zero-interest peer credit")
    status: DebtStatus = DebtStatus.OUTSTANDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    settled_at: Optional[datetime] = None


class SettleDebtRequest(BaseModel):
    debt_id: Optional[str] = None
    debtor_agent_id: Optional[str] = None
    amount: Optional[float] = None


class SettlementResult(BaseModel):
    settled_count: int
    total_repaid: float
    debts_cleared: list[str]
    message: str
