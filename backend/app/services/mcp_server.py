import json
import logging
from typing import List, Dict, Any, Optional

from ..models.mcp import (
    MCPTool,
    MCPContentItem,
    MCPCallToolResult,
    MCPJsonRpcRequest,
    MCPJsonRpcResponse,
)
from ..models.transaction import TransactionIntent
from .policy_engine import policy_engine
from .security_engine import llm_risk_analyzer

logger = logging.getLogger(__name__)


class MCPServer:
    """Official PayPal Model Context Protocol (MCP) Wallet & Governance Server.
    Provides standardized tools for Cursor, Claude Desktop, AutoGen, and LangChain agents
    to inspect budgets, evaluate spending policies, and execute PayPal transactions safely."""

    def __init__(self):
        self._tools = self._build_tools_manifest()

    def _build_tools_manifest(self) -> List[MCPTool]:
        return [
            MCPTool(
                name="payagent_request_funds",
                description="Autonomous payment and disbursement request governed by PayAgent OS enterprise guardrails and PayPal Sandbox REST API.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "ID of the calling autonomous AI agent (e.g. agent-devops, agent-research).",
                        },
                        "amount": {
                            "type": "number",
                            "description": "Amount in USD requested for transaction.",
                        },
                        "recipient": {
                            "type": "string",
                            "description": "Vendor name (e.g. 'AWS', 'RunPod') or freelancer PayPal email.",
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Explainable AI natural language justification for the expenditure.",
                        },
                        "category": {
                            "type": "string",
                            "default": "CLOUD_COMPUTE",
                            "description": "Expense category (CLOUD_COMPUTE, API_QUOTA, DATASET, FREELANCE).",
                        },
                    },
                    "required": ["agent_id", "amount", "recipient", "reasoning"],
                },
            ),
            MCPTool(
                name="payagent_check_budget",
                description="Check an agent's available wallet balance, daily budget cap, spent today, and remaining headroom.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "ID of the autonomous AI agent.",
                        }
                    },
                    "required": ["agent_id"],
                },
            ),
            MCPTool(
                name="payagent_get_policy",
                description="Inspect an agent's spending rules: single transaction ceiling, pre-approved vendor whitelist, and auto-approval status.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "ID of the autonomous AI agent.",
                        }
                    },
                    "required": ["agent_id"],
                },
            ),
            MCPTool(
                name="payagent_list_agents",
                description="List all active autonomous AI agents operating within the corporate PayAgent OS fleet.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            MCPTool(
                name="payagent_scan_risk",
                description="Run real-time PayPal AI Guardrails & Prompt Injection analysis on a proposed task reasoning without financial commitment.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "reasoning": {
                            "type": "string",
                            "description": "AI's prompt / reasoning to scan.",
                        },
                        "amount": {
                            "type": "number",
                            "description": "Target amount in USD.",
                        },
                        "vendor": {
                            "type": "string",
                            "description": "Target vendor or beneficiary name.",
                        },
                    },
                    "required": ["reasoning", "amount", "vendor"],
                },
            ),
        ]

    def get_tools(self) -> List[MCPTool]:
        return self._tools

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> MCPCallToolResult:
        try:
            if name == "payagent_request_funds":
                intent = TransactionIntent(
                    agent_id=arguments.get("agent_id", "agent-devops"),
                    amount=float(arguments.get("amount", 0.0)),
                    recipient=arguments.get("recipient", "Unknown"),
                    reasoning=arguments.get("reasoning", "Autonomous compute task"),
                    category=arguments.get("category", "CLOUD_COMPUTE"),
                    currency="USD",
                )
                tx = await policy_engine.submit_intent(intent)
                result_payload = {
                    "transaction_id": tx.id,
                    "status": tx.status.value,
                    "amount": tx.amount,
                    "currency": tx.currency,
                    "recipient": tx.recipient,
                    "policy_reason": tx.policy_evaluation_reason,
                    "paypal_order_id": tx.paypal_order_id,
                    "paypal_capture_id": tx.paypal_capture_id,
                    "risk_score": tx.risk_score,
                }
                return MCPCallToolResult(
                    content=[MCPContentItem(text=json.dumps(result_payload, indent=2))],
                    isError=False,
                )

            elif name == "payagent_check_budget":
                agent_id = arguments.get("agent_id")
                agent = policy_engine.get_agent(agent_id)
                if not agent:
                    return MCPCallToolResult(
                        content=[MCPContentItem(text=f"Error: Agent '{agent_id}' not found.")],
                        isError=True,
                    )
                remaining_daily = max(0.0, agent.policy.daily_budget - agent.spent_today)
                budget_info = {
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "wallet_balance": agent.wallet_balance,
                    "daily_budget_limit": agent.policy.daily_budget,
                    "spent_today": agent.spent_today,
                    "remaining_daily_headroom": round(remaining_daily, 2),
                    "currency": agent.currency,
                    "is_active": agent.is_active,
                }
                return MCPCallToolResult(
                    content=[MCPContentItem(text=json.dumps(budget_info, indent=2))],
                    isError=False,
                )

            elif name == "payagent_get_policy":
                agent_id = arguments.get("agent_id")
                agent = policy_engine.get_agent(agent_id)
                if not agent:
                    return MCPCallToolResult(
                        content=[MCPContentItem(text=f"Error: Agent '{agent_id}' not found.")],
                        isError=True,
                    )
                policy_info = {
                    "agent_id": agent.id,
                    "max_per_transaction": agent.policy.max_per_transaction,
                    "daily_budget": agent.policy.daily_budget,
                    "allowed_vendors": agent.policy.allowed_vendors,
                    "allow_unlisted_vendors": agent.policy.allow_unlisted_vendors,
                    "auto_approval_enabled": agent.policy.auto_approval_enabled,
                    "personality": agent.personality.value,
                }
                return MCPCallToolResult(
                    content=[MCPContentItem(text=json.dumps(policy_info, indent=2))],
                    isError=False,
                )

            elif name == "payagent_list_agents":
                agents = policy_engine.list_agents()
                summary = [
                    {
                        "id": a.id,
                        "name": a.name,
                        "balance": a.wallet_balance,
                        "spent_today": a.spent_today,
                        "personality": a.personality.value,
                    }
                    for a in agents
                ]
                return MCPCallToolResult(
                    content=[MCPContentItem(text=json.dumps(summary, indent=2))],
                    isError=False,
                )

            elif name == "payagent_scan_risk":
                reasoning = arguments.get("reasoning", "")
                amount = float(arguments.get("amount", 0.0))
                vendor = arguments.get("vendor", "")
                risk = llm_risk_analyzer.analyze(reasoning=reasoning, amount=amount, vendor=vendor)
                return MCPCallToolResult(
                    content=[MCPContentItem(text=json.dumps(risk.model_dump(), indent=2))],
                    isError=False,
                )

            else:
                return MCPCallToolResult(
                    content=[MCPContentItem(text=f"Unknown tool: '{name}'")],
                    isError=True,
                )

        except Exception as e:
            logger.error(f"MCP tool execution failed for '{name}': {e}")
            return MCPCallToolResult(
                content=[MCPContentItem(text=f"Execution error: {str(e)}")],
                isError=True,
            )

    async def handle_jsonrpc(self, request: MCPJsonRpcRequest) -> MCPJsonRpcResponse:
        req_id = request.id
        method = request.method

        if method == "initialize":
            return MCPJsonRpcResponse(
                id=req_id,
                result={
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "payagent-os-mcp-server",
                        "version": "1.0.0",
                        "description": "Official PayPal AI Model Context Protocol Server for PayAgent OS",
                    },
                    "capabilities": {
                        "tools": {"listChanged": False},
                    },
                },
            )

        elif method == "tools/list":
            tools_manifest = [
                {
                    "name": t.name,
                    "description": t.description,
                    "inputSchema": t.inputSchema,
                }
                for t in self.get_tools()
            ]
            return MCPJsonRpcResponse(id=req_id, result={"tools": tools_manifest})

        elif method == "tools/call":
            params = request.params or {}
            name = params.get("name")
            arguments = params.get("arguments", {})
            call_res = await self.call_tool(name=name, arguments=arguments)
            return MCPJsonRpcResponse(
                id=req_id,
                result={
                    "content": [c.model_dump() for c in call_res.content],
                    "isError": call_res.isError,
                },
            )

        elif method == "ping":
            return MCPJsonRpcResponse(id=req_id, result={})

        else:
            return MCPJsonRpcResponse(
                id=req_id,
                error={
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
            )


mcp_server = MCPServer()
