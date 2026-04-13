from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    address = Column(String, nullable=False)
    
    # Координаты для будущего расчета расстояния (пока просто числа)
    latitude = Column(Float)
    longitude = Column(Float)
    
    is_active = Column(Boolean, default=True)

    # Связь с таблицей пользователей (один владелец -> много ресторанов)
    owner = relationship("User", backref="restaurants")