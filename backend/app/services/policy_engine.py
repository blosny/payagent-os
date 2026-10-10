import uuid
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
from ..models.agent import Agent, AgentCreate, AgentPolicy, AgentPersonality
from ..models.transaction import (
    TransactionIntent,
    TransactionRecord,
    TransactionStatus,
    TransactionType,
)
from ..models.negotiation import NegotiationRequest, NegotiationRecord
from ..models.debt import DebtRecord, DebtStatus, SettlementResult
from .paypal_service import paypal_service


class PolicyEngine:
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._transactions: Dict[str, TransactionRecord] = {}
        self._negotiations: Dict[str, NegotiationRecord] = {}
        self._debts: Dict[str, DebtRecord] = {}
        self._seed_default_agents()


    def _seed_default_agents(self):
        """Seeds initial realistic agents for instant demo and evaluation."""
        defaults = [
            (
                "agent-devops",
                "DevOps Infrastructure Agent",
                "Manages cloud compute, GPU clusters, and server resource scaling.",
                1200.0,
                AgentPersonality.FRUGAL_VAULT,
                "Cimri Birikim Kasası — Acil durum fonudur; sadece CRITICAL arızalarda kota verir.",
                AgentPolicy(
                    max_per_transaction=40.0,
                    daily_budget=200.0,
                    allowed_vendors=["AWS", "Cloudflare", "GitHub", "DigitalOcean", "HuggingFace"],
                    allow_unlisted_vendors=False,
                    min_lending_urgency="CRITICAL",
                ),
            ),
            (
                "agent-research",
                "Market Research & Data Agent",
                "Procures paid scientific datasets, API query tokens, and industry reports.",
                600.0,
                AgentPersonality.GROWTH_EXPLORER,
                "Büyüme & İnovasyon — Yapay zeka modelleri ve araştırma deneyleri için fon arar.",
                AgentPolicy(
                    max_per_transaction=25.0,
                    daily_budget=100.0,
                    allowed_vendors=["OpenAI", "Anthropic", "Statista", "Kaggle", "arXiv"],
                    allow_unlisted_vendors=False,
                    min_lending_urgency="MEDIUM",
                ),
            ),
            (
                "agent-payout",
                "Freelance Contractor Coordinator",
                "Disburses micro-rewards and milestone payments to vetted external talent.",
                1500.0,
                AgentPersonality.BALANCED_COORDINATOR,
                "Dengeli Hazine — Serbest çalışan hakedişleri ve çıktı bazlı rasyonel fon yöneticisi.",
                AgentPolicy(
                    max_per_transaction=50.0,
                    daily_budget=300.0,
                    allowed_vendors=[],
                    allow_unlisted_vendors=True,
                    min_lending_urgency="HIGH",
                ),
            ),
        ]

        for aid, name, desc, balance, personality, pers_desc, policy in defaults:
            self._agents[aid] = Agent(
                id=aid,
                name=name,
                description=desc,
                wallet_balance=balance,
                spent_today=0.0,
                currency="USD",
                personality=personality,
                personality_description=pers_desc,
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
            personality=data.personality,
            personality_description=data.personality_description,
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

        # Check LLM Risk & Guardrail Anomaly
        from .security_engine import llm_risk_analyzer
        risk = llm_risk_analyzer.analyze(intent.reasoning, intent.amount, intent.recipient, agent.id)
        if risk.is_blocked:
            return False, f"Security Risk Blocked: {risk.analysis_summary}"
        if risk.requires_hitl:
            return False, f"Security Anomaly Triggered: {risk.analysis_summary}"
        if risk.requires_multisig:
            return False, f"Enterprise Multi-Sig Required: Expenditure of ${intent.amount:.2f} requires consensus (Threshold: $500.00)."

        return True, "Within all autonomous policy limits."

    async def submit_intent(self, intent: TransactionIntent) -> TransactionRecord:
        """Processes an incoming payment intent from an autonomous AI agent."""
        agent = self.get_agent(intent.agent_id)
        if not agent:
            raise ValueError(f"Agent with ID '{intent.agent_id}' not found.")

        from .security_engine import llm_risk_analyzer
        risk_eval = llm_risk_analyzer.analyze(intent.reasoning, intent.amount, intent.recipient, agent.id)

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
                    risk_score=risk_eval.risk_score,
                    risk_flags=risk_eval.flags,
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
                    risk_score=risk_eval.risk_score,
                    risk_flags=risk_eval.flags,
                    resolved_at=datetime.now(timezone.utc),
                )

            # Deduct balance and increment daily spending
            agent.wallet_balance -= intent.amount
            agent.spent_today += intent.amount

        else:
            # Requires Human-in-the-Loop approval
            # Detect limit or daily budget shortfall and find candidate peer donor
            shortfall = 0.0
            if intent.amount > agent.policy.max_per_transaction:
                shortfall = max(shortfall, intent.amount - agent.policy.max_per_transaction)
            if (agent.spent_today + intent.amount) > agent.policy.daily_budget:
                shortfall = max(shortfall, (agent.spent_today + intent.amount) - agent.policy.daily_budget)

            donor_id = None
            donor_name = None
            proposal_note = None

            if shortfall > 0:
                eligible_donors = [
                    a for a in self._agents.values()
                    if a.id != agent.id and (a.policy.daily_budget - a.spent_today) >= shortfall
                ]
                if eligible_donors:
                    eligible_donors.sort(key=lambda a: (a.policy.daily_budget - a.spent_today), reverse=True)
                    best_donor = eligible_donors[0]
                    headroom = best_donor.policy.daily_budget - best_donor.spent_today
                    donor_id = best_donor.id
                    donor_name = best_donor.name
                    proposal_note = (
                        f"{best_donor.name} cüzdanında ${headroom:.2f} boşta kota mevcut. "
                        f"Süpervizör onayı ile eksik kalan ${shortfall:.2f} bu karttan aktarılacak."
                    )

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
                shortfall_amount=shortfall if shortfall > 0 else None,
                proposed_donor_agent_id=donor_id,
                proposed_donor_agent_name=donor_name,
                borrowing_proposal_note=proposal_note,
                risk_score=risk_eval.risk_score,
                risk_flags=risk_eval.flags,
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
            # If this transaction had an automated peer shortfall transfer, execute the quota reallocation!
            if tx.shortfall_amount and tx.proposed_donor_agent_id:
                donor = self.get_agent(tx.proposed_donor_agent_id)
                if donor:
                    donor.policy.daily_budget -= tx.shortfall_amount
                    if agent:
                        agent.policy.daily_budget += tx.shortfall_amount
                        if agent.policy.max_per_transaction < tx.amount:
                            agent.policy.max_per_transaction = tx.amount

                    neg_id = f"NEG-{uuid.uuid4().hex[:8].upper()}"
                    transcript = (
                        f"[{agent.name if agent else 'Requester'} -> {donor.name}]: \"OpenAI/Vendor harcamasında ${tx.shortfall_amount:.2f} eksik kota tespit edildi. Transfer talep edildi.\"\n"
                        f"[{donor.name} -> {agent.name if agent else 'Requester'}]: \"SÜPERVİZÖR ONAYLADI: ${tx.shortfall_amount:.2f} kota başarıyla aktarıldı. PayPal ödemesi tahsil edildi.\""
                    )
                    neg_record = NegotiationRecord(
                        id=neg_id,
                        requester_agent_id=agent.id if agent else "unknown",
                        requester_name=agent.name if agent else "Unknown Agent",
                        target_agent_id=donor.id,
                        target_name=donor.name,
                        amount=tx.shortfall_amount,
                        currency=tx.currency,
                        justification=f"{tx.recipient} harcaması için eksik bütçe tamamlama",
                        urgency="HIGH",
                        accepted=True,
                        transcript=transcript,
                    )
                    self._negotiations[neg_id] = neg_record

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

    def list_negotiations(self) -> List[NegotiationRecord]:
        """Lists all peer-to-peer agent budget negotiations."""
        return sorted(self._negotiations.values(), key=lambda x: x.created_at, reverse=True)

    def negotiate_budget_transfer(self, req: NegotiationRequest) -> NegotiationRecord:
        """Processes autonomous budget negotiation and quota transfer between two AI agents."""
        requester = self.get_agent(req.requester_agent_id)
        target = self.get_agent(req.target_agent_id)

        if not requester:
            raise ValueError(f"Requester agent '{req.requester_agent_id}' not found.")
        if not target:
            raise ValueError(f"Target agent '{req.target_agent_id}' not found.")
        if requester.id == target.id:
            raise ValueError("An agent cannot negotiate a budget transfer with itself.")

        # Financial personality urgency ranks
        urgency_ranks = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        req_score = urgency_ranks.get(req.urgency.upper(), 2)
        min_threshold = urgency_ranks.get(target.policy.min_lending_urgency.upper(), 3)

        # Headroom calculation
        target_headroom = max(0.0, target.policy.daily_budget - target.spent_today)
        has_funds = target_headroom >= req.amount
        personality_allows = req_score >= min_threshold

        is_accepted = has_funds and personality_allows
        neg_id = f"NEG-{uuid.uuid4().hex[:8].upper()}"

        if not has_funds:
            transcript = (
                f"[{requester.name} -> {target.name} ({target.personality.value})]: \"Urgency: {req.urgency}. "
                f"Requesting ${req.amount:.2f} daily quota transfer. Justification: {req.justification}\"\n"
                f"[{target.name} ({target.personality.value}) -> {requester.name}]: \"REJECTED (Insufficient Headroom). Only ${target_headroom:.2f} surplus available, "
                f"which cannot satisfy the requested ${req.amount:.2f} quota.\""
            )
        elif not personality_allows:
            transcript = (
                f"[{requester.name} -> {target.name} ({target.personality.value})]: \"Urgency: {req.urgency}. "
                f"Requesting ${req.amount:.2f} daily quota transfer. Justification: {req.justification}\"\n"
                f"[{target.name} ({target.personality.value}) -> {requester.name}]: \"REJECTED ({target.personality_description}). "
                f"Talep aciliyeti '{req.urgency}', ancak benim birikim/fon eşiğim '{target.policy.min_lending_urgency}'. Rezervlerimi koruyorum.\""
            )
        else:
            # Autonomous quota reallocation
            target.policy.daily_budget -= req.amount
            requester.policy.daily_budget += req.amount

            transcript = (
                f"[{requester.name} -> {target.name} ({target.personality.value})]: \"Urgency: {req.urgency}. "
                f"Requesting ${req.amount:.2f} daily quota transfer. Justification: {req.justification}\"\n"
                f"[{target.name} ({target.personality.value}) -> {requester.name}]: \"APPROVED ({target.personality_description}). "
                f"Surplus verified (${target_headroom:.2f} available). Urgency criteria met. Transferred ${req.amount:.2f} quota under Cooperative Protocol.\""
            )

            # Record in Autonomous Internal Debt Ledger
            debt_id = f"DEBT-{uuid.uuid4().hex[:6].upper()}"
            debt_entry = DebtRecord(
                id=debt_id,
                debtor_agent_id=requester.id,
                debtor_name=requester.name,
                creditor_agent_id=target.id,
                creditor_name=target.name,
                principal_amount=req.amount,
                remaining_balance=req.amount,
                negotiation_id=neg_id,
                reason=req.justification,
                status=DebtStatus.OUTSTANDING,
            )
            self._debts[debt_id] = debt_entry

        record = NegotiationRecord(
            id=neg_id,
            requester_agent_id=requester.id,
            requester_name=requester.name,
            target_agent_id=target.id,
            target_name=target.name,
            amount=req.amount,
            currency=req.currency,
            justification=req.justification,
            urgency=req.urgency,
            accepted=is_accepted,
            transcript=transcript,
        )

        self._negotiations[neg_id] = record
        return record

    def list_debts(self, status: Optional[DebtStatus] = None) -> List[DebtRecord]:
        """Lists internal debts filtered by status or all."""
        debts = list(self._debts.values())
        if status:
            debts = [d for d in debts if d.status == status]
        return sorted(debts, key=lambda d: d.created_at, reverse=True)

    def get_debt(self, debt_id: str) -> Optional[DebtRecord]:
        return self._debts.get(debt_id)

    def settle_debt(self, debt_id: str, amount: Optional[float] = None) -> Tuple[bool, str, Optional[DebtRecord]]:
        """Settles an outstanding debt by transferring wallet balance from debtor to creditor."""
        debt = self.get_debt(debt_id)
        if not debt:
            return False, f"Debt with ID '{debt_id}' not found.", None

        if debt.status == DebtStatus.SETTLED:
            return False, f"Debt '{debt_id}' is already fully settled.", debt

        debtor = self.get_agent(debt.debtor_agent_id)
        creditor = self.get_agent(debt.creditor_agent_id)

        if not debtor or not creditor:
            return False, "Debtor or creditor agent profile missing.", debt

        pay_amount = min(debt.remaining_balance, amount) if amount else debt.remaining_balance

        if debtor.wallet_balance < pay_amount:
            # If debtor has partial balance, pay what they can
            if debtor.wallet_balance > 0:
                pay_amount = debtor.wallet_balance
            else:
                return False, f"Debtor '{debtor.name}' has insufficient balance (${debtor.wallet_balance:.2f}) to repay.", debt

        # Execute internal atomic balance transfer
        debtor.wallet_balance -= pay_amount
        creditor.wallet_balance += pay_amount

        # Also restore target creditor's daily policy quota
        creditor.policy.daily_budget += pay_amount
        debtor.policy.daily_budget = max(0.0, debtor.policy.daily_budget - pay_amount)

        debt.remaining_balance -= pay_amount
        if debt.remaining_balance <= 0.001:
            debt.remaining_balance = 0.0
            debt.status = DebtStatus.SETTLED
            debt.settled_at = datetime.now(timezone.utc)
            msg = f"Debt '{debt_id}' fully cleared. ${pay_amount:.2f} refunded from {debtor.name} to {creditor.name}."
        else:
            debt.status = DebtStatus.PARTIALLY_SETTLED
            msg = f"Partial payment of ${pay_amount:.2f} applied. ${debt.remaining_balance:.2f} remaining."

        return True, msg, debt

    def settle_all_debts_for_agent(self, debtor_agent_id: str) -> SettlementResult:
        """Settles all outstanding debts for a specific agent as far as balance allows."""
        active_debts = [d for d in self.list_debts(DebtStatus.OUTSTANDING) if d.debtor_agent_id == debtor_agent_id]
        partially_active = [d for d in self.list_debts(DebtStatus.PARTIALLY_SETTLED) if d.debtor_agent_id == debtor_agent_id]
        all_to_settle = active_debts + partially_active

        total_repaid = 0.0
        cleared_ids = []

        for d in all_to_settle:
            success, _, updated_debt = self.settle_debt(d.id)
            if success and updated_debt:
                repaid = d.principal_amount - updated_debt.remaining_balance
                total_repaid += repaid
                if updated_debt.status == DebtStatus.SETTLED:
                    cleared_ids.append(d.id)

        return SettlementResult(
            settled_count=len(cleared_ids),
            total_repaid=round(total_repaid, 2),
            debts_cleared=cleared_ids,
            message=f"Autonomous settlement cycle executed: {len(cleared_ids)} debt(s) cleared, ${total_repaid:.2f} repaid."
        )

    def simulate_daily_rollover_and_settlement(self) -> Dict[str, Any]:
        """
        Simulates 24-hour daily budget rollover:
        1. Resets spent_today to 0.0 for all agents.
        2. Automatically executes debt settlement loop where debtors repay creditors from replenished liquidity.
        """
        for agent in self._agents.values():
            agent.spent_today = 0.0

        total_settled_amount = 0.0
        settled_debts = []

        # Run settlement across all debtors
        for agent in self._agents.values():
            res = self.settle_all_debts_for_agent(agent.id)
            total_settled_amount += res.total_repaid
            settled_debts.extend(res.debts_cleared)

        return {
            "rollover_timestamp": datetime.now(timezone.utc).isoformat(),
            "agents_reset_count": len(self._agents),
            "debts_cleared_count": len(settled_debts),
            "debts_cleared_ids": settled_debts,
            "total_settled_volume": round(total_settled_amount, 2),
            "message": f"Daily budget rolled over. Spent quotas reset to $0.00. Settled ${total_settled_amount:.2f} in outstanding peer debts."
        }


policy_engine = PolicyEngine()

