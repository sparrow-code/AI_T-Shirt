from fastapi import APIRouter
from controller.payment import PaymentController

router = APIRouter(prefix="/payment", tags=["Payment"])

@router.get("/create")
async def create_payment():
    return await PaymentController.create_payment()

@router.get("/{status}")
async def payment_status(status: str, session_id: str):
    return await PaymentController.get_status(status, session_id)
