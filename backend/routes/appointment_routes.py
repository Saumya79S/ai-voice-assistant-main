from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

# from auth.jwt import get_current_user
from const.const import get_current_user

from controllers.appointment_controller import (
    cancel_appointment_controller,
    create_appointment_controller,
    get_appointment_controller,
    list_appointments_controller,
    update_appointment_controller,
)
from database import get_db
from models.appointment import AppointmentStatus
from models.user import User
from schemas.appointment import AppointmentCreate, AppointmentOut, AppointmentUpdate

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("", response_model=AppointmentOut, status_code=201)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        return create_appointment_controller(payload, db)
    except Exception as e:
        raise e


@router.get("", response_model=List[AppointmentOut])
def list_appointments(
    appt_date: Optional[date] = Query(None),
    status: Optional[AppointmentStatus] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return list_appointments_controller(db, appt_date, status)
    except Exception as e:
        raise e


@router.get("/{appt_id}", response_model=AppointmentOut)
def get_appointment(
    appt_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return get_appointment_controller(appt_id, db)
    except Exception as e:
        raise e


@router.patch("/{appt_id}", response_model=AppointmentOut)
def update_appointment(
    appt_id: int,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return update_appointment_controller(appt_id, payload, db)
    except Exception as e:
        raise e


@router.delete("/{appt_id}", status_code=204)
def cancel_appointment(
    appt_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return cancel_appointment_controller(appt_id, db)
    except Exception as e:
        raise e
