from typing import List
from fastapi import APIRouter, HTTPException
from ...models.negotiation import NegotiationRequest, NegotiationRecord
from ...services.policy_engine import policy_engine

router = APIRouter()


@router.get("", response_model=List[NegotiationRecord])
async def list_negotiations():
    """Retrieve all peer-to-peer agent budget negotiations and transfer transcripts."""
    return policy_engine.list_negotiations()


@router.post("/propose", response_model=NegotiationRecord, status_code=200)
async def propose_negotiation(req: NegotiationRequest):
    """Propose an autonomous budget negotiation and daily quota reallocation between two agents."""
    try:
        return policy_engine.negotiate_budget_transfer(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
