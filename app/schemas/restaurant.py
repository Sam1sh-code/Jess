from pydantic import BaseModel
from typing import Optional

class RestaurantOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
    delivery_time_mins: Optional[int] = None

    # Эта настройка позволяет Pydantic читать данные прямо из базы SQLAlchemy
    class Config:
        from_attributes = True