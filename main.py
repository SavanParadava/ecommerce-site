from fastapi import FastAPI, HTTPException
from typing import List
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import asynccontextmanager
from pydantic import BaseModel, EmailStr, Field, constr

# Database connection parameters
DB_HOST = "localhost"
DB_NAME = "test"
DB_USER = "postgres"
DB_PASS = "postgres"

# Pydantic model for User
class User(BaseModel):
    id: int | None = None
    name: constr(strip_whitespace=True, min_length=1, max_length=100)
    email: EmailStr
    department_id: int | None = Field(default=None, ge=1)

class Department(BaseModel):
    id: int | None = None
    name: constr(strip_whitespace=True, min_length=1, max_length=100)

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        cursor_factory=RealDictCursor
    )

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create table if not exists
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE
    );""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            department_id INT,
            CHECK (char_length(name) >= 1),
            FOREIGN KEY (department_id) REFERENCES departments(id)
                ON DELETE SET NULL
                ON UPDATE CASCADE

        );
    """)
    conn.commit()
    cursor.close()
    conn.close()
    yield
    # Shutdown: No cleanup needed in this case

app = FastAPI(lifespan=lifespan)

# Create user
@app.post("/users/", response_model=User)
def create_user(user: User):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, department_id) VALUES (%s, %s, %s) RETURNING id, name, email, department_id",
            (user.name, user.email, user.department_id)
        )
        new_user = cursor.fetchone()
        conn.commit()
        return new_user
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# Create department
@app.post("/departments/", response_model=Department)
def create_department(dep: Department):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO departments (name) VALUES (%s) RETURNING id, name",
            (dep.name,)
        )
        new_dep = cursor.fetchone()
        conn.commit()
        return new_dep
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# Read all users
@app.get("/users/", response_model=List[User])
def read_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, department_id FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

# Read all departments
@app.get("/departments/",response_model=List[Department])
def read_departments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select id, name from departments")
    deps = cursor.fetchall()
    cursor.close()
    conn.close()
    return deps

# Read single user
@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update user
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: User):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET name = %s, email = %s, department_id = %s WHERE id = %s RETURNING id, name, email, department_id",
            (user.name, user.email, user_id)
        )
        updated_user = cursor.fetchone()
        conn.commit()
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# Delete user
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s RETURNING id", (user_id,))
    deleted_user = cursor.fetchone()
    conn.commit()
    if deleted_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    cursor.close()
    conn.close()
    return {"message": "User deleted successfully"}


# Delete department
@app.delete("/departments/{dep_id}")
def delete_user(dep_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM departments WHERE id = %s RETURNING id", (dep_id,))
    deleted_dep = cursor.fetchone()
    conn.commit()
    if deleted_dep is None:
        raise HTTPException(status_code=404, detail="Department not found")
    cursor.close()
    conn.close()
    return {"message": "Department deleted successfully"}












# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import List
# import psycopg2
# from psycopg2.extras import RealDictCursor
# from contextlib import asynccontextmanager

# # Database connection parameters
# DB_HOST = "localhost"
# DB_NAME = "test"
# DB_USER = "postgres"
# DB_PASS = "postgres"

# # Pydantic model for User
# class User(BaseModel):
#     id: int | None = None
#     name: str
#     email: str

# # Database connection
# def get_db_connection():
#     return psycopg2.connect(
#         host=DB_HOST,
#         database=DB_NAME,
#         user=DB_USER,
#         password=DB_PASS,
#         cursor_factory=RealDictCursor
#     )

# # Lifespan event handler
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup: Create table if not exists
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id SERIAL PRIMARY KEY,
#             name VARCHAR(100) NOT NULL,
#             email VARCHAR(100) UNIQUE NOT NULL
#         )
#     """)
#     conn.commit()
#     cursor.close()
#     conn.close()
#     yield
#     # Shutdown: No cleanup needed in this case

# app = FastAPI(lifespan=lifespan)

# # Create user
# @app.post("/users/", response_model=User)
# def create_user(user: User):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     try:
#         cursor.execute(
#             "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id, name, email",
#             (user.name, user.email)
#         )
#         new_user = cursor.fetchone()
#         conn.commit()
#         return new_user
#     except psycopg2.Error as e:
#         conn.rollback()
#         raise HTTPException(status_code=400, detail=str(e))
#     finally:
#         cursor.close()
#         conn.close()

# # Read all users
# @app.get("/users/", response_model=List[User])
# def read_users():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, name, email FROM users")
#     users = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return users

# # Read single user
# @app.get("/users/{user_id}", response_model=User)
# def read_user(user_id: int):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
#     user = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

# # Update user
# @app.put("/users/{user_id}", response_model=User)
# def update_user(user_id: int, user: User):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     try:
#         cursor.execute(
#             "UPDATE users SET name = %s, email = %s WHERE id = %s RETURNING id, name, email",
#             (user.name, user.email, user_id)
#         )
#         updated_user = cursor.fetchone()
#         conn.commit()
#         if updated_user is None:
#             raise HTTPException(status_code=404, detail="User not found")
#         return updated_user
#     except psycopg2.Error as e:
#         conn.rollback()
#         raise HTTPException(status_code=400, detail=str(e))
#     finally:
#         cursor.close()
#         conn.close()

# # Delete user
# @app.delete("/users/{user_id}")
# def delete_user(user_id: int):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM users WHERE id = %s RETURNING id", (user_id,))
#     deleted_user = cursor.fetchone()
#     conn.commit()
#     if deleted_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     cursor.close()
#     conn.close()
#     return {"message": "User deleted successfully"}


