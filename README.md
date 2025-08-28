# Credit Plans API

A simple HTTP service for managing users, credits, payments, and monthly plans.  
Implemented with **FastAPI**, **SQLAlchemy**, and **MySQL**.  

---

## Tech Stack
- Python 3.11
- FastAPI
- SQLAlchemy
- MySQL
- Pandas (CSV/Excel processing)

## API Endpoints
*GET /user_credits/{user_id}*

Get all credits for a given user with detailed info (issue date, status, payments, overdue days, etc.).

*POST /plans_insert*

Upload an Excel file with monthly plans.
Validates:

first day of month is correct

no duplicate month + category

no empty "sum" values

*GET /plans_performance?date=DD/MM/YYYY*

Get plan performance up to a specific date:

month

category

planned amount

actual credits/payments

% completed

*GET /year_performance?year=YYYY*

Yearly summary grouped by month:

number of credits and payments

planned vs actual amounts

% of completion

monthly share of yearly totals
