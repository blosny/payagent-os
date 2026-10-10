from typing import Dict, List, Optional
from datetime import datetime, timezone
from ..models.credit import FICOConfig, AgentCreditScore, FICOUpdateResponse


class CreditService:
    """Manages autonomous AI fleet FICO credit ratings (300-850) and dynamic daily spending limits."""

    def __init__(self):
        self.config = FICOConfig()
        self._scores: Dict[str, AgentCreditScore] = {}
        self._init_mock_scores()

    def _init_mock_scores(self):
        now = datetime.now(timezone.utc).isoformat()
        initial = [
            AgentCreditScore(
                agent_id="agent-devops",
                agent_name="DevOps Agent",
                fico_score=812,
                tier="Prime",
                color_accent="#10b981",
                dynamic_daily_limit=800.0,
                total_settled_debts=14,
                anomalies_count=0,
                last_adjusted_at=now,
            ),
            AgentCreditScore(
                agent_id="agent-research",
                agent_name="Research Agent",
                fico_score=746,
                tier="Trusted",
                color_accent="#3b82f6",
                dynamic_daily_limit=350.0,
                total_settled_debts=8,
                anomalies_count=1,
                last_adjusted_at=now,
            ),
            AgentCreditScore(
                agent_id="agent-contractor",
                agent_name="Contractor Agent",
                fico_score=628,
                tier="Monitored",
                color_accent="#f59e0b",
                dynamic_daily_limit=180.0,
                total_settled_debts=3,
                anomalies_count=2,
                last_adjusted_at=now,
            ),
        ]
        for s in initial:
            s.dynamic_daily_limit = self._calculate_limit_for_score(s.fico_score)
            self._scores[s.agent_id] = s

    def get_score(self, agent_id: str) -> Optional[AgentCreditScore]:
        return self._scores.get(agent_id)

    def list_scores(self) -> List[AgentCreditScore]:
        return list(self._scores.values())

    def update_config(self, new_config: FICOConfig) -> FICOConfig:
        self.config = new_config
        # Re-evaluate tiers for all agents with new config thresholds
        for score in self._scores.values():
            score.tier = self._calculate_tier(score.fico_score)
            score.color_accent = self._tier_color(score.tier)
        return self.config

    def _calculate_tier(self, score: int) -> str:
        if score >= self.config.prime_threshold:
            return "Prime"
        elif score >= self.config.trusted_threshold:
            return "Trusted"
        elif score >= self.config.monitored_threshold:
            return "Monitored"
        else:
            return "Restricted"

    def _tier_color(self, tier: str) -> str:
        colors = {
            "Prime": "#10b981",
            "Trusted": "#3b82f6",
            "Monitored": "#f59e0b",
            "Restricted": "#ef4444",
        }
        return colors.get(tier, "#94a3b8")

    def _calculate_limit_for_score(self, score: int) -> float:
        # Scale limit linearly between $100 and $1,000 depending on score
        ratio = max(0.0, min(1.0, (score - 300) / (850 - 300)))
        return round(100.0 + ratio * 900.0, 2)

    def adjust_score(self, agent_id: str, event_type: str, reason: str) -> Optional[FICOUpdateResponse]:
        agent_score = self._scores.get(agent_id)
        if not agent_score:
            # Create default for new agent
            agent_score = AgentCreditScore(
                agent_id=agent_id,
                agent_name=agent_id.replace("agent-", "").capitalize() + " Agent",
                fico_score=700,
                tier="Monitored",
                color_accent="#f59e0b",
                dynamic_daily_limit=500.0,
                total_settled_debts=0,
                anomalies_count=0,
                last_adjusted_at=datetime.now(timezone.utc).isoformat(),
            )
            self._scores[agent_id] = agent_score

        old_score = agent_score.fico_score
        old_limit = agent_score.dynamic_daily_limit

        delta = 0
        if event_type == "ON_TIME_REPAYMENT":
            delta = self.config.on_time_repayment_bonus
            agent_score.total_settled_debts += 1
        elif event_type == "BUDGET_DISCIPLINE":
            delta = self.config.budget_discipline_bonus
        elif event_type == "POLICY_ANOMALY":
            delta = -self.config.policy_anomaly_penalty
            agent_score.anomalies_count += 1
        elif event_type == "HIGH_RISK_ATTEMPT":
            delta = -self.config.high_risk_penalty
            agent_score.anomalies_count += 1

        new_score = max(300, min(850, old_score + delta))
        agent_score.fico_score = new_score
        agent_score.tier = self._calculate_tier(new_score)
        agent_score.color_accent = self._tier_color(agent_score.tier)
        agent_score.dynamic_daily_limit = self._calculate_limit_for_score(new_score)
        agent_score.last_adjusted_at = datetime.now(timezone.utc).isoformat()

        return FICOUpdateResponse(
            agent_id=agent_id,
            old_score=old_score,
            new_score=new_score,
            old_limit=old_limit,
            new_limit=agent_score.dynamic_daily_limit,
            tier=agent_score.tier,
            reason=reason,
        )


credit_service = CreditService()
