from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router 
from app.api.profile import router as auth_profile 
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

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
app.include_router(auth_profile)
#Разрешаем раздавать файлы из папки статик
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Сервер работает отличноц"}