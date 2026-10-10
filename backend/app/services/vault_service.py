import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from ..models.vault import SaaSSubscription, SubscriptionStatus, CancelSubscriptionRequest


class VaultService:
    """Manages SaaS recurring subscriptions via PayPal Vault and auto-detects inactive subscriptions."""

    def __init__(self):
        self._subscriptions: Dict[str, SaaSSubscription] = {}
        self._init_mock_subscriptions()

    def _init_mock_subscriptions(self):
        now = datetime.now(timezone.utc).isoformat()
        subs = [
            SaaSSubscription(
                id="sub_notion_01",
                service_name="Notion AI Workspace",
                plan_tier="BUSINESS",
                monthly_cost=49.00,
                currency="USD",
                paypal_vault_id="VAULT-NTN-99412",
                last_agent_call_at="2026-09-12T10:00:00Z",
                days_unused=28,
                inactivity_threshold_days=14,
                status=SubscriptionStatus.UNUSED_WARNING,
                savings_on_cancel=49.00,
                agent_subscribers=["agent-research", "agent-copywriter"],
                created_at="2026-01-15T00:00:00Z",
            ),
            SaaSSubscription(
                id="sub_cursor_02",
                service_name="Cursor IDE Business Fleet",
                plan_tier="TEAM",
                monthly_cost=40.00,
                currency="USD",
                paypal_vault_id="VAULT-CRS-33810",
                last_agent_call_at=now,
                days_unused=1,
                inactivity_threshold_days=14,
                status=SubscriptionStatus.ACTIVE,
                savings_on_cancel=0.0,
                agent_subscribers=["agent-devops", "agent-secops"],
                created_at="2026-03-01T00:00:00Z",
            ),
            SaaSSubscription(
                id="sub_datadog_03",
                service_name="Datadog APM & Logs",
                plan_tier="ENTERPRISE",
                monthly_cost=65.00,
                currency="USD",
                paypal_vault_id="VAULT-DDG-77215",
                last_agent_call_at="2026-09-22T14:30:00Z",
                days_unused=18,
                inactivity_threshold_days=14,
                status=SubscriptionStatus.UNUSED_WARNING,
                savings_on_cancel=65.00,
                agent_subscribers=["agent-devops"],
                created_at="2026-02-10T00:00:00Z",
            ),
        ]
        for sub in subs:
            self._subscriptions[sub.id] = sub

    def list_subscriptions(self, status: Optional[SubscriptionStatus] = None) -> List[SaaSSubscription]:
        subs = list(self._subscriptions.values())
        if status:
            return [s for s in subs if s.status == status]
        return subs

    def get_subscription(self, subscription_id: str) -> Optional[SaaSSubscription]:
        return self._subscriptions.get(subscription_id)

    def cancel_subscription(self, request: CancelSubscriptionRequest) -> Optional[SaaSSubscription]:
        sub = self._subscriptions.get(request.subscription_id)
        if not sub:
            return None
        sub.status = SubscriptionStatus.CANCELED
        sub.savings_on_cancel = sub.monthly_cost
        return sub

    def scan_inactivity(self) -> Dict[str, Any]:
        """Scans all subscriptions for fleet usage and marks unused ones as warnings."""
        flagged = []
        potential_monthly_savings = 0.0

        for sub in self._subscriptions.values():
            if sub.status == SubscriptionStatus.CANCELED:
                continue
            if sub.days_unused >= sub.inactivity_threshold_days:
                sub.status = SubscriptionStatus.UNUSED_WARNING
                flagged.append(sub)
                potential_monthly_savings += sub.monthly_cost

        return {
            "total_subscriptions": len(self._subscriptions),
            "flagged_unused_count": len(flagged),
            "potential_monthly_savings": potential_monthly_savings,
            "flagged_subscriptions": flagged,
        }


vault_service = VaultService()
