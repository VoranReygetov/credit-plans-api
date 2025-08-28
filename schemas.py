from pydantic import BaseModel
from datetime import date
from typing import Optional


class CreditInfo(BaseModel):
    """Union-like wrapper (either closed or open credit)"""
    issuance_date: date
    is_closed: bool
    actual_return_date: Optional[date] = None
    return_date: Optional[date] = None
    overdue_days: Optional[int] = None
    body: Optional[float] = None
    percent: Optional[float] = None
    total_payments: Optional[float] = None
    body_payments: Optional[float] = None
    percent_payments: Optional[float] = None

    class Config:
        from_attributes = True


class PlanPerformanceOut(BaseModel):
    """Plan performance of the month by a day"""
    month: str
    category: str
    planned_sum: float
    actual_sum: float
    percent_completion: float


class YearPerformanceOut(BaseModel):
    """Year performance by every month"""
    month: str
    credits_count: int
    planned_credits_sum: float
    actual_credits_sum: float
    credits_completion_percent: float
    payments_count: int
    planned_payments_sum: float
    actual_payments_sum: float
    payments_completion_percent: float
    month_credits_share_percent: float
    month_payments_share_percent: float