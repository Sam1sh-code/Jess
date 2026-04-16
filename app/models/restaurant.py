from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    address = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    
    # ТЕ САМЫЕ ПОЛЯ, КОТОРЫЕ СЛЕТЕЛИ:
    rating = Column(Float, default=0.0)
    delivery_time_mins = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
