from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))

    # Связь с рестораном
    restaurant = relationship("Restaurant", backref="categories")

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    image_url = Column(String) # Сюда сохраним путь к картинке еды
    is_available = Column(Boolean, default=True)

    category = relationship("Category", backref="items")