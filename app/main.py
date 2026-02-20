from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db import get_db

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI layer running"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "healthy"}

@app.get("/sales")
def get_employee_sales(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM vw_employee_sales"))
    rows = result.fetchall()
    return {"data": [dict(row._mapping) for row in rows]}