from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router 
from app.api.admin import router as admin_router
from app.api.restaurants import router as restaurant_router
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.core.security import get_current_admin, get_current_user, get_owner_or_admin
from app.models.user import User
from app.models.order import Order, OrderItem
from app.api.orders import router as orders_router
from app.api.courier import courier_router 
from sqlalchemy.orm import joinedload
from app.db.database import get_db
from app.models.restaurant import Restaurant
from app.models.menu import Category
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse

app = FastAPI()

templates = Jinja2Templates(directory="frontend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # В продакшене тут будут конкретные домены, а пока разрешаем все
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(restaurant_router)
app.include_router(admin_router)
app.include_router(orders_router)
app.include_router(courier_router)

#Разрешаем раздавать файлы из папки статик
app.mount("/static", StaticFiles(directory="static"), name="static")



@app.get("/")
def render_home_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")



@app.get("/admin")
def render_admin_page(request: Request, admin_user: User = Depends(get_current_admin)):
    return templates.TemplateResponse(request=request, name="admin_users.html")

@app.get('/register')
def regiser_get(request : Request ):
    return templates.TemplateResponse(request=request, name="register.html")

@app.get("/login")
def render_login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

from sqlalchemy.orm import joinedload

@app.get("/profile")
def get_profile(
    request: Request, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    # Получаем все заказы пользователя от новых к старым
    orders = db.query(Order).options(
        joinedload(Order.restaurant),    # Чтобы знать, откуда еда
        joinedload(Order.items).joinedload(OrderItem.item) # Чтобы видеть список блюд
    ).filter(
        Order.user_id == user.id,
        Order.status != "completed"
    ).order_by(Order.created_at.desc()).all()

    my_restaurants = []

    if user.role == "admin" or "owner":
        my_restaurants = db.query(Restaurant).all()

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "user": user,
            "orders": orders,  # Передаем список заказов в шаблон
            "my_restaurants":my_restaurants 
        }
    )

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    
    if exc.status_code == 401:
        return templates.TemplateResponse(
            request=request,
            name="401.html", 
            status_code=401
        )
    return HTMLResponse(content=f"<h1>Ошибка {exc.status_code}</h1><p>{exc.detail}</p>", status_code=exc.status_code)   