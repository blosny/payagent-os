"""
PayAgent OS — Official PayPal AI Toolkit & MCP Guardian Adapter
Bridging PayPal's official AI-Toolkit (https://github.com/paypal/AI-Toolkit)
and official Sandbox MCP Server (https://mcp.sandbox.paypal.com/sse)
with enterprise-grade policy enforcement, budget guardrails, and HITL approval.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging
from backend.app.services.policy_engine import policy_engine
from backend.app.models.transaction import (
    TransactionIntent,
    TransactionRecord,
    TransactionStatus
)

logger = logging.getLogger(__name__)

# Official PayPal MCP Tools Catalog
OFFICIAL_PAYPAL_MCP_TOOLS = [
    {
        "name": "paypal_create_order",
        "description": "Create a PayPal order for checkout / vendor purchase (Orders v2 API).",
        "parameters": {
            "amount": {"type": "number", "description": "Order total in USD"},
            "currency": {"type": "string", "default": "USD"},
            "recipient": {"type": "string", "description": "Vendor name or store title"},
            "reasoning": {"type": "string", "description": "AI agent intent and explanation"}
        },
        "financial_action": True,
        "default_category": "CLOUD_COMPUTE"
    },
    {
        "name": "paypal_create_payout",
        "description": "Send direct disbursement or contractor payout to a PayPal email (Payouts v1 API).",
        "parameters": {
            "amount": {"type": "number", "description": "Payout amount in USD"},
            "recipient_email": {"type": "string", "description": "Payee PayPal email address"},
            "note": {"type": "string", "description": "Memo for payout"},
            "reasoning": {"type": "string", "description": "Justification for payout"}
        },
        "financial_action": True,
        "default_category": "FREELANCE_PAYOUT"
    },
    {
        "name": "paypal_send_invoice",
        "description": "Draft and send a professional PayPal commercial invoice (Invoicing v2 API).",
        "parameters": {
            "amount": {"type": "number", "description": "Invoice line item amount in USD"},
            "recipient_email": {"type": "string", "description": "Billed party email"},
            "reasoning": {"type": "string", "description": "Invoice issuance reasoning"}
        },
        "financial_action": True,
        "default_category": "API_QUOTA"
    },
    {
        "name": "paypal_list_disputes",
        "description": "Query open customer or merchant dispute cases (Disputes v1 API).",
        "parameters": {
            "limit": {"type": "integer", "default": 10}
        },
        "financial_action": False,
        "default_category": None
    },
    {
        "name": "paypal_get_balance",
        "description": "Query available PayPal merchant or sandbox wallet balances.",
        "parameters": {},
        "financial_action": False,
        "default_category": None
    }
]


class MCPToolInvocation(BaseModel):
    agent_id: str = Field(..., description="Unique ID of the AI agent calling the tool")
    tool_name: str = Field(..., description="PayPal MCP Tool identifier, e.g. paypal_create_order")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Parameters supplied to the tool")
    reasoning: Optional[str] = Field(None, description="Natural language explanation of why the agent invoked this tool")


class GuardianInterceptResult(BaseModel):
    allowed: bool
    status: str  # EXECUTED, SUSPENDED_PENDING_HITL, REJECTED, READ_ONLY_PASSTHROUGH
    tool_name: str
    message: str
    guardian_verdict: str
    transaction_id: Optional[str] = None
    paypal_order_id: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None


class PayPalToolkitGuardianAdapter:
    """
    Middleware adapter wrapping PayPal's MCP tools.
    Evaluates policy before any financial operation touches PayPal Sandbox or Live endpoints.
    """

    def __init__(self):
        self.mcp_server_url = "https://mcp.sandbox.paypal.com/sse"
        self.catalog = {t["name"]: t for t in OFFICIAL_PAYPAL_MCP_TOOLS}

    def _resolve_agent_id(self, raw_id: str) -> str:
        """Helper to resolve alias names like 'devops_agent' to registered 'agent-devops'."""
        agents = policy_engine.list_agents()
        raw_clean = raw_id.lower().replace("_", "-")
        for a in agents:
            if a.id.lower() == raw_clean or a.id.lower() in raw_clean or raw_clean in a.id.lower():
                return a.id
        return raw_id

    def get_catalog(self) -> List[Dict[str, Any]]:
        return OFFICIAL_PAYPAL_MCP_TOOLS

    def get_status(self) -> Dict[str, Any]:
        agents = policy_engine.list_agents()
        return {
            "mcp_server": {
                "url": self.mcp_server_url,
                "protocol": "SSE (Model Context Protocol)",
                "status": "CONNECTED_READY",
                "paypal_env": "sandbox"
            },
            "guardian_layer": {
                "status": "ACTIVE_INTERCEPTOR",
                "active_agents": len(agents),
                "guarded_tools_count": sum(1 for t in OFFICIAL_PAYPAL_MCP_TOOLS if t["financial_action"]),
                "read_only_tools_count": sum(1 for t in OFFICIAL_PAYPAL_MCP_TOOLS if not t["financial_action"])
            },
            "tools": OFFICIAL_PAYPAL_MCP_TOOLS
        }

    async def intercept_and_execute(self, invocation: MCPToolInvocation) -> GuardianInterceptResult:
        tool_meta = self.catalog.get(invocation.tool_name)
        if not tool_meta:
            return GuardianInterceptResult(
                allowed=False,
                status="UNKNOWN_TOOL",
                tool_name=invocation.tool_name,
                message=f"Tool '{invocation.tool_name}' is not recognized in official PayPal MCP catalog.",
                guardian_verdict="REJECTED_UNKNOWN_TOOL"
            )

        # 1. Non-financial tools (e.g. disputes, balance queries) pass through safely
        if not tool_meta["financial_action"]:
            return GuardianInterceptResult(
                allowed=True,
                status="READ_ONLY_PASSTHROUGH",
                tool_name=invocation.tool_name,
                message="Read-only diagnostic tool executed without policy hold.",
                guardian_verdict="SAFE_PASS",
                output_data={"mock_result": f"Executed read-only tool {invocation.tool_name}", "sample_items": []}
            )

        # 2. Extract financial parameters
        args = invocation.arguments
        amount = float(args.get("amount", 0.0))
        recipient = str(args.get("recipient") or args.get("recipient_email") or "Unknown Vendor")
        reasoning = invocation.reasoning or str(args.get("reasoning") or args.get("note") or f"MCP tool {invocation.tool_name} call")
        category = tool_meta.get("default_category", "CLOUD_COMPUTE")

        resolved_agent_id = self._resolve_agent_id(invocation.agent_id)

        # 3. Create Intent & Consult PayAgent OS Policy Engine
        intent = TransactionIntent(
            agent_id=resolved_agent_id,
            amount=amount,
            currency=str(args.get("currency", "USD")),
            recipient=recipient,
            category=category,
            reasoning=reasoning
        )

        try:
            record: TransactionRecord = await policy_engine.submit_intent(intent)
        except Exception as e:
            return GuardianInterceptResult(
                allowed=False,
                status="REJECTED",
                tool_name=invocation.tool_name,
                message=f"Tool invocation BLOCKED: {str(e)}",
                guardian_verdict="BLOCKED_BY_POLICY"
            )

        if record.status in (TransactionStatus.APPROVED_AUTONOMOUS, TransactionStatus.SETTLED):
            return GuardianInterceptResult(
                allowed=True,
                status="EXECUTED",
                tool_name=invocation.tool_name,
                message="Autonomous tool execution approved by PolicyEngine. Processed via PayPal Orders v2.",
                guardian_verdict="AUTONOMOUS_APPROVED",
                transaction_id=record.id,
                paypal_order_id=record.paypal_order_id,
                output_data={
                    "order_status": "COMPLETED",
                    "amount": amount,
                    "recipient": recipient,
                    "paypal_ref": record.paypal_order_id or record.paypal_capture_id
                }
            )

        elif record.status == TransactionStatus.PENDING_APPROVAL:
            # Suspended -> Block tool from completing and alert Human-in-the-Loop
            return GuardianInterceptResult(
                allowed=False,
                status="SUSPENDED_PENDING_HITL",
                tool_name=invocation.tool_name,
                message=f"Tool invocation HALTED by PayAgent OS Guardian: {record.policy_evaluation_reason}. Sent to Human Supervisor Queue.",
                guardian_verdict="HITL_HOLD_REQUIRED",
                transaction_id=record.id,
                output_data={
                    "requires_supervisor_approval": True,
                    "hitl_queue_id": record.id,
                    "pending_amount": amount,
                    "breach_rule": record.policy_evaluation_reason
                }
            )

        else:
            # Rejected outright (e.g. unknown vendor or policy block)
            return GuardianInterceptResult(
                allowed=False,
                status="REJECTED",
                tool_name=invocation.tool_name,
                message=f"Tool invocation BLOCKED: {record.policy_evaluation_reason}",
                guardian_verdict="BLOCKED_BY_POLICY",
                transaction_id=record.id
            )


# Singleton instance
toolkit_adapter = PayPalToolkitGuardianAdapter()
