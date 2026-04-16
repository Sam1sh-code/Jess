from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status, Cookie, Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.core.config import settings
from app.db.database import get_db
from app.models.user import User
from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(request: Request, db: Session = Depends(get_db)):
    
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы. Нет токена."
        )
    
    try:
        # 2. Расшифровываем токен и достаем EMAIL (то, что мы клали в 'sub')
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_email = payload.get("sub")
        
        if user_email is None:
            raise HTTPException(status_code=401, detail="Ошибка: В токене нет email")
            
    except JWTError:
        raise HTTPException(status_code=401, detail="Ошибка: Токен сломан или просрочен")

    # 3. Ищем пользователя по EMAIL!
    user = db.query(User).filter(User.email == user_email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Ошибка: Пользователь не найден в БД")
    
    return user

# 2. ПРОВЕРКА ПРАВ: А есть ли у этого человека доступ?
def get_current_admin(current_user: User = Depends(get_current_user)):
    """
    Эта функция сначала просит get_current_user достать юзера по токену,
    а потом проверяет его должность.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен. Эта территория только для администраторов."
        )
    return current_user

def jwt_get(username: str):
    """ Создание JWT токена    """
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username.email,
        "exp": expire
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def authenticate_user(db: Session, email: str, password: str):
    """
    Проверяет связку email + пароль при попытке входа.
    Возвращает объект User, если всё верно, или False при ошибке.
    """
    # 1. Ищем пользователя по email
    user = db.query(User).filter(User.email == email).first()

    # 2. Если такого email нет в базе
    if not user:
        return False

    # 3. Сверяем введенный пароль с хэшем из базы
    if not verify_password(password, user.hashed_password):
        return False
    
    # 4. Всё совпало! Отдаем объект пользователя
    return user

def get_current_user(
    access_token: str = Cookie(None), 
    db: Session = Depends(get_db)
):
    # 1. Если куки вообще нет
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы (кука не найдена)"
        )

    try:
        # 2. Расшифровываем
        payload = jwt.decode(
            access_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username = payload.get("sub") # У тебя там либо email, либо username

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен пустой (отсутствует sub)"
            )
            
    except JWTError:
        # Сюда попадем, если токен протух, подделан или кривой
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен невалиден или просрочен"
        )

    # 3. Достаем полноценный объект из БД
    # ВАЖНО: фильтруй по тому полю, которое ты клал в "sub" при логине
    user = db.query(User).filter(User.email == username).first() 
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь из токена не найден в базе данных"
        )

    return user