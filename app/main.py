from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router 
from app.api.admin import router as admin_router
from app.api.restaurants import router as restaurant_router
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.core.security import get_current_admin, get_current_user, get_owner_or_admin
from app.models.user import User

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

@app.get("/profile")
def get_profile(
    request: Request, 
    user: User = Depends(get_current_user)
):
    
    # Явно указываем, что есть что. Это "защита от дурака" для библиотек.
    return templates.TemplateResponse(
        request=request,         # Теперь request идет первым и явно
        name="profile.html",     # Имя файла явно
        context={"user": user}   # Контекст явно, и request внутрь словаря класть НЕ НУЖНО
    )

@app.get("/restaurants/create")
def show_create_restaurant_form(request: Request, user: User = Depends(get_owner_or_admin)):
    return templates.TemplateResponse(request=request, name = "create_restaurant.html")
    # return templates.TemplateResponse(name = "create_restaurant.html", context= {"request": request, "user": user})
