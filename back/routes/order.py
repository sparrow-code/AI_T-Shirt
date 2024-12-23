from fastapi.security import OAuth2PasswordBearer

from fastapi import APIRouter, Depends, Query, Path
from typing import List
from controller.auth import get_user_details
from schemas.order import (
    OrderInResponse,
    OrderCreate,
    OrderUpdate
)

from controller.order import OrderController
from utils.db import db


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
order_controller = OrderController(db)

@router.post(
    "/",
    response_model=OrderInResponse,
    summary="Create a new order",
    description="""
    Create a new order with the following data:
    - User information
    - Shipping address
    - Order items (products with size, color, quantity)
    - Payment method
    - Discount and shipping cost
    """
)
async def create_order(
    order: OrderCreate,
    token: str = Depends(oauth2_scheme),
):
    """
    Creates a new order in the system.
    
    - Validates all order details
    - Calculates total amount
    - Assigns pending status
    - Records creation timestamp
    """
    return await order_controller.create_order(order)

@router.get(
    "/",
    response_model=List[OrderInResponse],
    summary="Get all orders",
    description="Retrieve orders with pagination. Admins see all orders, users see only their orders."
)
async def get_orders(
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of orders to return"),
    token: str = Depends(oauth2_scheme),
):
    """
    Retrieves a list of orders with pagination.
    
    - Admins: Access to all orders
    - Regular users: Access only to their orders
    - Supports pagination parameters
    """
    current_user = get_user_details(token, id=True)
    return await order_controller.get_orders(
        user_id=str(current_user["_id"]),
        skip=skip,
        limit=limit,
        is_admin=current_user["is_admin"]
    )

@router.get(
    "/{order_id}",
    response_model=OrderInResponse,
    summary="Get order by ID",
    description="Retrieve a specific order by its ID. Users can only access their own orders."
)
async def get_order(
    order_id: str = Path(..., description="The ID of the order to retrieve"),
    token: str = Depends(oauth2_scheme),
):
    """
    Retrieves a specific order by ID.
    
    - Validates user authorization
    - Returns complete order details
    - Includes shipping and payment information
    """
    current_user = get_user_details(token, id=True)
    return await order_controller.get_order_by_id(
        order_id=order_id,
        user_id=str(current_user["_id"]),
        is_admin=current_user["is_admin"]
    )

@router.patch(
    "/{order_id}",
    response_model=OrderInResponse,
    summary="Update order status",
    description="""
    Update order status and tracking information:
    - Admins can update status and tracking number
    - Status can be changed to: processing, shipped, delivered, cancelled, or refunded
    """
)
async def update_order(
    order_update: OrderUpdate,
    order_id: str = Path(..., description="The ID of the order to update"),
    token: str = Depends(oauth2_scheme),
):
    """
    Updates order status and tracking information.
    
    - Validates user permissions
    - Records update timestamp
    - Returns updated order details
    """
    current_user = get_user_details(token, id=True)
    return await order_controller.update_order(
        order_id=order_id,
        order_update=order_update,
        user_id=str(current_user["_id"]),
        is_admin=current_user["is_admin"]
    )