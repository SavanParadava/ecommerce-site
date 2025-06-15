# from fastapi import Depends, FastAPI, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from jose import JWTError, jwt
# from passlib.context import CryptContext
# from datetime import datetime, timedelta
# from pydantic import BaseModel
# import psycopg2
# from psycopg2.extras import RealDictCursor
# from contextlib import asynccontextmanager
# from typing import List



# # Database connection parameters
# DB_HOST = "localhost"
# DB_NAME = "test"
# DB_USER = "postgres"
# DB_PASS = "postgres"

# # Database connection
# def get_db_connection():
#     return psycopg2.connect(
#         host=DB_HOST,
#         database=DB_NAME,
#         user=DB_USER,
#         password=DB_PASS,
#         cursor_factory=RealDictCursor
#     )

# # --- Config for JWT ---
# SECRET_KEY = "your-secret-key"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# # --- Auth Setup ---
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# # --- User Table for Auth ---
# class AuthUser(BaseModel):
#     username: str
#     password: str

# # Token response model
# class Token(BaseModel):
#     access_token: str
#     token_type: str

# # --- Helper Functions ---
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# def get_user_from_db(username: str):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT username, password FROM auth_users WHERE username = %s", (username,))
#     result = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     return result

# def authenticate_user(username: str, password: str):
#     user = get_user_from_db(username)
#     if user and verify_password(password, user["password"]):
#         return {"username": user["username"]}
#     return None

# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=401, detail="Invalid credentials")
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     user = get_user_from_db(username)
#     if user is None:
#         raise HTTPException(status_code=401, detail="User not found")
#     return {"username": username}

# # --- Add table creation in lifespan ---
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS auth_users (
#             username VARCHAR(50) PRIMARY KEY,
#             password TEXT NOT NULL
#         );
#     """)
#     conn.commit()
#     cursor.close()
#     conn.close()
#     yield

# app = FastAPI(lifespan=lifespan)

# # --- Auth Routes ---
# @app.post("/register", status_code=201)
# def register(auth_user: AuthUser):
#     hashed_password = get_password_hash(auth_user.password)
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     try:
#         cursor.execute(
#             "INSERT INTO auth_users (username, password) VALUES (%s, %s)",
#             (auth_user.username, hashed_password)
#         )
#         conn.commit()
#         return {"message": "User registered successfully"}
#     except psycopg2.Error as e:
#         conn.rollback()
#         raise HTTPException(status_code=400, detail="User already exists")
#     finally:
#         cursor.close()
#         conn.close()

# @app.post("/token", response_model=Token)
# def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     access_token = create_access_token(data={"sub": user["username"]})
#     return {"access_token": access_token, "token_type": "bearer"}


# # Pydantic model for User
# class User(BaseModel):
#     id: int | None = None
#     name: str
#     email: str
#     department_id: int | None = None


# @app.get("/users/", response_model=List[User])
# def read_users(current_user: dict = Depends(get_current_user)):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, name, email, department_id FROM users")
#     users = cursor.fetchall()
#     cursor.close()
#     conn.close()
    
#     if users is None:
#         return []  # ✅ Make sure to return an empty list if no users found

#     return users











from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "password123")

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


from fastapi import FastAPI

app = FastAPI()

@app.get("/users/", dependencies=[Depends(get_current_user)])
def read_users():
    # Your logic to return users
    return [{"name": "Alice"}, {"name": "Bob"}]
