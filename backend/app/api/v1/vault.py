from typing import List, Optional
from fastapi import APIRouter, HTTPException
from ...models.vault import SaaSSubscription, SubscriptionStatus, CancelSubscriptionRequest
from ...services.vault_service import vault_service

router = APIRouter(prefix="/vault", tags=["PayPal Vault & Subscriptions"])


@router.get("/subscriptions", response_model=List[SaaSSubscription])
async def list_subscriptions(status: Optional[SubscriptionStatus] = None):
    return vault_service.list_subscriptions(status=status)


@router.post("/scan")
async def scan_inactivity():
    return vault_service.scan_inactivity()


@router.post("/cancel", response_model=SaaSSubscription)
async def cancel_subscription(request: CancelSubscriptionRequest):
    sub = vault_service.cancel_subscription(request)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub
