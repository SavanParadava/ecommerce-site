from fastapi import APIRouter, Depends, HTTPException
from database import get_db_connection
from auth import hash_password, verify_password, create_access_token, authenticate_user
from schemas import User


router = APIRouter()

@router.post("/register")
def register(user: User):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM admin_users WHERE username = %s", (user.username,))
    if cur.fetchone():
        raise HTTPException(400, "Username already exists")
    hashed = hash_password(user.password)
    cur.execute("INSERT INTO admin_users (username, password) VALUES (%s, %s)", (user.username, hashed))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "User created"}

@router.post("/login")
def login(user: User):
    db_user = authenticate_user(user.username, user.password)
    print(db_user)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(data={"username": db_user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}