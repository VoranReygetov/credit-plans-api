from fastapi import APIRouter, UploadFile, HTTPException, Depends, File
from sqlalchemy.orm import Session
from database import get_db
from crud import insert_plans_from_df, get_plans_performance, get_year_performance
import pandas as pd
from io import BytesIO
from datetime import datetime
from schemas import PlanPerformanceOut, YearPerformanceOut


router = APIRouter(prefix="", tags=["default"])

@router.post("/plans_insert")
async def plans_insert(
    file: UploadFile = File(..., description="Excel file with plans (.xlsx)"),
    db: Session = Depends(get_db)
):
    
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only Excel (.xlsx) files are allowed")

    contents = await file.read()
    df = pd.read_excel(BytesIO(contents))

    required_columns = {"period", "category", "sum"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"File must contain the following columns: {required_columns}")

    try:
        inserted_count = insert_plans_from_df(db, df)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": f"Successfully inserted {inserted_count} plans"}


@router.get("/plans_performance", response_model=list[PlanPerformanceOut])
def plans_performance(check_date: str, db: Session = Depends(get_db)):
    check_date_parsed = datetime.strptime(check_date, "%d/%m/%Y").date()
    return get_plans_performance(db, check_date_parsed)


@router.get("/year_performance", response_model=list[YearPerformanceOut])
def year_performance(year: int, db: Session = Depends(get_db)):
    return get_year_performance(db, year)