
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from schemas.product import (
    ProductCreate, 
    ProductUpdate, 
    ProductInResponse
)

from controller.product import ProductService
from controller.auth import get_user_details
from utils.db import db

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
product_service = ProductService(db)

@router.post("/", response_model=ProductInResponse)
async def create_product(
    product: ProductCreate,
    token: str = Depends(oauth2_scheme),
):
    """
    Create a new product
    - Requires authentication
    - Sets the creator_id to the current user
    """

    current_user = get_user_details(token, id=True)
    # Validate and set creator_id
    product_data = product.dict()
    product_data['creator_id'] = str(current_user['_id'])
    
    # Create product
    created_product = await product_service.create_product(product_data)

    return created_product

@router.get("/", response_model=List[ProductInResponse])
async def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    creator_id: Optional[str] = None,
    design_id: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    is_active: Optional[bool] = None
):
    """
    List products with advanced filtering options
    - Supports pagination
    - Optional filtering by creator, design, price range, and active status
    """
    
    # Prepare filter conditions
    filter_conditions = {}
    if creator_id:
        filter_conditions['creator_id'] = creator_id
    if design_id:
        filter_conditions['design_id'] = design_id
    if is_active is not None:
        filter_conditions['is_active'] = is_active
    
    # Price range filter
    if min_price is not None or max_price is not None:
        price_filter = {}
        if min_price is not None:
            price_filter['$gte'] = min_price
        if max_price is not None:
            price_filter['$lte'] = max_price
        if price_filter:
            filter_conditions['base_price'] = price_filter
    
    products = await product_service.list_products(
        filter_conditions, 
        page=page, 
        limit=limit
    )
    return products

@router.get("/{product_id}", response_model=ProductInResponse)
async def get_product(product_id: str):
    """
    Get a specific product by its ID
    """
    product = await product_service.get_product_by_id(product_id)
    return product

@router.put("/{product_id}", response_model=ProductInResponse)
async def update_product(
    product_id: str, 
    product_update: ProductUpdate,
    token: str = Depends(oauth2_scheme)
):
    """
    Update a product
    - Requires authentication
    - Ensures only the creator can update the product
    """
    
    # Check if product exists and get current product
    current_product = await product_service.get_product_by_id(product_id)
   
    # Ensure only creator can update
    current_user = get_user_details(token, id=True)
    if str(current_product['creator_id']) != str(current_user['_id']):
        raise HTTPException(
            status_code=403, 
            detail="Not authorized to update this product"
        )
    
    # Update product
    updated_product = await product_service.update_product(
        product_id, 
        product_update.dict(exclude_unset=True)
    )
    return updated_product

@router.delete("/{product_id}")
async def delete_product(
    product_id: str, 
    token: str = Depends(oauth2_scheme)
):
    """
    Delete a product
    - Requires authentication
    - Ensures only the creator can delete the product
    """
    
    # Check if product exists and get current product
    current_product = await product_service.get_product_by_id(product_id)
    
    # Ensure only creator can delete
    current_user = get_user_details(token, id=True)
    if str(current_product['creator_id']) != str(current_user['_id']):
        raise HTTPException(
            status_code=403, 
            detail="Not authorized to delete this product"
        )
    
    # Delete product
    await product_service.delete_product(product_id)
    return {"message": "Product deleted successfully"}