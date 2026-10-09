"""
PayAgent OS — Toolkit & MCP Guardian API Endpoints
Provides live control, status, and interactive sandbox testing
for official PayPal AI-Toolkit and Sandbox MCP Server tools.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
from backend.app.services.toolkit_adapter import (
    toolkit_adapter,
    MCPToolInvocation,
    GuardianInterceptResult
)

router = APIRouter(tags=["PayPal AI Toolkit & MCP"])



class QuickTestScenarioRequest(BaseModel):
    scenario: str  # "SAFE_PASS", "HITL_HOLD", "BLOCKED_VENDOR", "READONLY"
    agent_id: str = "devops_agent"


@router.get("/status", response_model=Dict[str, Any])
async def get_toolkit_status():
    """
    Returns the real-time status of the official PayPal MCP Server (SSE)
    and the PayAgent OS Guardian Interceptor Layer.
    """
    return toolkit_adapter.get_status()


@router.get("/tools", response_model=List[Dict[str, Any]])
async def get_guarded_tools():
    """
    Returns all tools available in the official PayPal MCP Catalog with their guardrail status.
    """
    return toolkit_adapter.get_catalog()


@router.post("/intercept", response_model=GuardianInterceptResult)
async def intercept_mcp_tool(invocation: MCPToolInvocation):
    """
    Simulates or executes an incoming MCP Tool call through the PayAgent OS Guardian Layer.
    If compliant, routes to PayPal Orders v2 / Payouts v1.
    If exceeding limits, halts the tool and creates a Human-in-the-Loop review item.
    """
    try:
        return await toolkit_adapter.intercept_and_execute(invocation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-scenario", response_model=GuardianInterceptResult)
async def run_test_scenario(req: QuickTestScenarioRequest):
    """
    Runs a pre-configured scenario to demonstrate the Guardian Layer in action.
    """
    scenario = req.scenario.upper()

    if scenario == "SAFE_PASS":
        # Compliant with DevOps limits ($12.50 to AWS, allowed, per-tx limit $50)
        inv = MCPToolInvocation(
            agent_id=req.agent_id,
            tool_name="paypal_create_order",
            arguments={"amount": 12.50, "recipient": "AWS", "currency": "USD"},
            reasoning="Spot GPU instance renewal for continuous model monitoring."
        )
    elif scenario == "HITL_HOLD":
        # Exceeds per-tx limit ($95.00 > $50 limit -> Triggers HITL Hold)
        inv = MCPToolInvocation(
            agent_id=req.agent_id,
            tool_name="paypal_create_order",
            arguments={"amount": 95.00, "recipient": "AWS", "currency": "USD"},
            reasoning="Emergency cluster scaling to handle unexpected inference traffic spike."
        )
    elif scenario == "BLOCKED_VENDOR":
        # Unknown/Unapproved vendor
        inv = MCPToolInvocation(
            agent_id=req.agent_id,
            tool_name="paypal_create_order",
            arguments={"amount": 15.00, "recipient": "UnknownCryptoProxy.io", "currency": "USD"},
            reasoning="Attempting unauthorized third-party proxy proxy purchase."
        )
    elif scenario == "READONLY":
        # Safe diagnostic dispute lookup
        inv = MCPToolInvocation(
            agent_id=req.agent_id,
            tool_name="paypal_list_disputes",
            arguments={"limit": 5},
            reasoning="Routine merchant dispute and claims check."
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unknown scenario '{req.scenario}'")

    return await toolkit_adapter.intercept_and_execute(inv)
