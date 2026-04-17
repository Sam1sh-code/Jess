from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.models.user import User
from app.core.security import get_current_admin, get_current_user, authenticate_user

# ВАЖНО: Префикс начинается с /api/admin
router = APIRouter(prefix="/api/admin", tags=["Админка"])

# Схема для приема новой роли от фронтенда
class RoleUpdate(BaseModel):
    role: str

@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    # Ставим охранника и на получение данных:
    admin_user: User = Depends(get_current_admin)
):
    """Возвращает JSON со всеми пользователями (только для админов)"""
    
    users = db.query(User).all()
    
    # Возвращаем список пользователей. 
    # FastAPI сам превратит объекты SQLAlchemy в JSON для твоей таблицы.
    return users

@router.put("/users/{user_id}/role", dependencies=[Depends(get_current_admin)])
def update_user_role(user_id: int, payload: RoleUpdate, db: Session = Depends(get_db)):
    # Ищем пользователя по ID
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Обновляем роль и сохраняем изменения
    user.role = payload.role
    db.commit()
    
    return {"message": "Роль успешно обновлена", "new_role": user.role}