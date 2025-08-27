from sqlalchemy.orm import Session
from datetime import date
from schemas import CreditInfo, PlanPerformanceOut
import pandas as pd
from sqlalchemy import func
from models import Plan, Credit, Payment, Dictionary, User

def get_user_credits(db: Session, user_id: int) -> list[CreditInfo]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    today = date.today()
    result: list[CreditInfo] = []

    for credit in user.credits:
        payments = credit.payments

        total_payments = sum(p.sum for p in payments)
        body_payments = sum(p.sum for p in payments if p.type.name.lower() == "тіло")
        percent_payments = sum(p.sum for p in payments if p.type.name.lower() == "відсотки")

        if credit.actual_return_date:  # open credit
            result.append(
                CreditInfo(
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
                CreditInfo(
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
        category = db.query(Dictionary).filter(Dictionary.name == row["category"]).first()
        if not category:
            raise ValueError(f"Category '{row['category']}' not found in Dictionary")

        # Check duplicates
        exists = db.query(Plan).filter(
            Plan.period == period,
            Plan.category_id == category.id
        ).first()
        if exists:
            raise ValueError(f"Plan for {period} and category '{row['category']}' already exists")

        new_plans.append(Plan(
            period=period,
            sum=row["sum"],
            category_id=category.id
        ))

    db.bulk_save_objects(new_plans)
    db.commit()
    return len(new_plans)


def get_plans_performance(db: Session, check_date: date):
    results = []

    month_start = check_date.replace(day=1)

    plans = db.query(Plan).filter(Plan.period == month_start).all()
    
    for plan in plans:
        category_name = plan.category.name.lower()
        planned_sum = plan.sum
        actual_sum = 0

        if category_name == "видача":
            actual_sum = db.query(func.sum(Credit.body)).filter(
                Credit.issuance_date >= month_start,
                Credit.issuance_date <= check_date
            ).scalar() or 0
        elif category_name == "збір":
            actual_sum = db.query(func.sum(Payment.sum)).filter(
                Payment.payment_date >= month_start,
                Payment.payment_date <= check_date,
                Dictionary.id == plan.category_id
            ).scalar() or 0

        percent_completion = round((actual_sum / planned_sum) * 100, 2) if planned_sum else 0

        results.append(PlanPerformanceOut(
            month=plan.period.strftime("%Y-%m"),
            category=plan.category.name,
            planned_sum=float(planned_sum),
            actual_sum=float(actual_sum),
            percent_completion=percent_completion
        ))


    return results
