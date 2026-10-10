from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskAnalysisResult(BaseModel):
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Risk anomaly score between 0 (safe) and 100 (critical).")
    risk_level: RiskLevel
    flags: List[str] = Field(default_factory=list, description="List of detected anomalies or security flags.")
    is_blocked: bool = False
    requires_hitl: bool = False
    requires_multisig: bool = False
    analysis_summary: str
    prompt_injection_confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: str = "EXECUTE"  # EXECUTE, REQUIRE_HITL, REQUIRE_MULTISIG, BLOCK


class SignerRole(str, Enum):
    LEGAL_COMPLIANCE = "LEGAL_COMPLIANCE"
    SECOPS_AUDITOR = "SECOPS_AUDITOR"
    CFO_TREASURY = "CFO_TREASURY"
    SUPERVISOR_HUMAN = "SUPERVISOR_HUMAN"


class MultiSigStatus(str, Enum):
    PENDING_CONSENSUS = "PENDING_CONSENSUS"
    CONSENSUS_REACHED = "CONSENSUS_REACHED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"


class MultiSigSignature(BaseModel):
    signer_id: str
    signer_name: str
    role: SignerRole
    decision: str = "APPROVE"  # APPROVE, REJECT
    signature_hash: str
    reasoning: str
    signed_at: str


class MultiSigProposal(BaseModel):
    id: str
    initiator_agent_id: str
    initiator_agent_name: str
    amount: float
    currency: str = "USD"
    vendor: str
    purpose: str
    threshold_amount: float = 500.0
    required_signatures: int = 2
    status: MultiSigStatus = MultiSigStatus.PENDING_CONSENSUS
    signatures: List[MultiSigSignature] = Field(default_factory=list)
    risk_score: float = 0.0
    paypal_order_id: Optional[str] = None
    created_at: str
    executed_at: Optional[str] = None


class TaxJurisdiction(str, Enum):
    US_DOMESTIC = "US_DOMESTIC"
    EU_REVERSE_CHARGE = "EU_REVERSE_CHARGE"
    TURKEY_LOCAL = "TURKEY_LOCAL"
    REST_OF_WORLD = "REST_OF_WORLD"


class TaxBreakdown(BaseModel):
    vendor_name: str
    country_code: str
    jurisdiction: TaxJurisdiction
    net_amount: float
    tax_rate: float
    tax_amount: float
    total_amount: float
    withholding_tax_rate: float = 0.0
    withholding_tax_amount: float = 0.0
    is_reverse_charge: bool = False
    accounting_ledger_code: str
    erp_export_payload: Dict[str, Any] = Field(default_factory=dict)


class SLAIncidentStatus(str, Enum):
    MONITORED = "MONITORED"
    VIOLATED = "VIOLATED"
    DISPUTE_OPENED = "DISPUTE_OPENED"
    REFUND_PROCESSED = "REFUND_PROCESSED"
    RESOLVED = "RESOLVED"


class SLARecord(BaseModel):
    id: str
    vendor_name: str
    service_type: str
    paypal_order_id: str
    purchase_amount: float
    uptime_percentage: float
    error_rate: float
    error_threshold: float = 0.05
    status: SLAIncidentStatus = SLAIncidentStatus.MONITORED
    dispute_reason: Optional[str] = None
    refunded_amount: float = 0.0
    dispute_id: Optional[str] = None
    created_at: str
    resolved_at: Optional[str] = None


# Request payloads
class AnalyzeRiskRequest(BaseModel):
    reasoning: str
    amount: float
    vendor: str
    agent_id: str = "agent-devops"


class MultiSigCreateRequest(BaseModel):
    initiator_agent_id: str
    amount: float
    currency: str = "USD"
    vendor: str
    purpose: str


class MultiSigSignRequest(BaseModel):
    proposal_id: str
    signer_id: str
    role: SignerRole
    decision: str = "APPROVE"
    reasoning: str


class TaxCalculationRequest(BaseModel):
    vendor_name: str
    amount: float
    country_code: Optional[str] = None


class SLATriggerRequest(BaseModel):
    vendor_name: str
    paypal_order_id: str
    purchase_amount: float
    error_rate: float
    service_type: str = "CLOUD_API"
