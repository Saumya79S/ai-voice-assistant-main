from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from config import settings
from models.agent import Agent
from schemas.agent import AgentCreate, AgentOut, AgentUpdate
from services.vapi_service import create_vapi_assistant, update_vapi_assistant


def _agent_response(agent: Agent, vapi_sync_error: Optional[str] = None) -> AgentOut:
    out = AgentOut.model_validate(agent)
    if vapi_sync_error:
        return out.model_copy(update={"vapi_sync_error": vapi_sync_error})
    return out


async def _sync_vapi(agent: Agent, db: Session) -> Optional[str]:
    if not settings.VAPI_API_KEY.strip():
        return "VAPI_API_KEY is empty. Set it in .env at the project root and restart uvicorn."
    try:
        if agent.vapi_assistant_id:
            await update_vapi_assistant(agent.vapi_assistant_id, agent.name, agent.prompt, agent.voice)
            return None
        vapi_id = await create_vapi_assistant(agent.name, agent.prompt, agent.voice)
        if vapi_id:
            agent.vapi_assistant_id = vapi_id
            db.commit()
            db.refresh(agent)
        return None
    except Exception as e:
        return str(e) or repr(e)


async def create_agent_controller(payload: AgentCreate, db: Session) -> AgentOut:
    agent = Agent(**payload.model_dump())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    err = await _sync_vapi(agent, db)
    return _agent_response(agent, err)


def list_agents_controller(db: Session) -> list[AgentOut]:
    return db.query(Agent).all()


def get_agent_controller(agent_id: int, db: Session) -> AgentOut:
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return _agent_response(agent)


async def update_agent_controller(agent_id: int, payload: AgentUpdate, db: Session) -> AgentOut:
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(agent, k, v)
    db.commit()
    db.refresh(agent)
    err = await _sync_vapi(agent, db)
    return _agent_response(agent, err)
