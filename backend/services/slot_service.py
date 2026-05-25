from datetime import date, time, datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from models.availability import AvailabilityRule
from models.appointment import Appointment
from schemas.availability import SlotOut


def generate_slots(db: Session, target_date: date) -> List[SlotOut]:
    """
    Generate time slots for a given date based on availability rules,
    marking each as available or booked.
    """
    # day_of_week: Monday=0, Sunday=6 (matches Python's date.weekday())
    day = target_date.weekday()

    rule = (
        db.query(AvailabilityRule)
        .filter(
            AvailabilityRule.day_of_week == day,
            AvailabilityRule.is_active == True,
        )
        .first()
    )

    if not rule:
        return []

    # Fetch booked appointments for this date
    booked = db.query(Appointment).filter(
        Appointment.date == target_date,
        Appointment.status.in_(["pending", "confirmed"]),
    ).all()

    booked_ranges = [(a.start_time, a.end_time) for a in booked]

    slots: List[SlotOut] = []
    current = datetime.combine(target_date, rule.start_time)
    end = datetime.combine(target_date, rule.end_time)
    delta = timedelta(minutes=rule.slot_duration)

    while current + delta <= end:
        slot_start = current.time()
        slot_end = (current + delta).time()

        is_booked = any(
            _times_overlap(slot_start, slot_end, b_start, b_end)
            for b_start, b_end in booked_ranges
        )

        slots.append(
            SlotOut(
                date=target_date.isoformat(),
                start_time=slot_start.strftime("%H:%M"),
                end_time=slot_end.strftime("%H:%M"),
                available=not is_booked,
            )
        )
        current += delta

    return slots


def _times_overlap(s1: time, e1: time, s2: time, e2: time) -> bool:
    return s1 < e2 and e1 > s2


def get_slot_duration_for_date(db: Session, target_date: date) -> int:
    day = target_date.weekday()
    rule = (
        db.query(AvailabilityRule)
        .filter(AvailabilityRule.day_of_week == day, AvailabilityRule.is_active == True)
        .first()
    )
    return rule.slot_duration if rule else 30
