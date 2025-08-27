from sqlalchemy.orm import Session
from datetime import date
import models, schemas
import pandas as pd

def get_user_credits(db: Session, user_id: int) -> list[schemas.CreditInfo]:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return []

    today = date.today()
    result: list[schemas.CreditInfo] = []

    for credit in user.credits:
        payments = credit.payments

        total_payments = sum(p.sum for p in payments)
        body_payments = sum(p.sum for p in payments if p.type.name.lower() == "тіло")
        percent_payments = sum(p.sum for p in payments if p.type.name.lower() == "відсотки")

        if credit.actual_return_date:  # open credit
            result.append(
                schemas.CreditInfo(
                    issuance_date=credit.issuance_date,
                    is_closed=True,
                    actual_return_date=credit.actual_return_date,
                    body=float(credit.body),
                    percent=float(credit.percent),
                    total_payments=float(total_payments),
                )
            )
        else:  # closed credit
            overdue_days = 0
            if credit.return_date and today > credit.return_date:
                overdue_days = (today - credit.return_date).days

            result.append(
                schemas.CreditInfo(
                    issuance_date=credit.issuance_date,
                    is_closed=False,
                    return_date=credit.return_date,
                    overdue_days=overdue_days,
                    body=float(credit.body),
                    percent=float(credit.percent),
                    body_payments=float(body_payments),
                    percent_payments=float(percent_payments),
                )
            )

    return result


def insert_plans_from_df(db: Session, df: pd.DataFrame):
    new_plans = []
    for _, row in df.iterrows():
        # Validate date
        period = pd.to_datetime(str(row["period"]), dayfirst=True).date()
        print(period, period.day)
        if period.day != 1:
            raise ValueError(f"Plan period {period} must be the first day of the month")

        if pd.isna(row["sum"]):
            raise ValueError("Column 'sum' cannot contain empty values")

        # Find category
        category = db.query(models.Dictionary).filter(models.Dictionary.name == row["category"]).first()
        if not category:
            raise ValueError(f"Category '{row['category']}' not found in Dictionary")

        # Check duplicates
        exists = db.query(models.Plan).filter(
            models.Plan.period == period,
            models.Plan.category_id == category.id
        ).first()
        if exists:
            raise ValueError(f"Plan for {period} and category '{row['category']}' already exists")

        new_plans.append(models.Plan(
            period=period,
            sum=row["sum"],
            category_id=category.id
        ))

    db.bulk_save_objects(new_plans)
    db.commit()
    return len(new_plans)