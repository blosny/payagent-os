import pytest
from backend.app.models.agent import Agent, AgentPolicy
from backend.app.models.transaction import TransactionIntent
from backend.app.services.policy_engine import PolicyEngine


@pytest.fixture
def engine():
    return PolicyEngine()


def test_seed_agents(engine):
    agents = engine.list_agents()
    assert len(agents) >= 3
    devops = engine.get_agent("agent-devops")
    assert devops is not None
    assert devops.wallet_balance == 1200.0


def test_policy_allowlist_pass(engine):
    devops = engine.get_agent("agent-devops")
    intent = TransactionIntent(
        agent_id="agent-devops",
        amount=15.0,
        currency="USD",
        recipient="AWS",
        category="CLOUD_COMPUTE",
        reasoning="Spot node provisioning",
    )
    can_execute, reason = engine.evaluate_policy(devops, intent)
    assert can_execute is True
    assert "Within all autonomous policy limits" in reason


def test_policy_limit_exceeded(engine):
    devops = engine.get_agent("agent-devops")
    intent = TransactionIntent(
        agent_id="agent-devops",
        amount=95.0,  # Max limit is 40.0
        currency="USD",
        recipient="AWS",
        category="CLOUD_COMPUTE",
        reasoning="Large cluster provisioning",
    )
    can_execute, reason = engine.evaluate_policy(devops, intent)
    assert can_execute is False
    assert "exceeds single transaction limit" in reason


def test_policy_unlisted_vendor(engine):
    devops = engine.get_agent("agent-devops")
    intent = TransactionIntent(
        agent_id="agent-devops",
        amount=10.0,
        currency="USD",
        recipient="UntrustedVendorX",
        category="CLOUD_COMPUTE",
        reasoning="Testing unlisted merchant",
    )
    can_execute, reason = engine.evaluate_policy(devops, intent)
    assert can_execute is False
    assert "not on the agent's pre-approved allowlist" in reason
