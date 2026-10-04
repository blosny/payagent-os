import pytest
from backend.app.models.negotiation import NegotiationRequest
from backend.app.services.policy_engine import PolicyEngine


@pytest.fixture
def engine():
    return PolicyEngine()


def test_successful_budget_negotiation(engine):
    # agent-devops has daily_budget = 200.0, spent_today = 0.0 -> headroom = 200.0
    # agent-research has daily_budget = 100.0
    req = NegotiationRequest(
        requester_agent_id="agent-research",
        target_agent_id="agent-devops",
        amount=35.0,
        currency="USD",
        justification="Urgent quota needed for large-scale embedding batch job.",
        urgency="HIGH",
    )

    record = engine.negotiate_budget_transfer(req)

    assert record.accepted is True
    assert record.amount == 35.0
    assert "APPROVED autonomously" in record.transcript

    # Verify agent quotas updated
    devops = engine.get_agent("agent-devops")
    research = engine.get_agent("agent-research")
    assert devops.policy.daily_budget == 165.0  # 200 - 35
    assert research.policy.daily_budget == 135.0  # 100 + 35


def test_rejected_budget_negotiation_insufficient_headroom(engine):
    # agent-devops has daily_budget = 200.0, spent_today = 0.0 -> headroom = 200.0
    # Requesting 250.0 should be rejected
    req = NegotiationRequest(
        requester_agent_id="agent-research",
        target_agent_id="agent-devops",
        amount=250.0,
        currency="USD",
        justification="Massive cluster procurement request.",
        urgency="CRITICAL",
    )

    record = engine.negotiate_budget_transfer(req)

    assert record.accepted is False
    assert "REJECTED" in record.transcript
    devops = engine.get_agent("agent-devops")
    research = engine.get_agent("agent-research")
    assert devops.policy.daily_budget == 200.0  # Unchanged
    assert research.policy.daily_budget == 100.0  # Unchanged


def test_negotiation_self_error(engine):
    req = NegotiationRequest(
        requester_agent_id="agent-devops",
        target_agent_id="agent-devops",
        amount=10.0,
        currency="USD",
        justification="Self negotiation test.",
    )
    with pytest.raises(ValueError, match="cannot negotiate a budget transfer with itself"):
        engine.negotiate_budget_transfer(req)


@pytest.mark.anyio
async def test_automated_shortfall_detection_and_approval(engine):
    # agent-research: max_per_transaction=25.0, daily_budget=100.0
    # intent: 85.0 -> shortfall = 60.0
    # agent-devops has 200.0 headroom, should be picked as donor
    from backend.app.models.transaction import TransactionIntent, TransactionStatus

    intent = TransactionIntent(
        agent_id="agent-research",
        amount=85.0,
        currency="USD",
        recipient="OpenAI",
        category="API_QUOTA",
        reasoning="Batch embedding job for 50k scientific papers",
    )

    tx = await engine.submit_intent(intent)

    assert tx.status == TransactionStatus.PENDING_APPROVAL
    assert tx.shortfall_amount == 60.0
    assert tx.proposed_donor_agent_id in ["agent-payout", "agent-devops"]
    donor_id = tx.proposed_donor_agent_id
    donor_initial_budget = engine.get_agent(donor_id).policy.daily_budget

    # Now approve the transaction
    resolved = await engine.resolve_pending_transaction(tx.id, "APPROVE")
    assert resolved.status == TransactionStatus.APPROVED_BY_HUMAN

    # Donor should have given 60.0
    donor = engine.get_agent(donor_id)
    research = engine.get_agent("agent-research")
    assert donor.policy.daily_budget == donor_initial_budget - 60.0
    assert research.policy.daily_budget == 160.0  # 100 + 60


