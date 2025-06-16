from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from database import get_db_connection
from auth import hash_password, authenticate_user

app = FastAPI()

class User(BaseModel):
    username: str
    password: str

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