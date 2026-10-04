import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from ..models.agent import Agent, AgentCreate, AgentPolicy
from ..models.transaction import (
    TransactionIntent,
    TransactionRecord,
    TransactionStatus,
    TransactionType,
)
from .paypal_service import paypal_service


class PolicyEngine:
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._transactions: Dict[str, TransactionRecord] = {}
        self._seed_default_agents()

    def _seed_default_agents(self):
        """Seeds initial realistic agents for instant demo and evaluation."""
        defaults = [
            (
                "agent-devops",
                "DevOps Infrastructure Agent",
                "Manages cloud compute, GPU clusters, and server resource scaling.",
                1200.0,
                AgentPolicy(
                    max_per_transaction=40.0,
                    daily_budget=200.0,
                    allowed_vendors=["AWS", "Cloudflare", "GitHub", "DigitalOcean", "HuggingFace"],
                    allow_unlisted_vendors=False,
                ),
            ),
            (
                "agent-research",
                "Market Research & Data Agent",
                "Procures paid scientific datasets, API query tokens, and industry reports.",
                600.0,
                AgentPolicy(
                    max_per_transaction=25.0,
                    daily_budget=100.0,
                    allowed_vendors=["OpenAI", "Anthropic", "Statista", "Kaggle", "arXiv"],
                    allow_unlisted_vendors=False,
                ),
            ),
            (
                "agent-payout",
                "Freelance Contractor Coordinator",
                "Disburses micro-rewards and milestone payments to vetted external talent.",
                1500.0,
                AgentPolicy(
                    max_per_transaction=50.0,
                    daily_budget=300.0,
                    allowed_vendors=[],
                    allow_unlisted_vendors=True,
                ),
            ),
        ]

        for aid, name, desc, balance, policy in defaults:
            self._agents[aid] = Agent(
                id=aid,
                name=name,
                description=desc,
                wallet_balance=balance,
                spent_today=0.0,
                currency="USD",
                policy=policy,
            )

    def list_agents(self) -> List[Agent]:
        return list(self._agents.values())

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self._agents.get(agent_id)

    def create_agent(self, data: AgentCreate) -> Agent:
        agent_id = f"agent-{uuid.uuid4().hex[:6]}"
        policy = data.policy or AgentPolicy()
        agent = Agent(
            id=agent_id,
            name=data.name,
            description=data.description,
            wallet_balance=data.wallet_balance,
            spent_today=0.0,
            currency=data.currency,
            policy=policy,
        )
        self._agents[agent_id] = agent
        return agent

    def list_transactions(self, status: Optional[TransactionStatus] = None) -> List[TransactionRecord]:
        txs = list(self._transactions.values())
        if status:
            txs = [t for t in txs if t.status == status]
        return sorted(txs, key=lambda x: x.created_at, reverse=True)

    def get_transaction(self, tx_id: str) -> Optional[TransactionRecord]:
        return self._transactions.get(tx_id)

    def evaluate_policy(self, agent: Agent, intent: TransactionIntent) -> Tuple[bool, str]:
        """Evaluates whether an intent can execute autonomously or must wait for human approval."""
        if not agent.is_active:
            return False, "Agent is currently disabled."

        if intent.amount > agent.wallet_balance:
            return False, f"Insufficient wallet balance. Required: ${intent.amount:.2f}, Available: ${agent.wallet_balance:.2f}."

        policy = agent.policy
        if not policy.auto_approval_enabled:
            return False, "Autonomous auto-approval is disabled for this agent."

        # Check vendor allowlist
        if not policy.allow_unlisted_vendors:
            vendor_match = any(
                allowed.lower() in intent.recipient.lower()
                for allowed in policy.allowed_vendors
            )
            if not vendor_match:
                return False, f"Vendor '{intent.recipient}' is not on the agent's pre-approved allowlist."

        # Check single transaction limit
        if intent.amount > policy.max_per_transaction:
            return False, f"Amount ${intent.amount:.2f} exceeds single transaction limit (${policy.max_per_transaction:.2f})."

        # Check rolling daily budget
        if (agent.spent_today + intent.amount) > policy.daily_budget:
            return False, f"Transaction causes daily spending (${agent.spent_today + intent.amount:.2f}) to exceed daily budget (${policy.daily_budget:.2f})."

        return True, "Within all autonomous policy limits."

    async def submit_intent(self, intent: TransactionIntent) -> TransactionRecord:
        """Processes an incoming payment intent from an autonomous AI agent."""
        agent = self.get_agent(intent.agent_id)
        if not agent:
            raise ValueError(f"Agent with ID '{intent.agent_id}' not found.")

        can_auto_execute, reason = self.evaluate_policy(agent, intent)
        tx_id = f"TX-{uuid.uuid4().hex[:8].upper()}"

        tx_type = TransactionType.PAYPAL_PAYOUT if "@" in intent.recipient else TransactionType.PAYPAL_ORDER

        if can_auto_execute:
            # Autonomous execution via PayPal API
            if tx_type == TransactionType.PAYPAL_ORDER:
                order_res = await paypal_service.create_order(
                    amount=intent.amount,
                    currency=intent.currency,
                    description=f"PayAgent OS: {intent.reasoning[:100]}",
                    reference_id=tx_id,
                )
                order_id = order_res.get("id")
                capture_res = await paypal_service.capture_order(order_id)
                capture_id = None
                try:
                    capture_id = capture_res["purchase_units"][0]["payments"]["captures"][0]["id"]
                except (KeyError, IndexError):
                    pass

                record = TransactionRecord(
                    id=tx_id,
                    agent_id=agent.id,
                    agent_name=agent.name,
                    amount=intent.amount,
                    currency=intent.currency,
                    recipient=intent.recipient,
                    category=intent.category,
                    reasoning=intent.reasoning,
                    policy_evaluation_reason=reason,
                    status=TransactionStatus.APPROVED_AUTONOMOUS,
                    transaction_type=tx_type,
                    paypal_order_id=order_id,
                    paypal_capture_id=capture_id,
                    resolved_at=datetime.now(timezone.utc),
                )
            else:
                payout_res = await paypal_service.create_payout(
                    recipient_email=intent.recipient,
                    amount=intent.amount,
                    currency=intent.currency,
                    note=intent.reasoning,
                )
                batch_id = payout_res.get("batch_header", {}).get("payout_batch_id")
                record = TransactionRecord(
                    id=tx_id,
                    agent_id=agent.id,
                    agent_name=agent.name,
                    amount=intent.amount,
                    currency=intent.currency,
                    recipient=intent.recipient,
                    category=intent.category,
                    reasoning=intent.reasoning,
                    policy_evaluation_reason=reason,
                    status=TransactionStatus.APPROVED_AUTONOMOUS,
                    transaction_type=tx_type,
                    paypal_payout_batch_id=batch_id,
                    resolved_at=datetime.now(timezone.utc),
                )

            # Deduct balance and increment daily spending
            agent.wallet_balance -= intent.amount
            agent.spent_today += intent.amount

        else:
            # Requires Human-in-the-Loop approval
            record = TransactionRecord(
                id=tx_id,
                agent_id=agent.id,
                agent_name=agent.name,
                amount=intent.amount,
                currency=intent.currency,
                recipient=intent.recipient,
                category=intent.category,
                reasoning=intent.reasoning,
                policy_evaluation_reason=reason,
                status=TransactionStatus.PENDING_APPROVAL,
                transaction_type=tx_type,
            )

        self._transactions[tx_id] = record
        return record

    async def resolve_pending_transaction(
        self, tx_id: str, decision: str, reviewer_notes: Optional[str] = None
    ) -> TransactionRecord:
        """Human Supervisor approves or rejects a pending transaction."""
        tx = self.get_transaction(tx_id)
        if not tx:
            raise ValueError(f"Transaction '{tx_id}' not found.")
        if tx.status != TransactionStatus.PENDING_APPROVAL:
            raise ValueError(f"Transaction '{tx_id}' is not in PENDING_APPROVAL state.")

        agent = self.get_agent(tx.agent_id)
        decision_upper = decision.upper()

        if decision_upper == "APPROVE":
            if agent:
                if tx.amount > agent.wallet_balance:
                    raise ValueError("Agent has insufficient balance to approve this transaction.")
                agent.wallet_balance -= tx.amount
                agent.spent_today += tx.amount

            # Execute via PayPal
            if tx.transaction_type == TransactionType.PAYPAL_ORDER:
                order_res = await paypal_service.create_order(
                    amount=tx.amount,
                    currency=tx.currency,
                    description=f"PayAgent Approved: {tx.reasoning[:100]}",
                    reference_id=tx.id,
                )
                order_id = order_res.get("id")
                capture_res = await paypal_service.capture_order(order_id)
                capture_id = None
                try:
                    capture_id = capture_res["purchase_units"][0]["payments"]["captures"][0]["id"]
                except (KeyError, IndexError):
                    pass
                tx.paypal_order_id = order_id
                tx.paypal_capture_id = capture_id
            else:
                payout_res = await paypal_service.create_payout(
                    recipient_email=tx.recipient,
                    amount=tx.amount,
                    currency=tx.currency,
                    note=tx.reasoning,
                )
                tx.paypal_payout_batch_id = payout_res.get("batch_header", {}).get("payout_batch_id")

            tx.status = TransactionStatus.APPROVED_BY_HUMAN
        elif decision_upper == "REJECT":
            tx.status = TransactionStatus.REJECTED_BY_HUMAN
        else:
            raise ValueError("Decision must be either 'APPROVE' or 'REJECT'.")

        tx.reviewer_notes = reviewer_notes
        tx.resolved_at = datetime.now(timezone.utc)
        return tx


policy_engine = PolicyEngine()
