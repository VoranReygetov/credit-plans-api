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
