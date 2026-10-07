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
