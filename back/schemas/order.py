from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

class ProductSize(str, Enum):
    XS = "xs"
    S = "s"
    M = "m"
    L = "l"
    XL = "xl"
    XXL = "xxl"

class ProductColor(str, Enum):
    WHITE = "white"
    BLACK = "black"
    GRAY = "gray"
    RED = "red"
    BLUE = "blue"
    GREEN = "green"

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    PAYPAL = "paypal"
    STRIPE = "stripe"
    STORE_CREDIT = "store_credit"


class ShippingAddress(BaseModel):
    full_name: str
    street_address: str
    city: str
    state: str
    postal_code: str
    country: str
    phone_number: Optional[str] = None

class OrderItemBase(BaseModel):
    product_id: str
    design_id: str
    quantity: int = Field(..., gt=0)
    size: ProductSize
    color: ProductColor
    unit_price: float = Field(..., gt=0)
    
    @validator('quantity')
    def validate_quantity(cls, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        return quantity

class OrderBase(BaseModel):
    user_id: str
    total_amount: float = Field(..., gt=0)
    status: OrderStatus = OrderStatus.PENDING
    payment_method: PaymentMethod
    
    shipping_address: ShippingAddress
    items: List[OrderItemBase]
    
    discount_applied: Optional[float] = 0
    shipping_cost: Optional[float] = 0

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    shipping_tracking_number: Optional[str] = None

class OrderInResponse(OrderBase):
    id: str
    created_at: datetime
    updated_at: datetime
    payment_status: Optional[str] = None
    shipping_tracking_number: Optional[str] = None