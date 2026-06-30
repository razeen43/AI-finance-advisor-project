from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

from database import users_col

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey123")
ALGORITHM = "HS256"


class RegisterUser(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginUser(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
async def register(user: RegisterUser):
    existing_user = await users_col.find_one({"email": user.email})

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)

    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    }

    await users_col.insert_one(new_user)

    return {"message": "User registered successfully"}


@router.post("/login")
async def login(user: LoginUser):
    db_user = await users_col.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token_data = {
        "sub": str(db_user["_id"]),
        "email": db_user["email"],
        "exp": datetime.utcnow() + timedelta(days=1)
    }

    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": token,
        "token_type": "bearer"
    }