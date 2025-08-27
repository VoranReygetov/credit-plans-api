from sqlalchemy.orm import Session
from datetime import date
import models, schemas


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

        if credit.actual_return_date:  # закритий
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
        else:  # відкритий
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
