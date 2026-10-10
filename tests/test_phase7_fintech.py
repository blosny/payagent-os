import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.vault_service import vault_service
from backend.app.services.credit_service import credit_service
from backend.app.services.telegram_service import telegram_service
from backend.app.services.roi_service import roi_service
from backend.app.models.credit import FICOConfig


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_vault_subscriptions_and_inactivity_scan():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # List all subscriptions
        res = await ac.get("/api/v1/vault/subscriptions")
        assert res.status_code == 200
        subs = res.json()
        assert len(subs) >= 3
        notion_sub = next(s for s in subs if s["id"] == "sub_notion_01")
        assert notion_sub["days_unused"] == 28
        assert notion_sub["status"] == "UNUSED_WARNING"

        # Scan inactivity
        scan_res = await ac.post("/api/v1/vault/scan")
        assert scan_res.status_code == 200
        scan_data = scan_res.json()
        assert scan_data["flagged_unused_count"] >= 1
        assert scan_data["potential_monthly_savings"] >= 49.0

        # Cancel unused subscription
        cancel_res = await ac.post(
            "/api/v1/vault/cancel",
            json={
                "subscription_id": "sub_notion_01",
                "reason": "AI fleet has no active seats for 28 days",
                "confirmed_by": "supervisor_elena",
            },
        )
        assert cancel_res.status_code == 200
        canceled_data = cancel_res.json()
        assert canceled_data["status"] == "CANCELED"
        assert canceled_data["savings_on_cancel"] == 49.0


@pytest.mark.asyncio
async def test_credit_service_and_fico_scoring():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # List fleet credit scores
        res = await ac.get("/api/v1/credit/scores")
        assert res.status_code == 200
        scores = res.json()
        assert len(scores) >= 3

        devops = next(s for s in scores if s["agent_id"] == "agent-devops")
        assert devops["fico_score"] == 812
        assert devops["tier"] == "Prime"
        initial_limit = devops["dynamic_daily_limit"]
        assert initial_limit > 0

        # Adjust score for prompt anomaly / policy penalty
        adj_res = await ac.post(
            "/api/v1/credit/adjust",
            json={
                "agent_id": "agent-devops",
                "event_type": "POLICY_ANOMALY",
                "reason": "Unexpected sudden budget spike detected",
            },
        )
        assert adj_res.status_code == 200
        adj_data = adj_res.json()
        assert adj_data["new_score"] < 812
        assert adj_data["new_limit"] < initial_limit

        # Get and update FICO config
        cfg_res = await ac.get("/api/v1/credit/config")
        assert cfg_res.status_code == 200
        cfg_data = cfg_res.json()
        assert cfg_data["prime_threshold"] == 800

        update_cfg_res = await ac.post(
            "/api/v1/credit/config",
            json={
                "on_time_repayment_bonus": 50,
                "budget_discipline_bonus": 30,
                "policy_anomaly_penalty": 45,
                "high_risk_penalty": 80,
                "prime_threshold": 805,
                "trusted_threshold": 745,
                "monitored_threshold": 675,
            },
        )
        assert update_cfg_res.status_code == 200
        assert update_cfg_res.json()["prime_threshold"] == 805


@pytest.mark.asyncio
async def test_telegram_supervisor_alerts():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Get settings
        res = await ac.get("/api/v1/telegram/settings")
        assert res.status_code == 200
        data = res.json()
        assert data["connected_account"] == "@elena_cfo"
        assert data["hitl_approval_requests"] is True

        # Update settings
        up_res = await ac.post(
            "/api/v1/telegram/settings",
            json={
                "connected_account": "@elena_cfo",
                "hitl_approval_requests": True,
                "blocked_risk_events": True,
                "daily_treasury_summary": True,
                "is_connected": True,
            },
        )
        assert up_res.status_code == 200
        assert up_res.json()["daily_treasury_summary"] is True

        # Send test alert
        alert_res = await ac.post(
            "/api/v1/telegram/test-alert",
            json={"message": "Fleet heartbeat check from PayAgent OS"},
        )
        assert alert_res.status_code == 200
        alert_data = alert_res.json()
        assert alert_data["delivered"] is True

        # List alerts history
        hist_res = await ac.get("/api/v1/telegram/alerts")
        assert hist_res.status_code == 200
        assert len(hist_res.json()) >= 1


@pytest.mark.asyncio
async def test_roi_and_coupon_harvesting():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Get metrics
        res = await ac.get("/api/v1/roi/metrics")
        assert res.status_code == 200
        data = res.json()
        assert data["fleet_multiplier"] >= 3.0
        assert data["cumulative_discount_saved"] >= 80.0
        assert len(data["recent_coupons"]) >= 3

        # Harvest new coupon deal
        harvest_res = await ac.post(
            "/api/v1/roi/harvest",
            json={
                "title": "Cloudflare Workers 20% Rebate",
                "vendor": "Cloudflare",
                "discount_percentage": 20.0,
                "original_amount": 50.0,
                "agent_id": "agent-devops",
            },
        )
        assert harvest_res.status_code == 200
        cpn = harvest_res.json()
        assert cpn["saved_amount"] == 10.0
        assert cpn["vendor"] == "Cloudflare"

        # Verify metrics updated
        res_after = await ac.get("/api/v1/roi/metrics")
        after_data = res_after.json()
        assert after_data["cumulative_discount_saved"] >= 94.0
