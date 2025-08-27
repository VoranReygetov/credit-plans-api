from fastapi import FastAPI
from routers import credits, default

app = FastAPI(title="Credit Plans API") #uvicorn main:app --reload

app.include_router(credits.router)
app.include_router(default.router)

@app.get("/")
def root():
    return {"message": "Credit Plans API"}
