from typing import Dict, List, Any
from bson import ObjectId
from fastapi import HTTPException

from datetime import datetime

class ProductService:
    def __init__(self, db):
        self.db = db
        self.collection = db["products"]
    
    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new product
        - Adds creation and update timestamps
        - Generates ObjectId
        """
        now = datetime.utcnow()
        product_data['created_at'] = now
        product_data['updated_at'] = now
        product_data['total_sales'] = 0
        
        # Insert product
        result = self.collection.insert_one(product_data)

        # Retrieve and return the inserted product
        product = self.collection.find_one({"_id": result.inserted_id})
        product['pid'] = "PID_" +  str(product.pop('_id'))
        return product
    
    async def get_product_by_id(self, product_id: str) -> Dict[str, Any]:
        """
        Retrieve a product by its ID
        - Converts ObjectId to string for response
        """
        product = self.collection.find_one({"_id": ObjectId(product_id)})
        
        if not product:
            raise HTTPException(
                status_code=404, 
                detail="Product not found"
            )
        
        product['pid'] = "PID_" + str(product['_id'])
        return product
    
    async def list_products(
        self, 
        filter_conditions: Dict[str, Any] = {},
        page: int = 1, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        List products with pagination and filtering
        - Supports complex query conditions
        """
        skip = (page - 1) * limit
        
        # Find products with pagination
        cursor = self.collection.find(filter_conditions)
        products = cursor.skip(skip).limit(limit).to_list(limit)
        
        # Convert ObjectId to string
        for product in products:
            product['pid'] = "PID_" + str(product['_id'])
        
        return products
    
    async def update_product(
        self, 
        product_id: str, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a product
        - Updates timestamp
        - Supports partial updates
        """
        # Add updated_at timestamp
        update_data['updated_at'] = datetime.utcnow()
        
        # Perform update
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(product_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if not result:
            raise HTTPException(
                status_code=404, 
                detail="Product not found"
            )
        
        result['_id'] = str(result['_id'])
        return result
    
    async def delete_product(self, product_id: str):
        """
        Delete a product
        """
        result = await self.collection.delete_one({"_id": ObjectId(product_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404, 
                detail="Product not found"
            )
        
        return True
    
    async def update_product_stock(
        self, 
        product_id: str, 
        size: str, 
        color: str, 
        quantity_sold: int
    ):
        """
        Update product stock after a sale
        """
        stock_key = f"stock.{size}_{color}"
        
        result = await self.collection.update_one(
            {"_id": ObjectId(product_id)},
            {
                "$inc": {
                    stock_key: -quantity_sold,
                    "total_sales": quantity_sold
                }
            }
        )
        
        return result.modified_count > 0