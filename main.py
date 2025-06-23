from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from database import get_db_connection
from auth import hash_password, authenticate_user
import re

app = FastAPI()

class User(BaseModel):
    username: str
    password: str = Field(..., min_length=8, max_length=64)

    @validator("password")
    def password_strength(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

@app.post("/register")
def register(user: User):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM admin_users WHERE username = %s", (user.username,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = hash_password(user.password)
    cur.execute("INSERT INTO admin_users (username, password) VALUES (%s, %s)", (user.username, hashed))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "User created successfully"}

@app.get("/protected")
def protected(user: dict = Depends(authenticate_user)):
    return {"message": f"Hello, {user['username']}!"}