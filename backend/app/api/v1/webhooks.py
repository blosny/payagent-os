import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Request, Header, HTTPException, status

from ...models.webhook import (
    PayPalWebhookEvent,
    WebhookVerificationResponse,
)
from ...services.webhook_service import paypal_webhook_service

router = APIRouter(prefix="/webhooks", tags=["Cryptographic PayPal Webhooks"])


@router.post("/paypal", response_model=WebhookVerificationResponse)
async def receive_paypal_webhook(
    request: Request,
    paypal_transmission_id: Optional[str] = Header(None, alias="PAYPAL-TRANSMISSION-ID"),
    paypal_transmission_time: Optional[str] = Header(None, alias="PAYPAL-TRANSMISSION-TIME"),
    paypal_cert_url: Optional[str] = Header(None, alias="PAYPAL-CERT-URL"),
    paypal_auth_algo: Optional[str] = Header(None, alias="PAYPAL-AUTH-ALGO"),
    paypal_transmission_sig: Optional[str] = Header(None, alias="PAYPAL-TRANSMISSION-SIG"),
):
    """Receives and cryptographically verifies PayPal webhook notifications."""
    raw_body_bytes = await request.body()
    raw_body_str = raw_body_bytes.decode("utf-8")

    try:
        body_json = json.loads(raw_body_str)
        event = PayPalWebhookEvent(**body_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook JSON payload: {e}")

    # Fallback default headers if sent in development simulation
    t_id = paypal_transmission_id or f"WH-TX-{event.id}"
    t_time = paypal_transmission_time or event.create_time
    cert_url = paypal_cert_url or "https://api.sandbox.paypal.com/v1/notifications/certs/CERT-SANDBOX"
    auth_algo = paypal_auth_algo or "SHA256withRSA"
    sig = paypal_transmission_sig or "TEST-SIG-SIMULATED"

    is_verified = paypal_webhook_service.verify_signature(
        transmission_id=t_id,
        transmission_time=t_time,
        cert_url=cert_url,
        auth_algo=auth_algo,
        transmission_sig=sig,
        raw_body=raw_body_str,
    )

    response = await paypal_webhook_service.process_webhook_event(
        event=event,
        transmission_id=t_id,
        is_verified=is_verified,
    )
    return response


@router.get("/events", response_model=List[Dict[str, Any]])
async def list_webhook_events():
    """Lists received and processed PayPal webhook events."""
    return paypal_webhook_service.get_received_events()
