from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from const.const import get_current_user
from controllers.call_logs_controller import list_call_logs_controller
from database import get_db
from models.user import User
from schemas.call_log import CallLogOut

router = APIRouter(prefix="/call-logs", tags=["call-logs"])


@router.get("", response_model=List[CallLogOut])
def list_call_logs(
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return list_call_logs_controller(db, limit, offset)
    except Exception as e:
        raise e
