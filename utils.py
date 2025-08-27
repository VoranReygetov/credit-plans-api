import pandas as pd
from sqlalchemy.orm import Session
import models

def load_users_from_csv(db: Session, file_path: str):
    df = pd.read_csv(file_path, sep='\t', dayfirst=True, parse_dates=['registration_date'])
    users = [
        models.User(
            id=row['id'],
            login=row['login'],
            registration_date=row['registration_date'].date()
        )
        for _, row in df.iterrows()
    ]
    db.bulk_save_objects(users)
    db.commit()

def load_dictionary_from_csv(db: Session, file_path: str):
    df = pd.read_csv(file_path, sep='\t')
    for _, row in df.iterrows():
        entry = models.Dictionary(
            id=row['id'],
            name=row['name']
        )
        db.add(entry)
    db.commit()

def load_plans_from_csv(db: Session, file_path: str):
    df = pd.read_csv(file_path, sep='\t')
    for _, row in df.iterrows():
        plan = models.Plan(
            id=row['id'],
            period=pd.to_datetime(str(row["period"]), dayfirst=True).date(),
            sum=row['sum'],
            category_id=row['category_id']
        )
        db.add(plan)
    db.commit()

def load_credits_from_csv(db: Session, file_path: str):
    df = pd.read_csv(file_path, sep='\t', dayfirst=True,
                     parse_dates=['issuance_date', 'return_date', 'actual_return_date'])
    credits = [
        models.Credit(
            id=row['id'],
            user_id=row['user_id'],
            issuance_date=row['issuance_date'].date(),
            return_date=row['return_date'].date() if pd.notna(row['return_date']) else None,
            actual_return_date=row['actual_return_date'].date() if pd.notna(row['actual_return_date']) else None,
            body=row['body'],
            percent=row['percent']
        )
        for _, row in df.iterrows()
    ]
    db.bulk_save_objects(credits)
    db.commit()

def load_payments_from_csv(db: Session, file_path: str):
    df = pd.read_csv(file_path, sep='\t', dayfirst=True, parse_dates=['payment_date'])
    payments = [
        models.Payment(
            id=row['id'],
            credit_id=row['credit_id'],
            payment_date=row['payment_date'].date(),
            type_id=row['type_id'],
            sum=row['sum']
        )
        for _, row in df.iterrows()
    ]
    db.bulk_save_objects(payments)
    db.commit()
