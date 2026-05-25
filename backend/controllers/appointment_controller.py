from datetime import date
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.appointment import Appointment, AppointmentStatus
from schemas.appointment import AppointmentCreate, AppointmentOut, AppointmentUpdate
from services.booking_service import book_appointment


def create_appointment_controller(payload: AppointmentCreate, db: Session) -> AppointmentOut:
    return book_appointment(
        db,
        name=payload.name,
        phone=payload.phone,
        appt_date=payload.date,
        start_time=payload.start_time,
        notes=payload.notes,
    )


def list_appointments_controller(
    db: Session,
    appt_date: Optional[date] = None,
    status: Optional[AppointmentStatus] = None,
) -> List[AppointmentOut]:
    q = db.query(Appointment)
    if appt_date:
        q = q.filter(Appointment.date == appt_date)
    if status:
        q = q.filter(Appointment.status == status)
    # Order by created_at descending (latest first)
    return q.order_by(Appointment.created_at.desc()).all()


def get_appointment_controller(appt_id: int, db: Session) -> AppointmentOut:
    appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


def update_appointment_controller(appt_id: int, payload: AppointmentUpdate, db: Session) -> AppointmentOut:
    appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(appt, k, v)
    db.commit()
    db.refresh(appt)
    return appt


def cancel_appointment_controller(appt_id: int, db: Session) -> None:
    appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appt.status = AppointmentStatus.cancelled
    db.commit()
