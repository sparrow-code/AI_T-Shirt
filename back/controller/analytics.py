from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class TimeRangeMetrics(BaseModel):
    total_orders: int
    total_revenue: float
    total_items_sold: int
    average_order_value: float
    total_shipping_cost: float
    total_discounts: float
    net_revenue: float

class ProductPerformance(BaseModel):
    product_id: str
    design_id: str
    total_quantity: int
    total_revenue: float
    popular_sizes: Dict[str, int]
    popular_colors: Dict[str, int]

class SalesOverTime(BaseModel):
    date: datetime
    orders: int
    revenue: float
    items_sold: int

class UserOrderStats(BaseModel):
    total_orders: int
    total_spent: float
    average_order_value: float
    favorite_products: List[ProductPerformance]
    order_history: List[SalesOverTime]
    preferred_sizes: Dict[str, int]
    preferred_colors: Dict[str, int]

class AdminDashboardStats(BaseModel):
    current_period: TimeRangeMetrics
    previous_period: TimeRangeMetrics
    growth_metrics: Dict[str, float]
    top_products: List[ProductPerformance]
    sales_over_time: List[SalesOverTime]
    size_distribution: Dict[str, int]
    color_distribution: Dict[str, int]
    shipping_metrics: Dict[str, float]

# controllers/analytics.py
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import pymongo
from bson import ObjectId

class AnalyticsController:
    def __init__(self, db):
        self.db = db
        self.orders_collection = db["orders"]
        
        # Create indexes for better performance
        self.setup_indexes()
    
    def setup_indexes(self):
        """Setup necessary indexes for faster queries"""
        try:
            # Compound index for date-based queries with user_id
            self.orders_collection.create_index([
                ("created_at", pymongo.DESCENDING),
                ("user_id", pymongo.ASCENDING)
            ])
            
            # Index for status-based queries
            self.orders_collection.create_index("status")
            
            # Index for product and design lookups
            self.orders_collection.create_index([
                ("items.product_id", pymongo.ASCENDING),
                ("items.design_id", pymongo.ASCENDING)
            ])
        except Exception as e:
            print(f"Error setting up indexes: {e}")

    async def get_admin_dashboard(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Get comprehensive admin dashboard analytics"""
        
        pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$facet": {
                    "current_period": [
                        {
                            "$group": {
                                "_id": None,
                                "total_orders": {"$sum": 1},
                                "total_revenue": {"$sum": "$total_amount"},
                                "total_items_sold": {
                                    "$sum": {
                                        "$reduce": {
                                            "input": "$items",
                                            "initialValue": 0,
                                            "in": {"$add": ["$$value", "$$this.quantity"]}
                                        }
                                    }
                                },
                                "total_shipping_cost": {"$sum": "$shipping_cost"},
                                "total_discounts": {"$sum": "$discount_applied"}
                            }
                        }
                    ],
                    "product_performance": [
                        {"$unwind": "$items"},
                        {
                            "$group": {
                                "_id": {
                                    "product_id": "$items.product_id",
                                    "design_id": "$items.design_id"
                                },
                                "total_quantity": {"$sum": "$items.quantity"},
                                "total_revenue": {
                                    "$sum": {
                                        "$multiply": ["$items.quantity", "$items.unit_price"]
                                    }
                                },
                                "sizes": {
                                    "$push": "$items.size"
                                },
                                "colors": {
                                    "$push": "$items.color"
                                }
                            }
                        },
                        {"$sort": {"total_revenue": -1}},
                        {"$limit": 10}
                    ],
                    "daily_sales": [
                        {
                            "$group": {
                                "_id": {
                                    "$dateToString": {
                                        "format": "%Y-%m-%d",
                                        "date": "$created_at"
                                    }
                                },
                                "orders": {"$sum": 1},
                                "revenue": {"$sum": "$total_amount"},
                                "items_sold": {
                                    "$sum": {
                                        "$reduce": {
                                            "input": "$items",
                                            "initialValue": 0,
                                            "in": {"$add": ["$$value", "$$this.quantity"]}
                                        }
                                    }
                                }
                            }
                        },
                        {"$sort": {"_id": 1}}
                    ]
                }
            }
        ]
        
        try:
            result = list(self.orders_collection.aggregate(pipeline))
            if not result:
                raise HTTPException(status_code=404, detail="No data found")
                
            analytics = result[0]
            
            # Calculate previous period metrics
            previous_start = start_date - (end_date - start_date)
            previous_pipeline = [
                {
                    "$match": {
                        "created_at": {
                            "$gte": previous_start,
                            "$lt": start_date
                        }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_orders": {"$sum": 1},
                        "total_revenue": {"$sum": "$total_amount"},
                        "total_items_sold": {
                            "$sum": {
                                "$reduce": {
                                    "input": "$items",
                                    "initialValue": 0,
                                    "in": {"$add": ["$$value", "$$this.quantity"]}
                                }
                            }
                        },
                        "total_shipping_cost": {"$sum": "$shipping_cost"},
                        "total_discounts": {"$sum": "$discount_applied"}
                    }
                }
            ]
            
            previous_period = list(self.orders_collection.aggregate(previous_pipeline))
            
            return {
                "current_period": analytics["current_period"][0],
                "previous_period": previous_period[0] if previous_period else None,
                "top_products": analytics["product_performance"],
                "sales_over_time": analytics["daily_sales"]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_user_analytics(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get user-specific analytics"""
        
        match_stage = {"user_id": user_id}
        if start_date and end_date:
            match_stage["created_at"] = {"$gte": start_date, "$lte": end_date}
            
        pipeline = [
            {"$match": match_stage},
            {
                "$facet": {
                    "overall_stats": [
                        {
                            "$group": {
                                "_id": None,
                                "total_orders": {"$sum": 1},
                                "total_spent": {"$sum": "$total_amount"},
                                "average_order_value": {"$avg": "$total_amount"}
                            }
                        }
                    ],
                    "favorite_products": [
                        {"$unwind": "$items"},
                        {
                            "$group": {
                                "_id": {
                                    "product_id": "$items.product_id",
                                    "design_id": "$items.design_id"
                                },
                                "total_quantity": {"$sum": "$items.quantity"},
                                "total_spent": {
                                    "$sum": {
                                        "$multiply": ["$items.quantity", "$items.unit_price"]
                                    }
                                }
                            }
                        },
                        {"$sort": {"total_quantity": -1}},
                        {"$limit": 5}
                    ],
                    "size_preferences": [
                        {"$unwind": "$items"},
                        {
                            "$group": {
                                "_id": "$items.size",
                                "count": {"$sum": 1}
                            }
                        }
                    ],
                    "color_preferences": [
                        {"$unwind": "$items"},
                        {
                            "$group": {
                                "_id": "$items.color",
                                "count": {"$sum": 1}
                            }
                        }
                    ]
                }
            }
        ]
        
        try:
            result = list(self.orders_collection.aggregate(pipeline))
            if not result:
                raise HTTPException(status_code=404, detail="No data found")
                
            analytics = result[0]
            
            # Convert to response format
            return {
                "overall_stats": analytics["overall_stats"][0],
                "favorite_products": analytics["favorite_products"],
                "preferences": {
                    "sizes": {item["_id"]: item["count"] for item in analytics["size_preferences"]},
                    "colors": {item["_id"]: item["count"] for item in analytics["color_preferences"]}
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))