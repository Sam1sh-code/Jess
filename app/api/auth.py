from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.core.security import get_password_hash

router = APIRouter(prefix="/auth", tags=["Аутентификация"])

@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Проверяем нет ли уже юзера с таким email
    user_exists = db.query(User).filter(User.email == user_data.email).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 

            detail="Пользователь с таким email уже существует"
        )
    
    # Хешируем пароль
    hashed_pwd = get_password_hash(user_data.password)
    
    #Создаем нового пользователя (пароль в хэше)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pwd,
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role
    )
    
    # Сохраняем в базу данных
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user