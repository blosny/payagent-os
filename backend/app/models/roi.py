from typing import Optional, List
from pydantic import BaseModel, Field


class PayPalDealCoupon(BaseModel):
    id: str
    title: str
    vendor: str
    discount_percentage: float
    saved_amount: float
    applied_at: str
    agent_id: str
    status: str = "HARVESTED"  # HARVESTED, AVAILABLE, EXPIRED


class ROIMultiplierMetric(BaseModel):
    fleet_multiplier: float = 3.4
    multiplier_trend: str = "+0.6x"
    total_spent: float = 128.50
    estimated_output_value: float = 436.90
    cumulative_discount_saved: float = 84.20
    active_deals_applied: int = 4
    sparkline_points: List[float] = Field(default_factory=lambda: [2.1, 2.4, 2.8, 3.1, 3.2, 3.4])
    recent_coupons: List[PayPalDealCoupon] = Field(default_factory=list)
