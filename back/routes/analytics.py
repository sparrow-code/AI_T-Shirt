from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional
from controller.analytics import (AdminDashboardStats, AnalyticsController, UserOrderStats)
from controller.auth import get_user_details
from utils.db import db
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
analytics_controller = AnalyticsController(db)


@router.get(
    "/admin/dashboard",
    response_model=AdminDashboardStats,
    summary="Get admin dashboard analytics",
    description="Retrieve comprehensive analytics for admin dashboard with performance optimizations"
)
async def get_admin_dashboard(
    start_date: datetime = Query(
        default_factory=lambda: datetime.utcnow() - timedelta(days=30)
    ),
    end_date: datetime = Query(
        default_factory=lambda: datetime.utcnow()
    ),
    token: str = Depends(oauth2_scheme),
):
    current_user = get_user_details(token, id=True)
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return await analytics_controller.get_admin_dashboard(start_date, end_date)

@router.get(
    "/user/stats",
    response_model=UserOrderStats,
    summary="Get user analytics",
    description="Retrieve personalized analytics for user including order history and preferences"
)
async def get_user_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    token: str = Depends(oauth2_scheme),
):
    current_user = get_user_details(token, id=True)
    return await analytics_controller.get_user_analytics(
        user_id=current_user["id"],
        start_date=start_date,
        end_date=end_date
    )