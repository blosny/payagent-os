import uuid
from typing import List, Optional, Dict
from datetime import datetime, timezone
from ..models.telegram import TelegramSettings, TelegramAlertNotification


class TelegramService:
    """Dispatches real-time supervisor alerts to Telegram (@elena_cfo) for HITL requests & risk events."""

    def __init__(self):
        self.settings = TelegramSettings()
        self._history: List[TelegramAlertNotification] = []
        self._init_mock_history()

    def _init_mock_history(self):
        now = datetime.now(timezone.utc).isoformat()
        self._history.append(
            TelegramAlertNotification(
                id=f"tg_{uuid.uuid4().hex[:8]}",
                recipient=self.settings.connected_account,
                event_type="HITL_PENDING",
                title="⚠️ Supervisor Review Required",
                message="DevOps Agent requested $240.00 for AWS Compute Cluster. Policy limit exceeded ($150 limit).",
                amount=240.00,
                vendor="AWS Compute",
                action_url="https://payagent.local/#hitl",
                sent_at=now,
                delivered=True,
            )
        )

    def get_settings(self) -> TelegramSettings:
        return self.settings

    def update_settings(self, new_settings: TelegramSettings) -> TelegramSettings:
        self.settings = new_settings
        return self.settings

    def list_history(self, limit: int = 20) -> List[TelegramAlertNotification]:
        return list(reversed(self._history))[:limit]

    def send_alert(
        self,
        event_type: str,
        title: str,
        message: str,
        amount: Optional[float] = None,
        vendor: Optional[str] = None,
        action_url: Optional[str] = None,
    ) -> Optional[TelegramAlertNotification]:
        if not self.settings.is_connected:
            return None

        # Check notification filter rules
        if event_type == "HITL_PENDING" and not self.settings.hitl_approval_requests:
            return None
        if event_type == "RISK_BLOCKED" and not self.settings.blocked_risk_events:
            return None
        if event_type == "DAILY_SUMMARY" and not self.settings.daily_treasury_summary:
            return None

        alert = TelegramAlertNotification(
            id=f"tg_{uuid.uuid4().hex[:8]}",
            recipient=self.settings.connected_account,
            event_type=event_type,
            title=title,
            message=message,
            amount=amount,
            vendor=vendor,
            action_url=action_url,
            sent_at=datetime.now(timezone.utc).isoformat(),
            delivered=True,
        )
        self._history.append(alert)
        return alert


telegram_service = TelegramService()
