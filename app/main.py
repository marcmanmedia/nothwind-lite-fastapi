from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import EmployeeSalesResponse

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.auth import hash_password, verify_password
from app.token import create_access_token, verify_access_token

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Fake database

#had to re-design fake database user because it will cause serverless function issues
#when hashing at import time. With this approach, dont have to worry about hashing at import time.
#hash will only run only on first login request. Same hash will bereused for future requests 
# (within that instance). And it also prevents the Vercel cold start crash which can happen with the
# free tier.

fake_users_db = None

def get_fake_users():
    global fake_users_db
    if fake_users_db is None:
        fake_users_db = {
            "admin": {
                "username": "admin",
                "hashed_password": hash_password("admin123")
            }
        }
    return fake_users_db

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


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


@app.get("/salesversion2", response_model=EmployeeSalesResponse)
def get_employee_sales(db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):
    result = db.execute(text("SELECT * FROM vw_employee_sales"))
    rows = result.fetchall()
    return {"data": [dict(row._mapping) for row in rows]}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    users_db = get_fake_users()
    user = users_db.get(form_data.username)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user["username"]})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
