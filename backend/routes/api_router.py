from fastapi import APIRouter

from routes import (
    agent_routes,
    appointment_routes,
    availability_routes,
    call_logs_routes,
    user_routes,
    vapi_webhook_routes,
)

router = APIRouter()

router.include_router(user_routes.router)
router.include_router(agent_routes.router)
router.include_router(appointment_routes.router)
router.include_router(availability_routes.router)
router.include_router(call_logs_routes.router)
router.include_router(vapi_webhook_routes.router)
