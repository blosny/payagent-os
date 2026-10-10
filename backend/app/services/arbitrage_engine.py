import uuid
import random
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone

from ..models.arbitrage import (
    WorkloadType,
    BiddingStrategy,
    VendorQuote,
    BiddingRequest,
    BiddingCompetitionResult,
    ArbitrageExecutionRequest,
    ArbitrageExecutionRecord,
    LiquidityRebalanceRequest,
    LiquidityRebalanceResult,
)
from ..models.transaction import (
    TransactionIntent,
    TransactionRecord,
    TransactionStatus,
    TransactionType,
)
from .policy_engine import policy_engine
from .paypal_service import paypal_service


class ArbitrageEngine:
    """
    Autonomous Vendor Spot Bidding & Arbitrage Engine.
    Periodically scrapes/simulates cloud & AI compute spot market rates across AWS, Cloudflare,
    HuggingFace, RunPod, and DeepInfra; conducts competitive auctions; selects optimal providers;
    and executes autonomous PayPal payments while capturing cost arbitrage (Alpha) for the treasury.
    """

    def __init__(self):
        self._active_biddings: Dict[str, BiddingCompetitionResult] = {}
        self._execution_history: List[ArbitrageExecutionRecord] = []
        self._rebalance_history: List[LiquidityRebalanceResult] = []
        self._total_arbitrage_saved: float = 0.0

        # Base pricing catalog per workload type
        # format: (vendor_id, vendor_name, unit_price, unit_label, latency_ms, reliability_sla, is_spot)
        self._vendor_catalog: Dict[WorkloadType, List[Dict[str, Any]]] = {
            WorkloadType.GPU_INFERENCE: [
                {
                    "vendor_id": "aws-bedrock",
                    "vendor_name": "AWS Bedrock (EC2 Spot)",
                    "base_unit_price": 4.20,
                    "unit_label": "$/GPU-hr",
                    "base_latency": 45,
                    "reliability": 0.999,
                    "is_spot": True,
                },
                {
                    "vendor_id": "runpod-spot",
                    "vendor_name": "RunPod GPU Spot Cluster",
                    "base_unit_price": 2.15,
                    "unit_label": "$/GPU-hr",
                    "base_latency": 68,
                    "reliability": 0.975,
                    "is_spot": True,
                },
                {
                    "vendor_id": "cloudflare-workers-ai",
                    "vendor_name": "Cloudflare Workers AI",
                    "base_unit_price": 3.40,
                    "unit_label": "$/GPU-hr",
                    "base_latency": 24,
                    "reliability": 0.998,
                    "is_spot": False,
                },
                {
                    "vendor_id": "huggingface-endpoints",
                    "vendor_name": "HuggingFace Dedicated Endpoints",
                    "base_unit_price": 2.90,
                    "unit_label": "$/GPU-hr",
                    "base_latency": 62,
                    "reliability": 0.992,
                    "is_spot": True,
                },
            ],
            WorkloadType.MODEL_FINE_TUNING: [
                {
                    "vendor_id": "aws-bedrock",
                    "vendor_name": "AWS EC2 p4de.24xlarge Spot",
                    "base_unit_price": 12.80,
                    "unit_label": "$/Cluster-hr",
                    "base_latency": 80,
                    "reliability": 0.999,
                    "is_spot": True,
                },
                {
                    "vendor_id": "runpod-spot",
                    "vendor_name": "RunPod 8x H100 SXM5 Spot",
                    "base_unit_price": 7.40,
                    "unit_label": "$/Cluster-hr",
                    "base_latency": 95,
                    "reliability": 0.970,
                    "is_spot": True,
                },
                {
                    "vendor_id": "huggingface-endpoints",
                    "vendor_name": "HuggingFace AutoTrain Cluster",
                    "base_unit_price": 9.20,
                    "unit_label": "$/Cluster-hr",
                    "base_latency": 85,
                    "reliability": 0.990,
                    "is_spot": True,
                },
            ],
            WorkloadType.BULK_EMBEDDINGS: [
                {
                    "vendor_id": "cloudflare-workers-ai",
                    "vendor_name": "Cloudflare BGE-Large Worker",
                    "base_unit_price": 0.12,
                    "unit_label": "$/1M tokens",
                    "base_latency": 18,
                    "reliability": 0.999,
                    "is_spot": False,
                },
                {
                    "vendor_id": "deepinfra-serverless",
                    "vendor_name": "DeepInfra Embeddings API",
                    "base_unit_price": 0.08,
                    "unit_label": "$/1M tokens",
                    "base_latency": 35,
                    "reliability": 0.991,
                    "is_spot": False,
                },
                {
                    "vendor_id": "aws-bedrock",
                    "vendor_name": "AWS Titan Embeddings v2",
                    "base_unit_price": 0.20,
                    "unit_label": "$/1M tokens",
                    "base_latency": 42,
                    "reliability": 0.999,
                    "is_spot": False,
                },
            ],
            WorkloadType.SERVERLESS_COMPUTE: [
                {
                    "vendor_id": "cloudflare-workers-ai",
                    "vendor_name": "Cloudflare Workers Unbound",
                    "base_unit_price": 0.30,
                    "unit_label": "$/1M requests",
                    "base_latency": 15,
                    "reliability": 0.999,
                    "is_spot": False,
                },
                {
                    "vendor_id": "aws-bedrock",
                    "vendor_name": "AWS Lambda Edge",
                    "base_unit_price": 0.60,
                    "unit_label": "$/1M requests",
                    "base_latency": 30,
                    "reliability": 0.999,
                    "is_spot": False,
                },
                {
                    "vendor_id": "runpod-spot",
                    "vendor_name": "RunPod Serverless Pods",
                    "base_unit_price": 0.22,
                    "unit_label": "$/1M requests",
                    "base_latency": 55,
                    "reliability": 0.985,
                    "is_spot": True,
                },
            ],
        }

    def get_market_spot_rates(self) -> Dict[str, Any]:
        """Returns the real-time spot price board across all workload categories."""
        board = {}
        for w_type, vendors in self._vendor_catalog.items():
            board[w_type.value] = []
            for v in vendors:
                jitter = random.uniform(0.96, 1.04)
                current_rate = round(v["base_unit_price"] * jitter, 2)
                board[w_type.value].append({
                    "vendor_id": v["vendor_id"],
                    "vendor_name": v["vendor_name"],
                    "current_rate": current_rate,
                    "unit_label": v["unit_label"],
                    "latency_ms": v["base_latency"],
                    "reliability": v["reliability"],
                    "is_spot": v["is_spot"],
                })
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_categories": len(board),
            "spot_board": board,
            "total_arbitrage_saved": round(self._total_arbitrage_saved, 2),
            "total_auctions_conducted": len(self._execution_history),
        }

    def solicit_quotes(self, request: BiddingRequest) -> BiddingCompetitionResult:
        """
        Solicts competitive bids for an agent's workload requirement across active cloud providers.
        Evaluates the quotes based on the agent's strategy (Cost, Speed, or Balanced),
        computes the cost arbitrage vs the most expensive vendor, and stores the bidding record.
        """
        agent = policy_engine.get_agent(request.requesting_agent_id)
        if not agent:
            raise ValueError(f"Requesting agent '{request.requesting_agent_id}' does not exist.")

        vendors = self._vendor_catalog.get(request.workload_type, [])
        if not vendors:
            raise ValueError(f"No providers available for workload type '{request.workload_type}'.")

        bidding_id = f"bid-{uuid.uuid4().hex[:8]}"
        quotes: List[VendorQuote] = []

        for v in vendors:
            # Add dynamic jitter to simulate live spot market fluctuations
            jitter = random.uniform(0.95, 1.05)
            unit_price = round(v["base_unit_price"] * jitter, 2)
            total_price = round(unit_price * request.units_required, 2)
            latency = int(v["base_latency"] * random.uniform(0.90, 1.10))

            quote = VendorQuote(
                vendor_id=v["vendor_id"],
                vendor_name=v["vendor_name"],
                workload_type=request.workload_type,
                unit_price=unit_price,
                unit_label=v["unit_label"],
                units_requested=request.units_required,
                total_price=total_price,
                latency_ms=latency,
                reliability_sla=v["reliability"],
                is_spot=v["is_spot"],
            )
            quotes.append(quote)

        # Sort quotes depending on strategy
        if request.strategy == BiddingStrategy.SPEED_FIRST:
            # Sort primarily by lowest latency
            sorted_quotes = sorted(quotes, key=lambda q: (q.latency_ms, q.total_price))
            winner = sorted_quotes[0]
            rationale = (
                f"Speed-first optimization: '{winner.vendor_name}' selected for minimal latency "
                f"({winner.latency_ms}ms) at ${winner.total_price:.2f}."
            )
        elif request.strategy == BiddingStrategy.BALANCED:
            # Score combining cost (60%), latency (20%), reliability (20%)
            min_cost = min(q.total_price for q in quotes)
            min_lat = min(q.latency_ms for q in quotes)

            def score(q: VendorQuote):
                cost_ratio = min_cost / max(q.total_price, 0.01)
                lat_ratio = min_lat / max(q.latency_ms, 1)
                rel_score = q.reliability_sla
                return (cost_ratio * 0.6) + (lat_ratio * 0.2) + (rel_score * 0.2)

            sorted_quotes = sorted(quotes, key=score, reverse=True)
            winner = sorted_quotes[0]
            rationale = (
                f"Balanced optimization: '{winner.vendor_name}' achieved highest composite score "
                f"(SLA: {winner.reliability_sla*100:.1f}%, latency: {winner.latency_ms}ms, cost: ${winner.total_price:.2f})."
            )
        else: # COST_FIRST (Default)
            sorted_quotes = sorted(quotes, key=lambda q: q.total_price)
            winner = sorted_quotes[0]
            rationale = (
                f"Cost-first spot arbitrage: '{winner.vendor_name}' won the competitive auction "
                f"with lowest total bid of ${winner.total_price:.2f} (unit: ${winner.unit_price:.2f}{winner.unit_label})."
            )

        highest = max(quotes, key=lambda q: q.total_price)
        arbitrage_saved = round(max(0.0, highest.total_price - winner.total_price), 2)
        savings_pct = round((arbitrage_saved / max(highest.total_price, 0.01)) * 100, 1) if highest.total_price > 0 else 0.0

        result = BiddingCompetitionResult(
            bidding_id=bidding_id,
            requesting_agent_id=request.requesting_agent_id,
            workload_type=request.workload_type,
            workload_description=request.workload_description,
            units_required=request.units_required,
            strategy=request.strategy,
            quotes=quotes,
            winning_quote=winner,
            highest_quote=highest,
            arbitrage_saved_amount=arbitrage_saved,
            savings_percentage=savings_pct,
            decision_rationale=rationale,
        )

        self._active_biddings[bidding_id] = result
        return result

    async def execute_winning_bid(self, req: ArbitrageExecutionRequest) -> ArbitrageExecutionRecord:
        """
        Executes autonomous procurement of the winning vendor quote:
        1. Validates agent limits & wallet balance.
        2. Dispatches real/simulated PayPal Orders v2 payment.
        3. Records transaction in the global audit trail.
        4. Accrues the cost arbitrage savings in treasury metrics.
        """
        bidding = self._active_biddings.get(req.bidding_id)
        if not bidding:
            raise ValueError(f"Bidding with ID '{req.bidding_id}' not found or expired.")

        agent = policy_engine.get_agent(bidding.requesting_agent_id)
        if not agent:
            raise ValueError(f"Agent '{bidding.requesting_agent_id}' does not exist.")

        winner = bidding.winning_quote
        highest = bidding.highest_quote
        amount = winner.total_price

        if req.override_max_price and amount > req.override_max_price:
            raise ValueError(f"Winning bid (${amount:.2f}) exceeds requested price limit (${req.override_max_price:.2f}).")

        if agent.wallet_balance < amount:
            raise ValueError(
                f"Agent '{agent.name}' has insufficient wallet balance (${agent.wallet_balance:.2f}) "
                f"for winning bid of ${amount:.2f}."
            )

        # Execute PayPal Orders v2 payment
        paypal_resp = await paypal_service.create_order(
            amount=amount,
            currency="USD",
            description=f"PayAgent OS Spot Arbitrage: {winner.vendor_name} ({bidding.workload_description})",
            reference_id=f"arb-{bidding.bidding_id}",
        )

        order_id = paypal_resp.get("order_id", f"PAYPAL-ARB-{uuid.uuid4().hex[:6].upper()}")
        paypal_status = paypal_resp.get("status", "COMPLETED")

        # Capture order if status is CREATED
        if paypal_status == "CREATED":
            capture_resp = await paypal_service.capture_order(order_id)
            paypal_status = capture_resp.get("status", "COMPLETED")

        # Deduct wallet balance and add to spent_today
        agent.wallet_balance = round(agent.wallet_balance - amount, 2)
        agent.spent_today = round(agent.spent_today + amount, 2)

        # Accrue arbitrage savings
        saved_amount = bidding.arbitrage_saved_amount
        self._total_arbitrage_saved = round(self._total_arbitrage_saved + saved_amount, 2)

        # Create record in audit trail
        tx_id = f"tx-arb-{uuid.uuid4().hex[:8]}"
        audit_note = (
            f"[SPOT ARBITRAGE WINNER: {winner.vendor_name}] Solicitied {len(bidding.quotes)} quotes. "
            f"Paid ${amount:.2f} via PayPal ({order_id}). Generated ${saved_amount:.2f} treasury alpha "
            f"({bidding.savings_percentage}% discount vs {highest.vendor_name} @ ${highest.total_price:.2f})."
        )

        record = TransactionRecord(
            id=tx_id,
            agent_id=agent.id,
            agent_name=agent.name,
            amount=amount,
            currency="USD",
            recipient=winner.vendor_name,
            category=f"Spot Compute / {bidding.workload_type.value}",
            reasoning=f"{bidding.workload_description} | {bidding.decision_rationale}",
            policy_evaluation_reason=audit_note,
            status=TransactionStatus.APPROVED_AUTONOMOUS,
            transaction_type=TransactionType.PAYPAL_ORDER,
            paypal_order_id=order_id,
            created_at=datetime.now(timezone.utc),
            resolved_at=datetime.now(timezone.utc),
        )
        policy_engine._transactions[tx_id] = record

        exec_record = ArbitrageExecutionRecord(
            id=f"exec-{uuid.uuid4().hex[:8]}",
            bidding_id=bidding.bidding_id,
            agent_id=agent.id,
            agent_name=agent.name,
            vendor_id=winner.vendor_id,
            vendor_name=winner.vendor_name,
            workload_type=bidding.workload_type,
            workload_description=bidding.workload_description,
            amount_paid=amount,
            reference_highest_price=highest.total_price,
            arbitrage_saved=saved_amount,
            savings_percentage=bidding.savings_percentage,
            paypal_order_id=order_id,
            paypal_status=paypal_status,
            audit_summary=audit_note,
        )

        self._execution_history.append(exec_record)
        return exec_record

    def rebalance_portfolio_liquidity(self, req: LiquidityRebalanceRequest) -> LiquidityRebalanceResult:
        """
        Autonomous nocturnal and workload-driven liquidity rebalancing.
        Transfers idle daytime quota from a dormant agent to a heavy nocturnal worker.
        """
        source = policy_engine.get_agent(req.from_agent_id)
        target = policy_engine.get_agent(req.to_agent_id)

        if not source or not target:
            raise ValueError("Source or target agent profile not found.")

        if req.amount <= 0:
            raise ValueError("Rebalance amount must be positive.")

        # Rebalance daily budget quota
        if source.policy.daily_budget < req.amount:
            req.amount = max(0.0, source.policy.daily_budget)

        source.policy.daily_budget = round(source.policy.daily_budget - req.amount, 2)
        target.policy.daily_budget = round(target.policy.daily_budget + req.amount, 2)

        result = LiquidityRebalanceResult(
            rebalance_id=f"reb-{uuid.uuid4().hex[:8]}",
            from_agent_id=source.id,
            from_agent_name=source.name,
            to_agent_id=target.id,
            to_agent_name=target.name,
            amount_rebalanced=req.amount,
            source_remaining_budget=source.policy.daily_budget,
            target_new_budget=target.policy.daily_budget,
            executed_at=datetime.now(timezone.utc),
            message=(
                f"Autonomous liquidity shift completed: ${req.amount:.2f} transferred from "
                f"{source.name} to {target.name}. Strategic Reason: {req.reason}"
            ),
        )

        self._rebalance_history.append(result)
        return result

    def get_total_arbitrage_saved(self) -> float:
        return self._total_arbitrage_saved

    def list_executions(self) -> List[ArbitrageExecutionRecord]:
        return sorted(self._execution_history, key=lambda x: x.executed_at, reverse=True)

    def list_rebalances(self) -> List[LiquidityRebalanceResult]:
        return sorted(self._rebalance_history, key=lambda x: x.executed_at, reverse=True)


arbitrage_engine = ArbitrageEngine()
