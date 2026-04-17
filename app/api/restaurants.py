from fastapi import APIRouter, Depends, Request, Form, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.templating import Jinja2Templates
from app.db.database import get_db
from app.models.restaurant import Restaurant 
from app.schemas.restaurant import RestaurantOut
from sqlalchemy.orm import joinedload
from app.models.menu import Category
from app.core.security import get_owner_or_admin
from fastapi.responses import RedirectResponse
from app.models.menu import MenuItem

from app.models.user import User

router = APIRouter(prefix="/api/restaurants", tags=["API Ресторанов"])
templates = Jinja2Templates(directory="frontend")

@router.get("/", response_model=List[RestaurantOut])
def get_all_restaurants(db: Session = Depends(get_db)):
    # Отдаем список всех ресторанов
    return db.query(Restaurant).all()

@router.post("/create") 
def create_restaurant_action(
    name: str = Form(...),
    description: str = Form(None),
    address: str = Form(None),
    image_url: str = Form(None),
    delivery_time_mins: int = Form(30),
    db: Session = Depends(get_db),
    user: User = Depends(get_owner_or_admin)
):
    new_restaurant = Restaurant(
        owner_id=user.id, 
        name=name,
        description=description,
        address=address,
        image_url=image_url,
        delivery_time_mins=delivery_time_mins
    )
    db.add(new_restaurant)
    db.commit()
    
    # После создания кидаем обратно на админку или профиль
    return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/categories/create")
def create_category_action(
    name: str = Form(...),
    restaurant_id: int = Form(...), # Скрытое поле из формы
    db: Session = Depends(get_db),
    user: User = Depends(get_owner_or_admin)
):
    new_cat = Category(name=name, restaurant_id=restaurant_id)
    db.add(new_cat)
    db.commit()
    
    # Редирект обратно на эту же страницу управления!
    return RedirectResponse(url=f"/api/restaurants/{restaurant_id}/manage-menu", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/menu/create")
def create_menu_item(
    category_id: int = Form(...),
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    image_url: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_owner_or_admin)
):
    new_item = MenuItem(
        category_id=category_id,
        name=name,
        description=description,
        price=price,
        image_url=image_url
    )
    db.add(new_item)
    db.commit()
    
    return RedirectResponse(url="/admin/menu", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/items/create")
def create_menu_item_action(
    category_id: int = Form(...),
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    image_url: str = Form(None),
    restaurant_id: int = Form(...), # Прокидываем для редиректа
    db: Session = Depends(get_db),
    user: User = Depends(get_owner_or_admin)
):
    new_item = MenuItem(
        category_id=category_id,
        name=name,
        description=description,
        price=price,
        image_url=image_url
    )
    db.add(new_item)
    db.commit()
    
    return RedirectResponse(url=f"/api/restaurants/{restaurant_id}/manage-menu", status_code=status.HTTP_303_SEE_OTHER)


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

@router.get("/{restaurant_id}/manage-menu")
def manage_menu_page(
    restaurant_id: int, 
    request: Request, 
    db: Session = Depends(get_db)
):
    # 1. Ищем ресторан
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Ресторан не найден")
    
    # 2. Ищем категории
    categories = db.query(Category).filter(Category.restaurant_id == restaurant_id).all()
    
    # 3. Собираем словарь БЕЗ ЗАПЯТОЙ В КОНЦЕ
    context_data = {
        "request": request,
        "restaurant": restaurant,
        "categories": categories
    }
    
    # 4. УЛЬТИМАТИВНЫЙ ВЫЗОВ (Явно пишем request=, name=, context=)
    return templates.TemplateResponse(
        request=request, 
        name="manage_menu.html", 
        context=context_data
    )