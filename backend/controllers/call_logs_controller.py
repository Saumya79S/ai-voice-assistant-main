from typing import List

from sqlalchemy.orm import Session

from models.call_log import CallLog
from schemas.call_log import CallLogOut


def list_call_logs_controller(
    db: Session,
    limit: int = 50,
    offset: int = 0,
) -> List[CallLogOut]:
    return (
        db.query(CallLog)
        .order_by(CallLog.start_time.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
