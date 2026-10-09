"""
Unit tests for Internal Autonomous Debt Ledger & Settlement Loop
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.policy_engine import policy_engine
from backend.app.models.negotiation import NegotiationRequest
from backend.app.models.debt import DebtStatus


@pytest.fixture(autouse=True)
def reset_policy_engine():
    policy_engine._debts.clear()
    policy_engine._negotiations.clear()
    # Reset default agents
    policy_engine._seed_default_agents()


def test_negotiation_creates_debt_record():
    req = NegotiationRequest(
        requester_agent_id="agent-research",
        target_agent_id="agent-devops",
        amount=35.0,
        currency="USD",
        justification="Urgent GPU cluster compute for training",
        urgency="CRITICAL"  # DevOps accepts CRITICAL
    )
    record = policy_engine.negotiate_budget_transfer(req)
    assert record.accepted is True

    # Verify Debt record was created
    debts = policy_engine.list_debts()
    assert len(debts) == 1
    debt = debts[0]
    assert debt.debtor_agent_id == "agent-research"
    assert debt.creditor_agent_id == "agent-devops"
    assert debt.principal_amount == 35.0
    assert debt.remaining_balance == 35.0
    assert debt.status == DebtStatus.OUTSTANDING


def test_settle_debt_atomic_transfer():
    req = NegotiationRequest(
        requester_agent_id="agent-research",
        target_agent_id="agent-devops",
        amount=30.0,
        currency="USD",
        justification="Testing repayment",
        urgency="CRITICAL"
    )
    policy_engine.negotiate_budget_transfer(req)
    debts = policy_engine.list_debts(DebtStatus.OUTSTANDING)
    assert len(debts) == 1
    debt = debts[0]

    devops = policy_engine.get_agent("agent-devops")
    research = policy_engine.get_agent("agent-research")
    devops_bal_before = devops.wallet_balance
    research_bal_before = research.wallet_balance

    # Settle debt
    success, msg, updated_debt = policy_engine.settle_debt(debt.id)
    assert success is True
    assert updated_debt.status == DebtStatus.SETTLED
    assert updated_debt.remaining_balance == 0.0

    # Balances shifted
    assert research.wallet_balance == research_bal_before - 30.0
    assert devops.wallet_balance == devops_bal_before + 30.0


def test_settle_all_debts_for_agent():
    req = NegotiationRequest(
        requester_agent_id="agent-research",
        target_agent_id="agent-devops",
        amount=25.0,
        currency="USD",
        justification="Borrowing 25",
        urgency="CRITICAL"
    )
    policy_engine.negotiate_budget_transfer(req)

    res = policy_engine.settle_all_debts_for_agent("agent-research")
    assert res.settled_count == 1
    assert res.total_repaid == 25.0

    remaining = policy_engine.list_debts(DebtStatus.OUTSTANDING)
    assert len(remaining) == 0


def test_daily_rollover_and_settlement_loop():
    req = NegotiationRequest(
        requester_agent_id="agent-research",
        target_agent_id="agent-devops",
        amount=40.0,
        currency="USD",
        justification="Daily rollover test",
        urgency="CRITICAL"
    )
    policy_engine.negotiate_budget_transfer(req)

    # Agent has spent money today
    research = policy_engine.get_agent("agent-research")
    research.spent_today = 80.0

    # Run daily rollover
    summary = policy_engine.simulate_daily_rollover_and_settlement()
    assert summary["agents_reset_count"] >= 3
    assert research.spent_today == 0.0
    assert summary["debts_cleared_count"] == 1
    assert summary["total_settled_volume"] == 40.0


@pytest.mark.asyncio
async def test_negotiations_debt_api_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a debt via negotiation
        prop_res = await client.post("/api/v1/negotiations/propose", json={
            "requester_agent_id": "agent-research",
            "target_agent_id": "agent-devops",
            "amount": 20.0,
            "currency": "USD",
            "justification": "API query burst",
            "urgency": "CRITICAL"
        })
        assert prop_res.status_code == 200

        # GET /api/v1/negotiations/debts
        debts_res = await client.get("/api/v1/negotiations/debts")
        assert debts_res.status_code == 200
        debts_data = debts_res.json()
        assert len(debts_data) >= 1
        debt_id = debts_data[0]["id"]

        # POST /api/v1/negotiations/debts/settle
        settle_res = await client.post("/api/v1/negotiations/debts/settle", json={
            "debt_id": debt_id
        })
        assert settle_res.status_code == 200
        assert settle_res.json()["debt"]["status"] == "SETTLED"

        # POST /api/v1/negotiations/debts/rollover
        roll_res = await client.post("/api/v1/negotiations/debts/rollover")
        assert roll_res.status_code == 200
        assert "agents_reset_count" in roll_res.json()
