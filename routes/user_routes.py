from fastapi import APIRouter, Depends
from auth import get_current_user
from database import get_db_connection
from schemas import User
from typing import List

router = APIRouter()

@router.get("/users/me")
def get_profile(user: dict = Depends(get_current_user)):
    return user

# Read all users
@router.get("/users/", response_model=List[User])
def read_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin_users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users