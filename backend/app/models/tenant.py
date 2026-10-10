import uuid
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class Department(BaseModel):
    id: str
    name: str
    code: str  # ENG, RES, MKT
    allocated_budget: float
    spent_today: float = 0.0
    currency: str = "USD"
    lead_name: str
    lead_email: str
    assigned_agent_ids: List[str] = Field(default_factory=list)
    created_at: str


class DepartmentTransferRequest(BaseModel):
    from_dept_id: str
    to_dept_id: str
    amount: float = Field(..., gt=0)
    reason: str
    authorized_by: str = "Elena Rostova (CFO)"


class DepartmentTransferResult(BaseModel):
    transfer_id: str
    from_dept_id: str
    to_dept_id: str
    from_dept_name: str
    to_dept_name: str
    amount: float
    reason: str
    authorized_by: str
    timestamp: str
    status: str = "COMPLETED"


class TenantSummary(BaseModel):
    total_departments: int
    total_allocated: float
    total_spent: float
    departments: List[Department]
    recent_transfers: List[DepartmentTransferResult] = Field(default_factory=list)
