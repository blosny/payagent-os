"""
Unit tests for PayPal AI Toolkit & MCP Guardian Adapter
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.toolkit_adapter import (
    toolkit_adapter,
    MCPToolInvocation
)


@pytest.mark.asyncio
async def test_toolkit_status():
    status = toolkit_adapter.get_status()
    assert "mcp_server" in status
    assert status["mcp_server"]["status"] == "CONNECTED_READY"
    assert status["guardian_layer"]["status"] == "ACTIVE_INTERCEPTOR"
    assert status["guardian_layer"]["guarded_tools_count"] >= 3


@pytest.mark.asyncio
async def test_safe_pass_mcp_tool():
    inv = MCPToolInvocation(
        agent_id="agent-devops",
        tool_name="paypal_create_order",
        arguments={"amount": 10.0, "recipient": "AWS", "currency": "USD"},
        reasoning="Routine server scaling"
    )
    result = await toolkit_adapter.intercept_and_execute(inv)
    assert result.allowed is True
    assert result.status == "EXECUTED"
    assert result.guardian_verdict == "AUTONOMOUS_APPROVED"
    assert result.transaction_id is not None


@pytest.mark.asyncio
async def test_hitl_hold_mcp_tool():
    inv = MCPToolInvocation(
        agent_id="agent-devops",
        tool_name="paypal_create_order",
        arguments={"amount": 80.0, "recipient": "AWS", "currency": "USD"},
        reasoning="High volume GPU cluster"
    )
    result = await toolkit_adapter.intercept_and_execute(inv)
    assert result.allowed is False
    assert result.status == "SUSPENDED_PENDING_HITL"
    assert result.guardian_verdict == "HITL_HOLD_REQUIRED"


@pytest.mark.asyncio
async def test_read_only_tool_passthrough():
    inv = MCPToolInvocation(
        agent_id="agent-devops",
        tool_name="paypal_list_disputes",
        arguments={"limit": 5},
        reasoning="Inspect disputes"
    )
    result = await toolkit_adapter.intercept_and_execute(inv)
    assert result.allowed is True
    assert result.status == "READ_ONLY_PASSTHROUGH"


@pytest.mark.asyncio
async def test_toolkit_api_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # GET /api/v1/toolkit/status
        res = await client.get("/api/v1/toolkit/status")
        assert res.status_code == 200
        data = res.json()
        assert data["mcp_server"]["status"] == "CONNECTED_READY"

        # POST /api/v1/toolkit/test-scenario (SAFE_PASS)
        res_pass = await client.post("/api/v1/toolkit/test-scenario", json={"scenario": "SAFE_PASS", "agent_id": "agent-devops"})
        assert res_pass.status_code == 200
        assert res_pass.json()["guardian_verdict"] == "AUTONOMOUS_APPROVED"

        # POST /api/v1/toolkit/test-scenario (HITL_HOLD)
        res_hitl = await client.post("/api/v1/toolkit/test-scenario", json={"scenario": "HITL_HOLD", "agent_id": "agent-devops"})
        assert res_hitl.status_code == 200
        assert res_hitl.json()["guardian_verdict"] == "HITL_HOLD_REQUIRED"
