from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from utils import load_users_from_csv, load_dictionary_from_csv, load_payments_from_csv, load_plans_from_csv, load_credits_from_csv

Base.metadata.create_all(bind=engine)

db: Session = SessionLocal()

load_users_from_csv(db, "data/users.csv")
load_dictionary_from_csv(db, "data/dictionary.csv")
load_credits_from_csv(db, "data/credits.csv")
load_payments_from_csv(db, "data/payments.csv")
load_plans_from_csv(db, "data/plans.csv")

