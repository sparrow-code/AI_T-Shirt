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

class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    design_id: str
    creator_id: str
    base_price: float = Field(..., gt=0)
    
    sizes_available: List[ProductSize]
    colors_available: List[ProductColor]
    
    stock: Dict[str, int] = Field(default_factory=dict)
    is_active: bool = True
    
    @validator('stock')
    def validate_stock(cls, stock):
        for key, value in stock.items():
            if value < 0:
                raise ValueError(f"Stock for {key} cannot be negative")
        return stock

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None
    sizes_available: Optional[List[ProductSize]] = None
    colors_available: Optional[List[ProductColor]] = None
    stock: Optional[Dict[str, int]] = None
    is_active: Optional[bool] = None

class ProductInResponse(ProductBase):
    pid: str
    created_at: datetime
    updated_at: datetime
    total_sales: int = 0
