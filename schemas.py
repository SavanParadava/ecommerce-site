from pydantic import BaseModel, Field, validator
from typing import Optional
import re

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

class Contact(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None