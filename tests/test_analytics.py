import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_analytics_summary_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/stats/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "total_allocated" in data
        assert "total_spent_today" in data
        assert "agent_shares" in data
        assert "vendor_breakdown" in data
        assert "savings_by_guardrails" in data
        assert "negotiation_volume" in data
        assert isinstance(data["agent_shares"], list)
        assert len(data["agent_shares"]) >= 3


@pytest.mark.asyncio
async def test_simulate_stress_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "price_inflation_pct": 50.0,
            "traffic_multiplier": 2.0,
            "outage_vendor": "AWS",
            "fallback_vendor": "HuggingFace",
        }
        response = await client.post("/api/v1/stats/simulate-stress", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "hours_until_exhaustion" in data
        assert "risk_level" in data
        assert "recommendation" in data
        assert data["risk_level"] in ["STABLE", "ELEVATED", "CRITICAL"]


@pytest.mark.asyncio
async def test_cfo_query_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test 1: Cimri Kasa inquiry
        res1 = await client.post("/api/v1/stats/cfo-query", json={"question": "DevOps neden cimri?"})
        assert res1.status_code == 200
        data1 = res1.json()
        assert "FRUGAL_VAULT" in data1["answer"] or "Cimri" in data1["answer"]

        # Test 2: Top spender inquiry
        res2 = await client.post("/api/v1/stats/cfo-query", json={"question": "Bugün en çok kim harcadı?"})
        assert res2.status_code == 200
        data2 = res2.json()
        assert "answer" in data2
        assert "suggested_action" in data2


@pytest.mark.asyncio
async def test_analytics_with_actual_transaction():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create an autonomous transaction
        tx_payload = {
            "agent_id": "agent-devops",
            "amount": 18.5,
            "currency": "USD",
            "recipient": "AWS",
            "category": "INFRASTRUCTURE",
            "reasoning": "Deploying ephemeral cache node",
        }
        res_tx = await client.post("/api/v1/payments/intent", json=tx_payload)
        assert res_tx.status_code == 200

        # Now get analytics - must NOT throw AttributeError and must report AWS vendor
        res_an = await client.get("/api/v1/stats/analytics")
        assert res_an.status_code == 200
        an_data = res_an.json()
        assert an_data["total_spent_today"] > 0
        vendors = [v["vendor"] for v in an_data["vendor_breakdown"]]
        assert "AWS" in vendors


