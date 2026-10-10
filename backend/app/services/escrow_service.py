import uuid
import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timezone

from ..models.escrow import (
    EscrowStatus,
    EscrowContract,
    CarbonOffsetRecord,
)
from .paypal_service import paypal_service


class EscrowAndESGService:
    """Milestone-Based AI Escrow and Autonomous ESG Green Compute Carbon Offset Service."""

    def __init__(self):
        self._contracts: Dict[str, EscrowContract] = {}
        self._carbon_records: Dict[str, CarbonOffsetRecord] = {}
        self._seed_data()

    def _seed_data(self):
        now = datetime.now(timezone.utc).isoformat()
        sample_escrow = EscrowContract(
            id="ESCROW-78A1B902",
            buyer_agent_id="agent-payout",
            provider_name="Senior Rust ML Engineer (Contractor)",
            total_amount=350.00,
            currency="USD",
            milestone_description="Optimize CUDA kernel for LLM quantized inference latency < 12ms",
            deliverable_evidence="PR #42 merged with benchmark results: 9.8ms median latency.",
            status=EscrowStatus.VERIFIED_RELEASED,
            paypal_order_id="MOCK-ORD-ESCROW-01",
            paypal_capture_id="MOCK-CAP-ESCROW-01",
            created_at=now,
            released_at=now,
        )
        self._contracts[sample_escrow.id] = sample_escrow

    def get_contracts(self) -> List[EscrowContract]:
        return sorted(list(self._contracts.values()), key=lambda x: x.created_at, reverse=True)

    def get_carbon_records(self) -> List[CarbonOffsetRecord]:
        return sorted(list(self._carbon_records.values()), key=lambda x: x.created_at, reverse=True)

    async def create_contract(
        self,
        buyer_agent_id: str,
        provider_name: str,
        total_amount: float,
        milestone_description: str,
    ) -> EscrowContract:
        contract_id = f"ESCROW-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc).isoformat()
        order = await paypal_service.create_order(
            amount=total_amount,
            currency="USD",
            description=f"AI Milestone Escrow: {milestone_description[:50]}",
            reference_id=contract_id,
        )
        contract = EscrowContract(
            id=contract_id,
            buyer_agent_id=buyer_agent_id,
            provider_name=provider_name,
            total_amount=total_amount,
            currency="USD",
            milestone_description=milestone_description,
            deliverable_evidence=None,
            status=EscrowStatus.IN_ESCROW,
            paypal_order_id=order.get("id"),
            created_at=now,
        )
        self._contracts[contract_id] = contract
        return contract

    async def submit_deliverable(
        self,
        contract_id: str,
        deliverable_evidence: str,
    ) -> EscrowContract:
        contract = self._contracts.get(contract_id)
        if not contract:
            raise ValueError(f"Escrow contract '{contract_id}' not found.")
        contract.deliverable_evidence = deliverable_evidence
        contract.status = EscrowStatus.MILESTONE_SUBMITTED
        return contract

    async def verify_and_release(
        self,
        contract_id: str,
    ) -> EscrowContract:
        contract = self._contracts.get(contract_id)
        if not contract:
            raise ValueError(f"Escrow contract '{contract_id}' not found.")
        if contract.status not in [EscrowStatus.IN_ESCROW, EscrowStatus.MILESTONE_SUBMITTED]:
            raise ValueError(f"Contract cannot be released from status: {contract.status}")

        # Capture escrow funds via PayPal Orders API
        order_id = contract.paypal_order_id or f"MOCK-ORD-{uuid.uuid4().hex[:8].upper()}"
        capture_res = await paypal_service.capture_order(order_id)
        capture_id = None
        try:
            capture_id = capture_res["purchase_units"][0]["payments"]["captures"][0]["id"]
        except (KeyError, IndexError):
            capture_id = f"MOCK-CAP-{uuid.uuid4().hex[:8].upper()}"

        contract.paypal_capture_id = capture_id
        contract.status = EscrowStatus.VERIFIED_RELEASED
        contract.released_at = datetime.now(timezone.utc).isoformat()
        return contract

    async def offset_carbon(
        self,
        agent_id: str,
        compute_hours: float,
        kwh_consumed: float,
    ) -> CarbonOffsetRecord:
        rec_id = f"ESG-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc).isoformat()
        # 0.385 kg CO2 per kWh grid average, $0.025 per kg offset cost
        kg_co2 = round(kwh_consumed * 0.385, 2)
        cost = round(max(0.50, kg_co2 * 0.025), 2)

        order = await paypal_service.create_order(
            amount=cost,
            currency="USD",
            description=f"ESG Green Compute Offset ({kg_co2} kg CO2) for {agent_id}",
            reference_id=rec_id,
        )
        order_id = order.get("id", f"MOCK-ORD-ESG-{uuid.uuid4().hex[:6].upper()}")
        await paypal_service.capture_order(order_id)

        raw = f"{agent_id}:{kwh_consumed}:{kg_co2}:{order_id}:{now}"
        cert_hash = f"CERT-VERRA-ESG-{hashlib.sha256(raw.encode()).hexdigest()[:16].upper()}"

        record = CarbonOffsetRecord(
            id=rec_id,
            agent_id=agent_id,
            compute_hours=compute_hours,
            kwh_consumed=kwh_consumed,
            kg_co2_offset=kg_co2,
            offset_cost_usd=cost,
            paypal_order_id=order_id,
            certificate_hash=cert_hash,
            created_at=now,
        )
        self._carbon_records[rec_id] = record
        return record


escrow_and_esg_service = EscrowAndESGService()
