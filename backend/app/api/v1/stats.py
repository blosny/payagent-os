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


@router.get("/analytics")
async def get_analytics_breakdown():
    """Provides visual analytics, vendor shares, and guardrail savings breakdown."""
    agents = policy_engine.list_agents()
    all_txs = policy_engine.list_transactions()
    negotiations = policy_engine.list_negotiations()

    total_allocated = sum(a.wallet_balance for a in agents)
    total_spent_today = sum(a.spent_today for a in agents)
    total_daily_budget = sum(a.policy.daily_budget for a in agents)

    # Vendor spending breakdown
    vendor_totals = {}
    for tx in all_txs:
        if tx.status in [
            TransactionStatus.APPROVED_AUTONOMOUS,
            TransactionStatus.APPROVED_BY_HUMAN,
            TransactionStatus.SETTLED,
        ]:
            vendor = tx.vendor or "Other"
            vendor_totals[vendor] = vendor_totals.get(vendor, 0.0) + tx.amount

    vendor_breakdown = [
        {
            "vendor": v,
            "amount": round(amt, 2),
            "percentage": round((amt / max(total_spent_today, 1.0)) * 100, 1)
            if total_spent_today > 0
            else 0,
        }
        for v, amt in vendor_totals.items()
    ]

    # Agent breakdown & chart colors
    colors = ["#10b981", "#3b82f6", "#f59e0b", "#a855f7", "#ec4899"]
    agent_shares = []
    for i, a in enumerate(agents):
        pct = (
            round((a.spent_today / max(total_spent_today, 1.0)) * 100, 1)
            if total_spent_today > 0
            else 0
        )
        agent_shares.append(
            {
                "agent_id": a.id,
                "name": a.name,
                "personality": a.personality.value,
                "spent_today": round(a.spent_today, 2),
                "daily_budget": round(a.policy.daily_budget, 2),
                "wallet_balance": round(a.wallet_balance, 2),
                "share_percentage": pct,
                "color": colors[i % len(colors)],
            }
        )

    # Savings & Preserved Capital by Guardrails / Frugal Personality
    rejected_txs = [t for t in all_txs if t.status == TransactionStatus.REJECTED]
    rejected_volume = sum(t.amount for t in rejected_txs)
    frugal_rejections = [
        n for n in negotiations if not n.approved and "Cimri" in (n.transcript or "")
    ]
    frugal_saved = sum(n.amount for n in frugal_rejections)

    # P2P Negotiation volume
    approved_neg = [n for n in negotiations if n.approved]
    negotiation_volume = sum(n.amount for n in approved_neg)

    return {
        "total_allocated": round(total_allocated, 2),
        "total_spent_today": round(total_spent_today, 2),
        "total_daily_budget": round(total_daily_budget, 2),
        "savings_by_guardrails": round(rejected_volume + frugal_saved, 2),
        "negotiation_volume": round(negotiation_volume, 2),
        "active_negotiations_count": len(negotiations),
        "vendor_breakdown": vendor_breakdown,
        "agent_shares": agent_shares,
        "total_tx_count": len(all_txs),
        "approved_tx_count": len(
            [
                t
                for t in all_txs
                if t.status
                in [
                    TransactionStatus.APPROVED_AUTONOMOUS,
                    TransactionStatus.APPROVED_BY_HUMAN,
                ]
            ]
        ),
        "pending_tx_count": len(
            [t for t in all_txs if t.status == TransactionStatus.PENDING_APPROVAL]
        ),
    }

