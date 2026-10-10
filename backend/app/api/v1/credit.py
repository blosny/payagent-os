from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from ...models.credit import FICOConfig, AgentCreditScore, FICOUpdateResponse
from ...services.credit_service import credit_service

router = APIRouter(prefix="/credit", tags=["AI Fleet FICO Credit"])


class ScoreAdjustmentRequest(BaseModel):
    agent_id: str
    event_type: str  # ON_TIME_REPAYMENT, BUDGET_DISCIPLINE, POLICY_ANOMALY, HIGH_RISK_ATTEMPT
    reason: str


@router.get("/scores", response_model=List[AgentCreditScore])
async def list_scores():
    return credit_service.list_scores()


@router.get("/scores/{agent_id}", response_model=AgentCreditScore)
async def get_score(agent_id: str):
    score = credit_service.get_score(agent_id)
    if not score:
        raise HTTPException(status_code=404, detail="Agent score not found")
    return score


@router.get("/config", response_model=FICOConfig)
async def get_config():
    return credit_service.config


@router.post("/config", response_model=FICOConfig)
async def update_config(config: FICOConfig):
    return credit_service.update_config(config)


@router.post("/adjust", response_model=FICOUpdateResponse)
async def adjust_score(request: ScoreAdjustmentRequest):
    result = credit_service.adjust_score(
        agent_id=request.agent_id,
        event_type=request.event_type,
        reason=request.reason,
    )
    if not result:
        raise HTTPException(status_code=400, detail="Could not adjust score")
    return result
