from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status

from ...models.escrow import (
    EscrowContract,
    CarbonOffsetRecord,
)
from ...services.escrow_service import escrow_and_esg_service

router = APIRouter(prefix="/escrow", tags=["Milestone AI Escrow & ESG Offset"])


class CreateEscrowRequest(BaseModel):
    buyer_agent_id: str = "agent-payout"
    provider_name: str
    total_amount: float
    milestone_description: str


class SubmitDeliverableRequest(BaseModel):
    deliverable_evidence: str


class CarbonOffsetRequest(BaseModel):
    agent_id: str = "agent-devops"
    compute_hours: float
    kwh_consumed: float


@router.get("/contracts", response_model=List[EscrowContract])
async def list_escrow_contracts():
    return escrow_and_esg_service.get_contracts()


@router.post("/contracts", response_model=EscrowContract, status_code=status.HTTP_201_CREATED)
async def create_escrow_contract(payload: CreateEscrowRequest):
    return await escrow_and_esg_service.create_contract(
        buyer_agent_id=payload.buyer_agent_id,
        provider_name=payload.provider_name,
        total_amount=payload.total_amount,
        milestone_description=payload.milestone_description,
    )


@router.post("/contracts/{contract_id}/submit", response_model=EscrowContract)
async def submit_escrow_deliverable(contract_id: str, payload: SubmitDeliverableRequest):
    try:
        return await escrow_and_esg_service.submit_deliverable(
            contract_id=contract_id,
            deliverable_evidence=payload.deliverable_evidence,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/contracts/{contract_id}/release", response_model=EscrowContract)
async def release_escrow_funds(contract_id: str):
    try:
        return await escrow_and_esg_service.verify_and_release(contract_id=contract_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/carbon/offset", response_model=CarbonOffsetRecord)
async def offset_compute_carbon(payload: CarbonOffsetRequest):
    return await escrow_and_esg_service.offset_carbon(
        agent_id=payload.agent_id,
        compute_hours=payload.compute_hours,
        kwh_consumed=payload.kwh_consumed,
    )


@router.get("/carbon/records", response_model=List[CarbonOffsetRecord])
async def list_carbon_records():
    return escrow_and_esg_service.get_carbon_records()
