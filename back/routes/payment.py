from fastapi import APIRouter, Depends, HTTPException, Query
from controller.payment import PaymentController
from fastapi.security import OAuth2PasswordBearer
import razorpay
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/payment", tags=["Payment"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class PaymentRequest(BaseModel):
    amount: float
    currency: str = "INR"
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    description: Optional[str] = None

class PaymentResponse(BaseModel):
    payment_link_id: str
    payment_link_url: str
    order_id: str


@app.post("/create", response_model=PaymentResponse)
async def create_payment_link(payment_request: PaymentRequest, token = Depends(oauth2_scheme)):
    return await PaymentController.create_payment(payment_request)

@router.get("/{status}")
async def payment_status(status: str, session_id: str):
    return await PaymentController.get_status(status, session_id)
