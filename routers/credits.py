from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import CreditInfo
from database import get_db
from crud import get_user_credits

router = APIRouter(prefix="/user_credits", tags=["credits"])


@router.get("/{user_id}", response_model=list[CreditInfo], response_model_exclude_none=True)
def user_credits(user_id: int, db: Session = Depends(get_db)):
    credits = get_user_credits(db, user_id)
    if not credits:
        raise HTTPException(status_code=404, detail="User not found or no credits")
    return credits
