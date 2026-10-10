from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status

from ...models.arbitrage import (
    BiddingRequest,
    BiddingCompetitionResult,
    ArbitrageExecutionRequest,
    ArbitrageExecutionRecord,
    LiquidityRebalanceRequest,
    LiquidityRebalanceResult,
)
from ...services.arbitrage_engine import arbitrage_engine

router = APIRouter()


@router.get("/rates")
async def get_market_spot_rates():
    """
    Returns live spot pricing board for cloud & AI compute instances (AWS, Cloudflare, HuggingFace, RunPod, DeepInfra).
    """
    return arbitrage_engine.get_market_spot_rates()


@router.post("/bids/solicit", response_model=BiddingCompetitionResult)
async def solicit_provider_bids(request: BiddingRequest):
    """
    Solicits real-time competitive quotes across providers for a specified compute workload.
    Selects optimal provider based on agent's strategy (Cost, Speed, Balanced) and computes arbitrage alpha.
    """
    try:
        result = arbitrage_engine.solicit_quotes(request)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/bids/execute", response_model=ArbitrageExecutionRecord)
async def execute_winning_bid(request: ArbitrageExecutionRequest):
    """
    Executes autonomous PayPal payment for the winning quote, registers transaction in audit log,
    and captures savings for the treasury.
    """
    try:
        record = await arbitrage_engine.execute_winning_bid(request)
        return record
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/rebalance", response_model=LiquidityRebalanceResult)
async def rebalance_liquidity(request: LiquidityRebalanceRequest):
    """
    Autonomous portfolio & day/night liquidity rebalancer. Transfers unused quota from idle agents
    to active nocturnal heavy-compute agents.
    """
    try:
        result = arbitrage_engine.rebalance_portfolio_liquidity(request)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/history")
async def get_arbitrage_history():
    """
    Returns history of spot bid executions and liquidity rebalance actions with cumulative savings.
    """
    executions = arbitrage_engine.list_executions()
    rebalances = arbitrage_engine.list_rebalances()
    total_saved = arbitrage_engine.get_total_arbitrage_saved()

    return {
        "total_arbitrage_saved": round(total_saved, 2),
        "total_executions_count": len(executions),
        "total_rebalances_count": len(rebalances),
        "executions": [e.model_dump() for e in executions],
        "rebalances": [r.model_dump() for r in rebalances],
    }
