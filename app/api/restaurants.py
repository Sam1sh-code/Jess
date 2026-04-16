from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from fastapi.templating import Jinja2Templates
from app.db.database import get_db
from app.models.restaurant import Restaurant 
from app.schemas.restaurant import RestaurantOut
from sqlalchemy.orm import joinedload
from app.models.menu import Category

router = APIRouter(prefix="/api/restaurants", tags=["API Ресторанов"])
templates = Jinja2Templates(directory="frontend")

@router.get("/", response_model=List[RestaurantOut])
def get_all_restaurants(db: Session = Depends(get_db)):
    # Отдаем список всех ресторанов
    return db.query(Restaurant).all()

# @router.get("/{restaurant_id}")
# def get_single_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
#     # Используем joinedload, чтобы SQLAlchemy одним запросом достала и ресторан, и меню
#     restaurant = db.query(Restaurant).options(
#         joinedload(Restaurant.categories).joinedload(Category.items)
#     ).filter(Restaurant.id == restaurant_id).first()
    
#     if not restaurant:
#         return {"error": "Ресторан не найден"}
        
#     return restaurant

@router.get("/{restaurant_id}")
def get_single_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    # 1. Достаем ресторан вместе с меню из БД
    restaurant = db.query(Restaurant).options(
        joinedload(Restaurant.categories).joinedload(Category.items)
    ).filter(Restaurant.id == restaurant_id).first()
    
    if not restaurant:
        return {"error": "Ресторан не найден"}
        
    # 2. Вручную собираем чистый словарь, чтобы FastAPI отдал его без обрезаний
    result = {
        "id": restaurant.id,
        "name": restaurant.name,
        "description": restaurant.description,
        "address": restaurant.address,
        "image_url": restaurant.image_url,
        "rating": restaurant.rating,
        "categories": []
    }
    
    # 3. Аккуратно перекладываем категории и блюда
    for cat in restaurant.categories:
        category_data = {
            "id": cat.id,
            "name": cat.name,
            "items": []
        }
        for item in cat.items:
            category_data["items"].append({
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "price": item.price,
                "image_url": item.image_url
            })
        result["categories"].append(category_data)

    return result