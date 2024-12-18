from fastapi import HTTPException
from datetime import datetime
from bson import ObjectId
from typing import List, Optional
from schemas.order import (
    OrderCreate,
    OrderUpdate
)
    

class OrderController:
    def __init__(self, db):
        self.db = db
        self.orders_collection = db["orders"]
        self.products_collection = db["products"]
    
    async def create_order(self, order: OrderCreate) -> dict:
        """
        Create a new order in the database with validation and calculations
        """
        order_dict = order.dict()
        
        # Add timestamps and generate ObjectId
        order_dict["_id"] = ObjectId()
        order_dict["created_at"] = datetime.utcnow()
        order_dict["updated_at"] = datetime.utcnow()
        order_dict["payment_status"] = "pending"
        
        # Calculate total amount including shipping and discounts
        subtotal = sum(item.unit_price * item.quantity for item in order.items)
        total = subtotal + order.shipping_cost - order.discount_applied
        
        # Validate total amount matches calculated amount
        if abs(total - order.total_amount) > 0.01:  # Allow small float precision differences
            raise HTTPException(
                status_code=400,
                detail="Total amount doesn't match calculated amount"
            )
        
        # Insert into database
        try:
            result = self.orders_collection.insert_one(order_dict)
            
            # Fetch the created order
            created_order = self.orders_collection.find_one({"_id": result.inserted_id})
            created_order["id"] = str(created_order.pop("_id"))
            return created_order
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_orders(
        self,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        is_admin: bool = False
    ) -> List[dict]:
        """
        Retrieve orders with pagination. Admins can see all orders,
        regular users can only see their own orders.
        """
        try:
            # Build query based on user role
            query = {} if is_admin else {"user_id": user_id}
            
            # Fetch orders with pagination
            cursor = self.orders_collection.find(query).skip(skip).limit(limit)
            orders = []
            
            for order in cursor:
                order["id"] = str(order.pop("_id"))
                orders.append(order)
            
            return orders
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_order_by_id(self, order_id: str, user_id: str, is_admin: bool) -> dict:
        """
        Retrieve a specific order by ID with user authorization check
        """
        try:
            query = {"_id": ObjectId(order_id)}
            if not is_admin:
                query["user_id"] = user_id
                
            order = self.orders_collection.find_one(query)
            
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            order["id"] = str(order.pop("_id"))
            return order
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def update_order(
        self,
        order_id: str,
        order_update: OrderUpdate,
        user_id: str,
        is_admin: bool
    ) -> dict:
        """
        Update order details with role-based permissions
        """
        try:
            # Verify order exists and user has permission
            existing_order = await self.get_order_by_id(order_id, user_id, is_admin)
            
            # Prepare update data
            update_data = {
                k: v for k, v in order_update.dict(exclude_unset=True).items()
                if v is not None
            }
            update_data["updated_at"] = datetime.utcnow()
            
            # Perform update
            result = self.orders_collection.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=400, detail="Order update failed")
            
            # Return updated order
            updated_order = await self.get_order_by_id(order_id, user_id, is_admin)
            return updated_order
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))