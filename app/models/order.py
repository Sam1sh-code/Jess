from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    courier_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Статусы: "pending", "preparing", "delivering", "completed", "cancelled"
    status = Column(String, default="pending")
    total_price = Column(Float)
    
    address_delivery = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    client = relationship("User", foreign_keys=[user_id])
    courier = relationship("User", foreign_keys=[courier_id])
    restaurant = relationship("Restaurant")

class OrderItem(Base):
    """Отдельные позиции внутри одного заказа"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer, default=1)
    price_at_order = Column(Float) # Цена на момент покупки (может измениться в меню позже)

    order = relationship("Order", backref="items")
    item = relationship("MenuItem")