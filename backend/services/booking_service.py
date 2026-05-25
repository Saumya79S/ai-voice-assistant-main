from datetime import date, time, datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.appointment import Appointment, AppointmentStatus
from models.availability import AvailabilityRule
from services.slot_service import generate_slots


def book_appointment(
    db: Session,
    name: str,
    phone: str,
    appt_date: date,
    start_time: time,
    notes: str = None,
) -> Appointment:
    # Enforce year >= 2026
    if appt_date.year < 2026:
        appt_date = appt_date.replace(year=2026)
    # Prevent booking in the past
    from datetime import date as dt_date
    if appt_date < dt_date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment date cannot be in the past.",
        )

    # Validate the slot is available
    slots = generate_slots(db, appt_date)
    slot_map = {s.start_time: s for s in slots}
    time_str = start_time.strftime("%H:%M")

    if time_str not in slot_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No slot available at {time_str} on {appt_date}",
        )

    slot = slot_map[time_str]
    if not slot.available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Slot {time_str} on {appt_date} is already booked",
        )

    end_time = datetime.strptime(slot.end_time, "%H:%M").time()

    appointment = Appointment(
        name=name,
        phone=phone,
        date=appt_date,
        start_time=start_time,
        end_time=end_time,
        status=AppointmentStatus.confirmed,
        notes=notes,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment
