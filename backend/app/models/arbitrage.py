from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class WorkloadType(str, Enum):
    GPU_INFERENCE = "gpu_inference"          # LLM / Vision inference (e.g. Llama-3-70B, DeepSeek)
    MODEL_FINE_TUNING = "model_fine_tuning"  # GPU training cluster (LoRA / SFT)
    BULK_EMBEDDINGS = "bulk_embeddings"      # Vector database indexing (10M+ tokens)
    SERVERLESS_COMPUTE = "serverless_compute"# Micro-tasks, web scrapers, ETL workers


class BiddingStrategy(str, Enum):
    COST_FIRST = "COST_FIRST"      # Lowest total USD cost (max arbitrage)
    SPEED_FIRST = "SPEED_FIRST"    # Lowest latency / quickest completion
    BALANCED = "BALANCED"          # Optimal cost-to-reliability trade-off


class VendorQuote(BaseModel):
    vendor_id: str = Field(..., description="Unique slug for the cloud/AI vendor")
    vendor_name: str = Field(..., description="Display name e.g. AWS EC2 Spot, Cloudflare Workers AI")
    workload_type: WorkloadType
    unit_price: float = Field(..., description="Price per unit (USD)")
    unit_label: str = Field(..., description="Unit descriptor e.g. '$/GPU-hr', '$/1M tokens'")
    units_requested: float = Field(..., description="Number of units needed")
    total_price: float = Field(..., description="Calculated total price in USD")
    latency_ms: int = Field(..., description="Estimated p95 roundtrip latency in milliseconds")
    reliability_sla: float = Field(..., description="Historical availability/reliability score 0.0-1.0")
    is_spot: bool = Field(default=True, description="Whether this is a spot/preemptible instance")
    quote_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_details: Optional[Dict[str, Any]] = None


class BiddingRequest(BaseModel):
    requesting_agent_id: str = Field(..., description="ID of the agent initiating procurement")
    workload_type: WorkloadType = Field(default=WorkloadType.GPU_INFERENCE)
    workload_description: str = Field(..., description="Natural language workload specification")
    units_required: float = Field(default=2.5, gt=0, description="Volume of compute/tokens required")
    strategy: BiddingStrategy = Field(default=BiddingStrategy.COST_FIRST)
    max_budget: Optional[float] = Field(None, description="Hard budget ceiling in USD")


class BiddingCompetitionResult(BaseModel):
    bidding_id: str
    requesting_agent_id: str
    workload_type: WorkloadType
    workload_description: str
    units_required: float
    strategy: BiddingStrategy
    quotes: List[VendorQuote]
    winning_quote: VendorQuote
    highest_quote: VendorQuote
    arbitrage_saved_amount: float = Field(..., description="USD saved compared to highest vendor")
    savings_percentage: float = Field(..., description="Percentage discount obtained")
    decision_rationale: str = Field(..., description="Explainable reason why the winner was selected")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArbitrageExecutionRequest(BaseModel):
    bidding_id: str
    override_max_price: Optional[float] = None


class ArbitrageExecutionRecord(BaseModel):
    id: str
    bidding_id: str
    agent_id: str
    agent_name: str
    vendor_id: str
    vendor_name: str
    workload_type: WorkloadType
    workload_description: str
    amount_paid: float
    reference_highest_price: float
    arbitrage_saved: float
    savings_percentage: float
    paypal_order_id: Optional[str] = None
    paypal_status: str = "COMPLETED"
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    audit_summary: str


class LiquidityRebalanceRequest(BaseModel):
    from_agent_id: str = Field(..., description="Agent with idle daytime liquidity")
    to_agent_id: str = Field(..., description="Agent needing nighttime batch budget")
    amount: float = Field(..., gt=0, description="USD volume to rebalance")
    reason: str = Field(..., description="Strategic explanation for capital reallocation")


class LiquidityRebalanceResult(BaseModel):
    rebalance_id: str
    from_agent_id: str
    from_agent_name: str
    to_agent_id: str
    to_agent_name: str
    amount_rebalanced: float
    source_remaining_budget: float
    target_new_budget: float
    executed_at: datetime
    message: str
