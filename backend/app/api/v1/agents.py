from typing import List
from fastapi import APIRouter, HTTPException
from ...models.agent import Agent, AgentCreate, AgentUpdate
from ...services.policy_engine import policy_engine

router = APIRouter()


@router.get("", response_model=List[Agent])
async def get_all_agents():
    """Retrieve all registered autonomous agents and their financial limits."""
    return policy_engine.list_agents()


@router.post("", response_model=Agent, status_code=201)
async def create_agent(payload: AgentCreate):
    """Register a new autonomous AI agent with custom policy limits."""
    return policy_engine.create_agent(payload)


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """Retrieve details, wallet balance, and policies of a specific agent."""
    agent = policy_engine.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.patch("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, payload: AgentUpdate):
    """Update agent wallet balance, active status, or policy rules."""
    agent = policy_engine.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if payload.name is not None:
        agent.name = payload.name
    if payload.description is not None:
        agent.description = payload.description
    if payload.wallet_balance is not None:
        agent.wallet_balance = payload.wallet_balance
    if payload.policy is not None:
        agent.policy = payload.policy

    return agent
