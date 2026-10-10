import uuid
from typing import List, Optional
from datetime import datetime, timezone
from ..models.roi import ROIMultiplierMetric, PayPalDealCoupon


class ROIService:
    """Computes AI Fleet ROI productivity multiplier & harvests PayPal Deals / enterprise discounts."""

    def __init__(self):
        self._metric = ROIMultiplierMetric()
        self._init_coupons()

    def _init_coupons(self):
        now = datetime.now(timezone.utc).isoformat()
        coupons = [
            PayPalDealCoupon(
                id="cpn_aws_01",
                title="15% Off AWS Spot Compute",
                vendor="AWS",
                discount_percentage=15.0,
                saved_amount=36.00,
                applied_at=now,
                agent_id="agent-devops",
                status="HARVESTED",
            ),
            PayPalDealCoupon(
                id="cpn_gh_02",
                title="20% Rebate GitHub Enterprise",
                vendor="GitHub",
                discount_percentage=20.0,
                saved_amount=20.00,
                applied_at=now,
                agent_id="agent-devops",
                status="HARVESTED",
            ),
            PayPalDealCoupon(
                id="cpn_mongo_03",
                title="MongoDB Atlas Dedicated Credit",
                vendor="MongoDB",
                discount_percentage=12.5,
                saved_amount=28.20,
                applied_at=now,
                agent_id="agent-research",
                status="HARVESTED",
            ),
        ]
        self._metric.recent_coupons = coupons
        self._metric.cumulative_discount_saved = sum(c.saved_amount for c in coupons)
        self._metric.active_deals_applied = len(coupons)

    def get_metrics(self) -> ROIMultiplierMetric:
        return self._metric

    def harvest_deal(
        self,
        title: str,
        vendor: str,
        discount_percentage: float,
        original_amount: float,
        agent_id: str,
    ) -> PayPalDealCoupon:
        saved_amount = round((discount_percentage / 100.0) * original_amount, 2)
        coupon = PayPalDealCoupon(
            id=f"cpn_{uuid.uuid4().hex[:8]}",
            title=title,
            vendor=vendor,
            discount_percentage=discount_percentage,
            saved_amount=saved_amount,
            applied_at=datetime.now(timezone.utc).isoformat(),
            agent_id=agent_id,
            status="HARVESTED",
        )
        self._metric.recent_coupons.insert(0, coupon)
        self._metric.cumulative_discount_saved = round(
            self._metric.cumulative_discount_saved + saved_amount, 2
        )
        self._metric.active_deals_applied += 1
        
        # Slight boost to multiplier for autonomous cost optimization
        self._metric.fleet_multiplier = round(self._metric.fleet_multiplier + 0.1, 1)
        self._metric.sparkline_points.append(self._metric.fleet_multiplier)
        if len(self._metric.sparkline_points) > 10:
            self._metric.sparkline_points.pop(0)

        return coupon


roi_service = ROIService()
