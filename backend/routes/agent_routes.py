from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# from auth.jwt import get_current_user
from const.const import get_current_user
from controllers.agent_controller import (
    create_agent_controller,
    get_agent_controller,
    list_agents_controller,
    update_agent_controller,
)
from database import get_db
from models.user import User
from schemas.agent import AgentCreate, AgentOut, AgentUpdate

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentOut, status_code=201)
async def create_agent(
    payload: AgentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return await create_agent_controller(payload, db)
    except Exception as e:
        raise e


@router.get("", response_model=list[AgentOut])
def list_agents(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    try:
        return list_agents_controller(db)
    except Exception as e:
        raise e


@router.get("/{agent_id}", response_model=AgentOut)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return get_agent_controller(agent_id, db)
    except Exception as e:
        raise e


@router.patch("/{agent_id}", response_model=AgentOut)
async def update_agent(
    agent_id: int,
    payload: AgentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return await update_agent_controller(agent_id, payload, db)
    except Exception as e:
        raise e
