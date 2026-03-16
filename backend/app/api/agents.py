import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.agent import Agent, AgentTask, AgentStatus, TaskStatus
from app.schemas.agent_schema import (
    AgentRegisterRequest,
    AgentResponse,
    HeartbeatResponse,
    TaskLogRequest,
)
from app.api.telemetry import broadcast

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/register", response_model=AgentResponse)
async def register_agent(
    body: AgentRegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "DEVELOPER")),
):
    agent = Agent(
        name=body.name,
        module_type=body.module_type,
        status=AgentStatus.IDLE,
    )
    db.add(agent)
    await db.flush()
    await db.refresh(agent)
    return agent


@router.get("", response_model=list[AgentResponse])
async def list_agents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Agent).order_by(Agent.created_at.desc()))
    return list(result.scalars().all())


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


@router.post("/{agent_id}/heartbeat", response_model=HeartbeatResponse)
async def agent_heartbeat(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    agent.last_heartbeat = datetime.now(timezone.utc)
    await db.flush()
    return HeartbeatResponse()


@router.post("/{agent_id}/logs")
async def agent_logs(
    agent_id: int,
    body: TaskLogRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    task = AgentTask(
        agent_id=agent_id,
        task_description=body.task_description,
        status=body.status,
        execution_time=body.execution_time,
    )
    if body.status == TaskStatus.RUNNING:
        agent.status = AgentStatus.PROCESSING
    elif body.status in (TaskStatus.SUCCESS, TaskStatus.FAILED):
        agent.status = AgentStatus.IDLE
    db.add(task)
    await db.flush()
    asyncio.create_task(
        broadcast.broadcast({
            "type": "task_log",
            "agent_id": agent_id,
            "agent_name": agent.name,
            "task_description": body.task_description,
            "task_status": body.status.value,
        })
    )
    return {"id": task.id, "status": "logged"}
