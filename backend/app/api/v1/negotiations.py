from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from ...models.negotiation import NegotiationRequest, NegotiationRecord
from ...models.debt import DebtRecord, DebtStatus, SettleDebtRequest, SettlementResult
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


@router.get("/debts", response_model=List[DebtRecord])
async def list_debts(status: Optional[DebtStatus] = Query(None, description="Filter by debt status")):
    """Retrieve internal debt ledger records."""
    return policy_engine.list_debts(status=status)


@router.post("/debts/settle", response_model=Dict[str, Any])
async def settle_debt_endpoint(req: SettleDebtRequest):
    """
    Settles an individual debt by ID or triggers settlement for all debts of a debtor agent.
    """
    if req.debt_id:
        success, msg, debt = policy_engine.settle_debt(req.debt_id, req.amount)
        if not success:
            raise HTTPException(status_code=400, detail=msg)
        return {
            "success": True,
            "message": msg,
            "debt": debt
        }
    elif req.debtor_agent_id:
        result: SettlementResult = policy_engine.settle_all_debts_for_agent(req.debtor_agent_id)
        return {
            "success": True,
            "message": result.message,
            "result": result
        }
    else:
        raise HTTPException(status_code=400, detail="Either 'debt_id' or 'debtor_agent_id' must be provided.")


@router.post("/debts/rollover", response_model=Dict[str, Any])
async def trigger_daily_rollover_and_settlement():
    """
    Triggers simulated 24h daily quota rollover and executes the autonomous debt settlement loop.
    Debtor agents repay creditor agents from refreshed daily balances.
    """
    return policy_engine.simulate_daily_rollover_and_settlement()
