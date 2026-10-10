from pydantic import BaseModel
from fastapi import APIRouter
from ...models.roi import ROIMultiplierMetric, PayPalDealCoupon
from ...services.roi_service import roi_service

router = APIRouter(prefix="/roi", tags=["ROI Multiplier & Deals Harvester"])


class HarvestCouponRequest(BaseModel):
    title: str
    vendor: str
    discount_percentage: float
    original_amount: float
    agent_id: str


@router.get("/metrics", response_model=ROIMultiplierMetric)
async def get_roi_metrics():
    return roi_service.get_metrics()


@router.post("/harvest", response_model=PayPalDealCoupon)
async def harvest_deal(request: HarvestCouponRequest):
    return roi_service.harvest_deal(
        title=request.title,
        vendor=request.vendor,
        discount_percentage=request.discount_percentage,
        original_amount=request.original_amount,
        agent_id=request.agent_id,
    )
