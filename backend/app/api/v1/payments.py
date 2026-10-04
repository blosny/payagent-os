from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from ...models.transaction import (
    TransactionIntent,
    TransactionRecord,
    TransactionStatus,
    ApprovalAction,
)
from ...services.policy_engine import policy_engine

router = APIRouter()


@router.get("", response_model=List[TransactionRecord])
async def list_transactions(
    status: Optional[TransactionStatus] = Query(None, description="Filter by status")
):
    """List transaction audit log, optionally filtered by status (e.g. PENDING_APPROVAL)."""
    return policy_engine.list_transactions(status)


@router.post("/intent", response_model=TransactionRecord)
async def submit_payment_intent(intent: TransactionIntent):
    """
    Primary endpoint for AI Agents: Submit an autonomous payment intent.
    - If policy checks pass: Autonomously executed via PayPal REST API.
    - If limits exceeded: Paused into PENDING_APPROVAL queue for Human-in-the-Loop review.
    """
    try:
        record = await policy_engine.submit_intent(intent)
        return record
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")


@router.get("/{tx_id}", response_model=TransactionRecord)
async def get_transaction(tx_id: str):
    """Retrieve full audit details for a specific transaction."""
    tx = policy_engine.get_transaction(tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.post("/{tx_id}/resolve", response_model=TransactionRecord)
async def resolve_transaction(tx_id: str, action: ApprovalAction):
    """
    Human-in-the-Loop (HITL) Endpoint:
    Allows a human supervisor to APPROVE or REJECT a paused agent payment.
    Upon approval, triggers the PayPal Orders/Payouts execution immediately.
    """
    try:
        resolved = await policy_engine.resolve_pending_transaction(
            tx_id=tx_id,
            decision=action.decision,
            reviewer_notes=action.reviewer_notes,
        )
        return resolved
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resolution error: {str(e)}")
