from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import joinedload
from fastapi.responses import RedirectResponse
import starlette.status as status
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_current_user, get_db
from app.models.order import Order
from fastapi.templating import Jinja2Templates

courier_router = APIRouter(prefix="/api/courier", tags=["Курьеры"])
templates = Jinja2Templates(directory="frontend")

@courier_router.get("/orders")
def view_courier_orders(
    request: Request, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user) # Сюда пускаем курьеров
):
    # Курьер видит только те заказы, которые ресторан УЖЕ приготовил и передал в доставку
    orders = db.query(Order).options(
        joinedload(Order.client),
        joinedload(Order.restaurant)
    ).filter(Order.status == "delivering").order_by(Order.created_at.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="courier_orders.html",
        context={"user": user, "orders": orders}
    )

# 2. Кнопка "Я доставил!"
@courier_router.post("/orders/{order_id}/complete")
def complete_order(
    order_id: int, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = "completed"
        order.courier_id = user.id # Записываем в базу, какой именно курьер доставил еду!
        db.commit()
        
    return RedirectResponse(url="/api/courier/orders", status_code=303)