from sqlalchemy.orm import Session
from datetime import date, timedelta
from schemas import CreditInfo, PlanPerformanceOut, YearPerformanceOut
import pandas as pd
from sqlalchemy import func, extract
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


def get_year_performance(db: Session, year: int):

    # Get all plans for the given year
    plans = db.query(Plan).filter(
        extract("year", Plan.period) == year
    ).all()

    # Get all credits issued in the given year
    credits = db.query(Credit).filter(
        extract("year", Credit.issuance_date) == year
    ).all()

    # Get all payments made in the given year
    payments = db.query(Payment).filter(
        extract("year", Payment.payment_date) == year
    ).all()

    # Calculate total sums for the entire year
    total_credits_sum = sum(c.body for c in credits)
    total_payments_sum = sum(p.sum for p in payments)

    results = []
    for month in range(1, 12 + 1):
        # Get start and end date for the current month
        month_start = date(year, month, 1)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        # Select plans for the current month
        month_plans = [p for p in plans if p.period.month == month]

        # Planned amounts (by category)
        planned_credits_sum = sum(p.sum for p in month_plans if p.category_id == 3)  # "Видача"
        planned_payments_sum = sum(p.sum for p in month_plans if p.category_id == 4)  # "Збір"

        # Actual credits and payments for the current month
        month_credits = [c for c in credits if month_start <= c.issuance_date <= month_end]
        month_payments = [p for p in payments if month_start <= p.payment_date <= month_end]

        actual_credits_sum = sum(c.body for c in month_credits)
        actual_payments_sum = sum(p.sum for p in month_payments)

        # Build monthly result entry
        results.append(YearPerformanceOut(
            month=f"{year}-{month:02d}",
            credits_count=len(month_credits),
            planned_credits_sum=float(planned_credits_sum),
            actual_credits_sum=float(actual_credits_sum),
            credits_completion_percent=round((actual_credits_sum / planned_credits_sum * 100), 2) if planned_credits_sum else 0,
            payments_count=len(month_payments),
            planned_payments_sum=float(planned_payments_sum),
            actual_payments_sum=float(actual_payments_sum),
            payments_completion_percent=round((actual_payments_sum / planned_payments_sum * 100), 2) if planned_payments_sum else 0,
            month_credits_share_percent=round((actual_credits_sum / total_credits_sum * 100), 2) if total_credits_sum else 0,
            month_payments_share_percent=round((actual_payments_sum / total_payments_sum * 100), 2) if total_payments_sum else 0,
        ))

    return results
