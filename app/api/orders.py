from fastapi import APIRouter, Depends, HTTPException, Form, Request
from app.core.security import get_owner_or_admin
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.user import User
from typing import List
from fastapi.templating import Jinja2Templates
from app.models.order import Order, OrderItem
from app.db.database import get_db
from app.core.security import get_current_user
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/api/restaurants", tags=["API Ресторанов"])
templates = Jinja2Templates(directory="frontend")

# 1. Pydantic-схемы для проверки того, что прислал фронтенд
class CartItem(BaseModel):
    id: int
    quantity: int
    price: float

class CheckoutRequest(BaseModel):
    restaurant_id: int
    address_delivery: str
    items: List[CartItem]
    total_price: float

# 2. Сам роут
@router.post("/checkout")
def create_order(
    order_data: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) # Пускаем всех залогиненных
):
    # 1. Создаем главный заказ
    new_order = Order(
        user_id=current_user.id,
        restaurant_id=order_data.restaurant_id,
        status="pending", # Статус по умолчанию
        total_price=order_data.total_price,
        address_delivery=order_data.address_delivery
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order) # Получаем ID созданного заказа

    # 2. Перебираем корзину и создаем позиции (OrderItem)
    for item in order_data.items:
        new_order_item = OrderItem(
            order_id=new_order.id,
            menu_item_id=item.id,
            quantity=item.quantity,
            price_at_order=item.price
        )
        db.add(new_order_item)
    
    db.commit()
    
    return {"status": "success", "order_id": new_order.id}

from sqlalchemy.orm import joinedload

@router.get("/{restaurant_id}/orders")
def view_restaurant_orders(
    restaurant_id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    user: User = Depends(get_owner_or_admin) # Пускаем только владельцев/админов
):
    # Достаем все заказы для этого ресторана, вместе с инфой о клиенте и позициями меню
    orders = db.query(Order).options(
        joinedload(Order.client),
        joinedload(Order.items).joinedload(OrderItem.item)
    ).filter(
        Order.restaurant_id == restaurant_id
    ).order_by(Order.created_at.desc()).all()
    
    return templates.TemplateResponse(
        request=request, 
        name="restaurant_orders.html", 
        context={
            "user": user,
            "orders": orders
        }
    )

# Роут для смены статуса (Ресторан нажимает "Взять в работу" или "Готово")
@router.post("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str = Form(...), # Получаем новый статус из кнопки
    db: Session = Depends(get_db),
    user: User = Depends(get_owner_or_admin)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    order.status = status
    db.commit()
    
    # Редиректим обратно на страницу заказов
    return RedirectResponse(url=f"/api/restaurants/{order.restaurant_id}/orders", status_code=303)
