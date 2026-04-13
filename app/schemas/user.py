from pydantic import BaseModel, EmailStr
from typing import Optional

# Что мы ждем от пользователя при регистрации
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    role: str = "client" # client, owner, courier

# Что мы отдаем фронтенду
class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    role: str
    is_active: bool

    class Config:
        from_attributes = True