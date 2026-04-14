from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import verify_password, create_access_token
from app.schemas.token import Token
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.core.security import get_password_hash
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Аутентификация"])
templates = Jinja2Templates(directory="frontend")

@router.get('/register')
def regiser_get(request : Request ):
    return templates.TemplateResponse(request=request, name="register.html")

@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    
    user_exists = db.query(User).filter(User.email == user_data.email).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 

            detail="Пользователь с таким email уже существует"
        )
    
    hashed_pwd = get_password_hash(user_data.password)
    
    #Создаем нового пользователя (пароль в хэше)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pwd,
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.get("/login")
def render_login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Ищем пользователя в БД
    # Важно: OAuth2 всегда ждет поле "username", поэтому мы передаем в него наш email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # 2. Если юзера нет или пароли не совпали — выдаем ошибку (одну и ту же для безопасности)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Если всё ок — создаем токен
    access_token = create_access_token(data={"sub": user.email})
    
    # Отдаем токен и данные пользователя, чтобы фронтенд мог их красиво показать
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "email": user.email,
        "full_name": user.full_name
    }