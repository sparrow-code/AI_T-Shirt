from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class StoreAnalytics(BaseModel):
    total_sales: float
    total_orders: int
    average_order_value: float
    top_selling_designs: List[str]
    revenue_by_month: Dict[str, float]
    user_engagement_metrics: Optional[Dict[str, Any]] = None