import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.models.arbitrage import (
    WorkloadType,
    BiddingStrategy,
    BiddingRequest,
    ArbitrageExecutionRequest,
    LiquidityRebalanceRequest,
)
from backend.app.services.arbitrage_engine import arbitrage_engine
from backend.app.services.policy_engine import policy_engine

client = TestClient(app)


def test_market_spot_rates():
    rates = arbitrage_engine.get_market_spot_rates()
    assert "spot_board" in rates
    assert rates["total_categories"] == 4
    assert WorkloadType.GPU_INFERENCE.value in rates["spot_board"]
    assert WorkloadType.MODEL_FINE_TUNING.value in rates["spot_board"]
    assert len(rates["spot_board"][WorkloadType.GPU_INFERENCE.value]) >= 3


def test_solicit_quotes_cost_first():
    req = BiddingRequest(
        requesting_agent_id="agent-devops",
        workload_type=WorkloadType.GPU_INFERENCE,
        workload_description="Llama-3-70B model evaluation for DevOps telemetry",
        units_required=5.0,
        strategy=BiddingStrategy.COST_FIRST,
    )
    result = arbitrage_engine.solicit_quotes(req)

    assert result.bidding_id.startswith("bid-")
    assert len(result.quotes) >= 3
    assert result.winning_quote.total_price <= result.highest_quote.total_price
    assert result.arbitrage_saved_amount == round(result.highest_quote.total_price - result.winning_quote.total_price, 2)
    assert result.savings_percentage >= 0.0
    assert "Cost-first" in result.decision_rationale


def test_solicit_quotes_speed_first():
    req = BiddingRequest(
        requesting_agent_id="agent-research",
        workload_type=WorkloadType.BULK_EMBEDDINGS,
        workload_description="Urgent 10M token embedding indexing",
        units_required=10.0,
        strategy=BiddingStrategy.SPEED_FIRST,
    )
    result = arbitrage_engine.solicit_quotes(req)

    assert len(result.quotes) >= 3
    # Speed first winner should have lowest or tied lowest latency
    min_lat = min(q.latency_ms for q in result.quotes)
    assert result.winning_quote.latency_ms == min_lat
    assert "Speed-first" in result.decision_rationale


def test_solicit_quotes_balanced():
    req = BiddingRequest(
        requesting_agent_id="agent-devops",
        workload_type=WorkloadType.MODEL_FINE_TUNING,
        workload_description="Balanced LoRA fine-tune cluster",
        units_required=2.0,
        strategy=BiddingStrategy.BALANCED,
    )
    result = arbitrage_engine.solicit_quotes(req)
    assert "Balanced optimization" in result.decision_rationale


@pytest.mark.asyncio
async def test_execute_winning_bid_flow():
    # 1. Solicit quotes
    req = BiddingRequest(
        requesting_agent_id="agent-devops",
        workload_type=WorkloadType.SERVERLESS_COMPUTE,
        workload_description="Telemetry aggregation pipeline",
        units_required=10.0,
        strategy=BiddingStrategy.COST_FIRST,
    )
    competition = arbitrage_engine.solicit_quotes(req)

    agent_before = policy_engine.get_agent("agent-devops")
    balance_before = agent_before.wallet_balance
    initial_savings = arbitrage_engine.get_total_arbitrage_saved()

    # 2. Execute winning bid
    exec_req = ArbitrageExecutionRequest(bidding_id=competition.bidding_id)
    record = await arbitrage_engine.execute_winning_bid(exec_req)

    assert record.bidding_id == competition.bidding_id
    assert record.amount_paid == competition.winning_quote.total_price
    assert record.arbitrage_saved == competition.arbitrage_saved_amount
    assert record.paypal_status in ["COMPLETED", "CREATED"]

    # 3. Verify balance deducted
    agent_after = policy_engine.get_agent("agent-devops")
    assert agent_after.wallet_balance == round(balance_before - competition.winning_quote.total_price, 2)

    # 4. Verify cumulative savings increased
    assert arbitrage_engine.get_total_arbitrage_saved() == round(initial_savings + competition.arbitrage_saved_amount, 2)


def test_rebalance_portfolio_liquidity():
    devops = policy_engine.get_agent("agent-devops")
    research = policy_engine.get_agent("agent-research")

    devops_budget_before = devops.policy.daily_budget
    research_budget_before = research.policy.daily_budget

    req = LiquidityRebalanceRequest(
        from_agent_id="agent-devops",
        to_agent_id="agent-research",
        amount=30.0,
        reason="Nocturnal model training requires overflow compute liquidity",
    )
    res = arbitrage_engine.rebalance_portfolio_liquidity(req)

    assert res.amount_rebalanced == 30.0
    assert devops.policy.daily_budget == round(devops_budget_before - 30.0, 2)
    assert research.policy.daily_budget == round(research_budget_before + 30.0, 2)


def test_arbitrage_api_endpoints():
    # 1. Market rates
    rates_res = client.get("/api/v1/arbitrage/rates")
    assert rates_res.status_code == 200
    assert "spot_board" in rates_res.json()

    # 2. Solicit quotes
    solicit_payload = {
        "requesting_agent_id": "agent-devops",
        "workload_type": "gpu_inference",
        "workload_description": "API Test GPU cluster solicitation",
        "units_required": 2.5,
        "strategy": "COST_FIRST",
    }
    solicit_res = client.post("/api/v1/arbitrage/bids/solicit", json=solicit_payload)
    assert solicit_res.status_code == 200
    bidding_data = solicit_res.json()
    assert "bidding_id" in bidding_data
    assert "winning_quote" in bidding_data

    # 3. Execute winning quote via API
    exec_payload = {"bidding_id": bidding_data["bidding_id"]}
    exec_res = client.post("/api/v1/arbitrage/bids/execute", json=exec_payload)
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert exec_data["bidding_id"] == bidding_data["bidding_id"]
    assert "paypal_order_id" in exec_data

    # 4. History endpoint
    hist_res = client.get("/api/v1/arbitrage/history")
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert hist_data["total_executions_count"] >= 1
    assert hist_data["total_arbitrage_saved"] > 0

    # 5. Liquidity rebalance endpoint
    reb_payload = {
        "from_agent_id": "agent-payout",
        "to_agent_id": "agent-devops",
        "amount": 25.0,
        "reason": "Reallocating contractor reserve for peak cloud load",
    }
    reb_res = client.post("/api/v1/arbitrage/rebalance", json=reb_payload)
    assert reb_res.status_code == 200
    assert reb_res.json()["amount_rebalanced"] == 25.0

    # 6. CFO Copilot recognizes arbitrage
    cfo_res = client.post("/api/v1/stats/cfo-query", json={"question": "Spot arbitraj tasarrufu nedir?"})
    assert cfo_res.status_code == 200
    assert "Spot Arbitraj Motoru" in cfo_res.json()["answer"]
