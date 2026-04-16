from fastapi import APIRouter, Depends, Form, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import verify_password, create_access_token
from app.schemas.token import Token
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.core.security import get_password_hash, jwt_get, authenticate_user
from fastapi.templating import Jinja2Templates
from app.core.config import settings
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/api/auth", tags=["Аутентификация"])
templates = Jinja2Templates(directory="frontend")

from fastapi import APIRouter, Depends, HTTPException, status, Form # Добавили Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
# ... твои импорты моделей и хеширования ...

@router.post("/register") # Убрали response_model, так как делаем редирект
def register(
    # Принимаем данные как форму, а не как JSON
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    phone: str = Form(None), # Опционально
    role: str = Form("user"), # По дефолту юзер
    db: Session = Depends(get_db)
):
    # 1. Проверка на существование
    user_exists = db.query(User).filter(User.email == email).first()
    if user_exists:
        # Тут лучше вернуть ошибку на страницу регистрации, 
        # но для дебага пока оставим так:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # 2. Хешируем и создаем
    hashed_pwd = get_password_hash(password)
    
    new_user = User(
        email=email,
        hashed_password=hashed_pwd,
        full_name=full_name,
        phone=phone,
        role=role
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        print(f"Ошибка БД: {e}")
        raise HTTPException(status_code=500, detail="Ошибка базы данных")
    
    # 3. Редирект на логин! 
    # Статус 303 нужен, чтобы POST превратился в GET при переходе
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    
    user = authenticate_user(db, username, password)

    if not user: 
        raise HTTPException(status_code=401, detail="Wrong password or username")
    
    access_token = jwt_get(user)

    response = RedirectResponse(url="/profile", status_code=302)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        path="/",
        max_age= settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return response