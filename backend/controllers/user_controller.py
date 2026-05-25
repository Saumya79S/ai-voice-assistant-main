import hashlib
import logging
import random
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# from auth.jwt import create_access_token, verify_password
from const.const import create_access_token, create_refresh_token, get_password_hash, verify_password
from config import settings
from const.const import create_error, create_refresh_token, get_password_hash
from models.password_reset import PasswordResetToken
from models.user import User
from models.verification_models import VerificationCode
from schemas.user_schema import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    Token,
    UserCreate,
    UserLogin,
    UserRegistrationResponse,
    UserResponse,
)
from services.password_reset_email import send_password_reset_email

logger = logging.getLogger(__name__)

_GENERIC_FORGOT_MSG = (
    "If that email is registered, you will receive password reset instructions shortly."
)


def get_users_controller(db: Session) -> list[UserResponse]:
    return db.query(User).all()


def register_user_controller(user: UserCreate, db: Session) -> UserRegistrationResponse:
    if db.query(User).filter(User.email == user.email).first():
        raise create_error(400, "Email already registered")

    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        password_hash=hashed_password,
        phone=user.phone_number if user.phone_number else None,
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        error_text = str(getattr(exc, "orig", exc)).lower()
        if "email" in error_text:
            raise create_error(400, "Email already registered")
        if "phone" in error_text:
            raise create_error(400, "Phone number already registered")
        raise create_error(500, "Failed to register user")
    db.refresh(new_user)

    email_code = generate_verification_code(new_user.id, db, "email")
    # TODO: send_verification_email(new_user.email, email_code)
    logger.info("DEV — email verification code for %s: %s", new_user.email, email_code)

    if user.phone_number:
        sms_code = generate_verification_code(new_user.id, db, "sms")
        # TODO: send_verification_sms(user.phone_number, sms_code)
        logger.info("DEV — SMS verification code for %s: %s", user.phone_number, sms_code)

    return new_user


def verify_code_controller(user_id: int, code: str, verification_type: str, db: Session) -> dict:
    verification = (
        db.query(VerificationCode)
        .filter(
            VerificationCode.user_id == user_id,
            VerificationCode.token == code,
            VerificationCode.type == verification_type,
        )
        .first()
    )

    if verification is None:
        raise create_error(400, "Invalid verification code")

    if verification.expiration < datetime.utcnow():
        db.delete(verification)
        db.commit()
        raise create_error(400, "Verification code expired")

    db.delete(verification)
    db.commit()
    return {"message": f"{verification_type} verified successfully"}


def resend_verification_controller(user_id: int, verification_type: str, db: Session) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise create_error(404, "User not found")

    db.query(VerificationCode).filter(
        VerificationCode.user_id == user_id,
        VerificationCode.type == verification_type,
    ).delete()
    db.commit()

    code = generate_verification_code(user_id, db, verification_type)

    if verification_type == "email":
        # TODO: send_verification_email(user.email, code)
        logger.info("DEV — resend email verification code for %s: %s", user.email, code)
    elif verification_type == "sms":
        if not user.phone:
            raise create_error(400, "User does not have a phone number")
        # TODO: send_verification_sms(user.phone, code)
        logger.info("DEV — resend SMS verification code for %s: %s", user.phone, code)
    else:
        raise create_error(400, "Invalid verification type")

    return {"message": "Verification code resent"}


# ── Helpers ────────────────────────────────────────────────────────────────────

def generate_verification_code(user_id: int, db: Session, verification_type: str) -> str:
    code = str(random.randint(100000, 999999))
    expiration = datetime.utcnow() + timedelta(minutes=10)
    db.add(VerificationCode(token=code, expiration=expiration, user_id=user_id, type=verification_type))
    db.commit()
    return code


def send_verification_email(email: str, code: str) -> None:
    email_user = settings.EMAIL_USER if hasattr(settings, "EMAIL_USER") else None
    email_password = settings.EMAIL_PASSWORD if hasattr(settings, "EMAIL_PASSWORD") else None

    if not email_user or not email_password:
        raise create_error(500, "Email service is not configured")

    message = MIMEText(f"Your verification code is: {code}\nThis code expires in 10 minutes.")
    message["Subject"] = "Email Verification Code"
    message["From"] = email_user
    message["To"] = email

    try:
        with smtplib.SMTP(settings.SMTP_HOST if hasattr(settings, "SMTP_HOST") else "smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_user, email_password)
            server.send_message(message)
    except smtplib.SMTPAuthenticationError:
        raise create_error(500, "Gmail authentication failed. Use an App Password in EMAIL_PASSWORD.")
    except smtplib.SMTPException:
        raise create_error(502, "Failed to send verification email")


def send_verification_sms(phone_number: str, code: str) -> None:
    # TODO: integrate Twilio
    pass


# ── Auth controllers ────────────────────────────────────────────────────────────

def login_user_controller(payload: UserLogin, db: Session) -> Token:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    return Token(access_token=access_token, refresh_token=refresh_token)


def forgot_password_controller(payload: ForgotPasswordRequest, db: Session) -> dict:
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id
        ).delete(synchronize_session=False)
        raw = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw.encode()).hexdigest()
        expires = datetime.now(timezone.utc) + timedelta(hours=settings.PASSWORD_RESET_TOKEN_HOURS)
        db.add(PasswordResetToken(user_id=user.id, token_hash=token_hash, expires_at=expires))
        db.commit()
        reset_url = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={raw}"
        if not send_password_reset_email(user.email, reset_url):
            if settings.ENVIRONMENT == "development":
                logger.warning("Password reset link (configure SMTP to email users): %s", reset_url)
    return {"detail": _GENERIC_FORGOT_MSG}


def reset_password_controller(payload: ResetPasswordRequest, db: Session) -> dict:
    token_hash = hashlib.sha256(payload.token.encode()).hexdigest()
    row = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.expires_at > datetime.now(timezone.utc),
        )
        .first()
    )
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset link. Request a new one from the login page.",
        )
    user = db.query(User).filter(User.id == row.user_id).first()
    if not user:
        db.delete(row)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset link.",
        )
    user.password_hash = get_password_hash(payload.new_password)
    db.delete(row)
    db.commit()
    return {"detail": "Password updated. You can sign in."}
