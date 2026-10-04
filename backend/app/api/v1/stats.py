from fastapi import APIRouter
from ...services.policy_engine import policy_engine
from ...models.transaction import TransactionStatus
from ...config import settings

router = APIRouter()


@router.get("/summary")
async def get_system_summary():
    """Provides aggregated metrics for the PayAgent OS supervisor dashboard."""
    agents = policy_engine.list_agents()
    all_txs = policy_engine.list_transactions()

    total_allocated = sum(a.wallet_balance for a in agents)
    total_spent_today = sum(a.spent_today for a in agents)
    pending_approvals = [t for t in all_txs if t.status == TransactionStatus.PENDING_APPROVAL]
    autonomous_executed = [
        t for t in all_txs if t.status == TransactionStatus.APPROVED_AUTONOMOUS
    ]
    settled_or_approved = [
        t
        for t in all_txs
        if t.status
        in [
            TransactionStatus.APPROVED_AUTONOMOUS,
            TransactionStatus.APPROVED_BY_HUMAN,
            TransactionStatus.SETTLED,
        ]
    ]

    total_spent_volume = sum(t.amount for t in settled_or_approved)

    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "paypal_mode": settings.PAYPAL_MODE,
        "is_live_sandbox": settings.has_paypal_credentials,
        "active_agents_count": len([a for a in agents if a.is_active]),
        "total_allocated_funds": round(total_allocated, 2),
        "total_spent_today": round(total_spent_today, 2),
        "total_volume_processed": round(total_spent_volume, 2),
        "pending_approval_count": len(pending_approvals),
        "autonomous_execution_count": len(autonomous_executed),
        "total_transactions_count": len(all_txs),
    }
