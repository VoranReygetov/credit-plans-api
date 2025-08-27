from fastapi import FastAPI
from routers import credits

app = FastAPI(title="Credit Plans API") #uvicorn main:app --reload

app.include_router(credits.router)

@app.get("/")
def root():
    return {"message": "Credit Plans API"}
