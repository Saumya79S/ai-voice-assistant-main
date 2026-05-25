from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# from auth.jwt import get_current_user
from const.const import get_current_user

from controllers.user_controller import (
    forgot_password_controller,
    get_users_controller,
    login_user_controller,
    register_user_controller,
    resend_verification_controller,
    reset_password_controller,
    verify_code_controller,
)
from database import get_db
from models.user import User
from schemas.user_schema import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    Token,
    UserCreate,
    UserLogin,
    UserRegistrationResponse,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return get_users_controller(db)


@router.post("/register", response_model=UserRegistrationResponse, status_code=201)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return register_user_controller(user, db)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    return login_user_controller(payload, db)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/verify")
def verify_code(
    user_id: int,
    code: str,
    verification_type: str = "email",
    db: Session = Depends(get_db),
):
    return verify_code_controller(user_id, code, verification_type, db)


@router.post("/resend-verification")
def resend_verification(
    user_id: int,
    verification_type: str,
    db: Session = Depends(get_db),
):
    return resend_verification_controller(user_id, verification_type, db)


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return forgot_password_controller(payload, db)


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    return reset_password_controller(payload, db)
