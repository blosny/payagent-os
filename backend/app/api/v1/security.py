from typing import List, Optional
from fastapi import APIRouter, HTTPException, status

from ...models.security import (
    RiskAnalysisResult,
    AnalyzeRiskRequest,
    MultiSigProposal,
    MultiSigCreateRequest,
    MultiSigSignRequest,
    TaxBreakdown,
    TaxCalculationRequest,
    SLARecord,
    SLATriggerRequest,
)
from ...services.security_engine import (
    llm_risk_analyzer,
    multisig_manager,
    tax_compliance_engine,
    autonomous_sla_tracker,
)
from ...services.policy_engine import policy_engine

router = APIRouter(prefix="/security", tags=["Enterprise Security & Multi-Sig"])


# 1. LLM Risk & Guardrail Analyzer
@router.post("/risk/analyze", response_model=RiskAnalysisResult)
async def analyze_risk(payload: AnalyzeRiskRequest):
    """Evaluates spending reasoning and parameters against official PayPal AI Guardrails."""
    res = llm_risk_analyzer.analyze(
        reasoning=payload.reasoning,
        amount=payload.amount,
        vendor=payload.vendor,
        agent_id=payload.agent_id,
    )
    return res


# 2. Multi-Sig Proposals & Consensus
@router.get("/multisig/proposals", response_model=List[MultiSigProposal])
async def list_multisig_proposals():
    """Returns all enterprise multi-signature expenditure proposals."""
    return multisig_manager.get_proposals()


@router.get("/multisig/proposals/{proposal_id}", response_model=MultiSigProposal)
async def get_multisig_proposal(proposal_id: str):
    p = multisig_manager.get_proposal(proposal_id)
    if not p:
        raise HTTPException(status_code=404, detail="Multi-Sig proposal not found.")
    return p


@router.post("/multisig/proposals", response_model=MultiSigProposal, status_code=status.HTTP_201_CREATED)
async def create_multisig_proposal(payload: MultiSigCreateRequest):
    """Submits a new high-value expenditure for multi-agent cryptographic consensus."""
    agent = policy_engine.get_agent(payload.initiator_agent_id)
    agent_name = agent.name if agent else payload.initiator_agent_id

    # Risk evaluation
    risk = llm_risk_analyzer.analyze(
        reasoning=payload.purpose,
        amount=payload.amount,
        vendor=payload.vendor,
        agent_id=payload.initiator_agent_id,
    )

    proposal = multisig_manager.create_proposal(
        initiator_agent_id=payload.initiator_agent_id,
        initiator_agent_name=agent_name,
        amount=payload.amount,
        currency=payload.currency,
        vendor=payload.vendor,
        purpose=payload.purpose,
        risk_score=risk.risk_score,
    )
    return proposal


@router.post("/multisig/sign", response_model=MultiSigProposal)
async def sign_multisig_proposal(payload: MultiSigSignRequest):
    """Auditor agent or human supervisor signs a proposal."""
    signer_names = {
        "agent-legal": "Legal & Compliance AI Agent",
        "agent-secops": "SecOps & Auditor AI Agent",
        "agent-cfo": "CFO AI Treasury Copilot",
        "human-admin": "Enterprise Supervisor (CFO)",
    }
    signer_name = signer_names.get(payload.signer_id, f"Auditor ({payload.signer_id})")

    try:
        updated = await multisig_manager.sign_proposal(
            proposal_id=payload.proposal_id,
            signer_id=payload.signer_id,
            signer_name=signer_name,
            role=payload.role,
            decision=payload.decision,
            reasoning=payload.reasoning,
        )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/multisig/proposals/{proposal_id}/execute", response_model=MultiSigProposal)
async def execute_multisig_proposal(proposal_id: str):
    """Executes a consensus-reached proposal via PayPal Orders v2."""
    try:
        executed = await multisig_manager.execute_proposal(proposal_id)
        return executed
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# 3. Tax & VAT Compliance
@router.post("/tax/calculate", response_model=TaxBreakdown)
async def calculate_tax(payload: TaxCalculationRequest):
    """Classifies vendor tax jurisdiction, calculates VAT / Reverse Charge,
    and produces ready-to-import JSON accounting vouchers for SAP, QuickBooks & Logo."""
    return tax_compliance_engine.calculate_tax(
        vendor_name=payload.vendor_name,
        amount=payload.amount,
        country_code=payload.country_code,
    )


# 4. Autonomous SLA & Dispute Recovery
@router.get("/sla/records", response_model=List[SLARecord])
async def list_sla_records():
    """Lists all monitored cloud services and automated dispute/refund incidents."""
    return autonomous_sla_tracker.get_records()


@router.post("/sla/evaluate", response_model=SLARecord)
async def evaluate_sla_service(payload: SLATriggerRequest):
    """Evaluates service health. If error rate breaches the 5% SLA threshold,
    initiates an autonomous PayPal dispute and issues refund recovery."""
    rec = await autonomous_sla_tracker.evaluate_service(
        vendor_name=payload.vendor_name,
        paypal_order_id=payload.paypal_order_id,
        purchase_amount=payload.purchase_amount,
        error_rate=payload.error_rate,
        service_type=payload.service_type,
    )
    return rec
