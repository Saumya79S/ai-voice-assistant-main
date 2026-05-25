from datetime import date
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# from auth.jwt import get_current_user
from const.const import get_current_user

from controllers.availability_controller import (
    create_or_update_rule_controller,
    delete_rule_controller,
    get_slots_controller,
    list_rules_controller,
    update_rule_controller,
)
from database import get_db
from models.user import User
from schemas.availability import (
    AvailabilityRuleCreate,
    AvailabilityRuleOut,
    AvailabilityRuleUpdate,
    SlotOut,
)

router = APIRouter(prefix="/availability", tags=["availability"])


@router.post("", response_model=AvailabilityRuleOut, status_code=201)
def create_rule(
    payload: AvailabilityRuleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return create_or_update_rule_controller(payload, db)
    except Exception as e:
        raise e


@router.get("", response_model=List[AvailabilityRuleOut])
def list_rules(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    try:
        return list_rules_controller(db)
    except Exception as e:
        raise e


@router.patch("/{rule_id}", response_model=AvailabilityRuleOut)
def update_rule(
    rule_id: int,
    payload: AvailabilityRuleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return update_rule_controller(rule_id, payload, db)
    except Exception as e:
        raise e


@router.delete("/{rule_id}", status_code=204)
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return delete_rule_controller(rule_id, db)
    except Exception as e:
        raise e


@router.get("/slots", response_model=List[SlotOut])
def get_slots(target_date: date, db: Session = Depends(get_db)):
    """Public endpoint — called by AI agent to get available slots."""
    try:
        return get_slots_controller(target_date, db)
    except Exception as e:
        raise e
