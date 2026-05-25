from datetime import date
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.availability import AvailabilityRule
from schemas.availability import (
    AvailabilityRuleCreate,
    AvailabilityRuleOut,
    AvailabilityRuleUpdate,
    SlotOut,
)
from services.slot_service import generate_slots


def create_or_update_rule_controller(payload: AvailabilityRuleCreate, db: Session) -> AvailabilityRuleOut:
    existing = db.query(AvailabilityRule).filter(
        AvailabilityRule.day_of_week == payload.day_of_week
    ).first()
    if existing:
        for k, v in payload.model_dump().items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    rule = AvailabilityRule(**payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def list_rules_controller(db: Session) -> List[AvailabilityRuleOut]:
    return db.query(AvailabilityRule).order_by(AvailabilityRule.day_of_week).all()


def update_rule_controller(rule_id: int, payload: AvailabilityRuleUpdate, db: Session) -> AvailabilityRuleOut:
    rule = db.query(AvailabilityRule).filter(AvailabilityRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(rule, k, v)
    db.commit()
    db.refresh(rule)
    return rule


def delete_rule_controller(rule_id: int, db: Session) -> None:
    rule = db.query(AvailabilityRule).filter(AvailabilityRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()


def get_slots_controller(target_date: date, db: Session) -> List[SlotOut]:
    return generate_slots(db, target_date)
