from app.db.database import SessionLocal
from app.models.restaurant import Restaurant
from app.models.user import User
from sqlalchemy import text
from app.models.menu import Category, MenuItem

def seed_data():
    db = SessionLocal()
    
    # 1. Очищаем старые данные (чтобы не было дублей)
    print("🧹 Очистка старых записей...")
    db.execute(text("TRUNCATE TABLE menu_items CASCADE;"))
    db.execute(text("TRUNCATE TABLE categories CASCADE;"))
    db.execute(text("TRUNCATE TABLE restaurants CASCADE;"))
    db.commit()

    # 2. Ищем владельца (твой аккаунт)
    first_user = db.query(User).first()
    if not first_user:
        print("❌ Ошибка: Пользователь не найден. Сначала зарегистрируйся!")
        return

    # 3. Список ТОП-8 ресторанов Душанбе
    dushanbe_restaurants = [
        Restaurant(
            owner_id=first_user.id,
            name="Сыроварня",
            description="Деревенский итальянский ресторан. Собственное производство сыров, дровяная печь и уютная атмосфера.",
            address="пр. Рудаки, отель 'Серена'",
            image_url="https://images.unsplash.com/photo-1559339352-11d035aa65de?q=80&w=1974&auto=format&fit=crop",
            rating=4.9,
            delivery_time_mins=40
        ),
        Restaurant(
            owner_id=first_user.id,
            name="Toqi",
            description="Легендарная национальная кухня. Лучший оши-палав, курутоб и аутентичный интерьер.",
            address="пр. Исмоили Сомони",
            image_url="https://images.unsplash.com/photo-1585032226651-759b368d7246?q=80&w=1984&auto=format&fit=crop",
            rating=4.8,
            delivery_time_mins=50
        ),
        Restaurant(
            owner_id=first_user.id,
            name="Traktir",
            description="Классическая русская и европейская кухня. Уютное место для семейных вечеров.",
            address="ул. Техрон (возле Оперного театра)",
            image_url="https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?q=80&w=2070&auto=format&fit=crop",
            rating=4.7,
            delivery_time_mins=35
        ),
        Restaurant(
            owner_id=first_user.id,
            name="Yak-I-Nur",
            description="Сочные шашлыки и богатый выбор восточных блюд. Место с историей.",
            address="ул. Айни",
            image_url="https://images.unsplash.com/photo-1544124499-58912cbddaad?q=80&w=2070&auto=format&fit=crop",
            rating=4.6,
            delivery_time_mins=45
        ),
        Restaurant(
            owner_id=first_user.id,
            name="Bukhara",
            description="Изысканная атмосфера и лучшие традиции восточного гостеприимства.",
            address="пр. Рудаки",
            image_url="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=2070&auto=format&fit=crop",
            rating=4.8,
            delivery_time_mins=60
        ),
        Restaurant(
            owner_id=first_user.id,
            name="Al-Sham",
            description="Ароматная ливанская и сирийская кухня. Хумус, фалафель и нежнейшее мясо.",
            address="ул. М. Турсунзаде",
            image_url="https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?q=80&w=1981&auto=format&fit=crop",
            rating=4.7,
            delivery_time_mins=40
        ),
        Restaurant(
            owner_id=first_user.id,
            name="Bella Pizza",
            description="Настоящая итальянская пицца на тонком тесте, приготовленная на дровах.",
            address="ул. Бухоро",
            image_url="https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=2070&auto=format&fit=crop",
            rating=4.5,
            delivery_time_mins=30
        ),
        Restaurant(
            owner_id=first_user.id,
            name="Chaihona Rohat",
            description="Культовая чайхона, визитная карточка Душанбе. Традиции в каждом глотке чая.",
            address="пр. Рудаки",
            image_url="https://images.unsplash.com/photo-1590846406792-0adc7f938f1d?q=80&w=1970&auto=format&fit=crop",
            rating=4.4,
            delivery_time_mins=55
        )
    ]
    syrovarnya = db.query(Restaurant).filter(Restaurant.name == "Сыроварня").first()
    if syrovarnya:
        # Категории для Сыроварни
        cat1 = Category(name="Завтраки", restaurant_id=syrovarnya.id)
        cat2 = Category(name="Пицца из печи", restaurant_id=syrovarnya.id)
        db.add_all([cat1, cat2])
        db.commit()

        # Блюда
        items = [
            MenuItem(category_id=cat1.id, name="Сырники из домашнего творога", price=65.0, description="Подаются со сметаной и вареньем"),
            MenuItem(category_id=cat2.id, name="Пицца Маргарита", price=85.0, description="Классика с моцареллой собственного производства"),
            MenuItem(category_id=cat2.id, name="Пицца с грушей и горгонзолой", price=110.0, description="Изысканное сочетание сладкого и соленого")
        ]
        db.add_all(items)
        db.commit()
    print("✅ Меню для Сыроварни готово!")

    db.add_all(dushanbe_restaurants)
    db.commit()
    print(f"✅ Успех! Добавлено {len(dushanbe_restaurants)} ресторанов Душанбе.")
    db.close()

if __name__ == "__main__":
    seed_data()