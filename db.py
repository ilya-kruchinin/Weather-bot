# db.py
import sqlite3
import os

DB_PATH = "data/bot.db"

def init_db():
    """Создает таблицу подписок, если её нет."""
    os.makedirs("data", exist_ok=True) # Создаем папку для сохранения БД
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER PRIMARY KEY,
                city TEXT NOT NULL
            )
        """)
        conn.commit()

def add_subscription(user_id: int, city: str):
    """Добавляет или обновляет город пользователя."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO subscriptions (user_id, city) VALUES (?, ?)",
            (user_id, city)
        )
        conn.commit()

def remove_subscription(user_id: int):
    """Удаляет подписку."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM subscriptions WHERE user_id = ?", (user_id,))
        conn.commit()

def get_all_subscriptions():
    """Возвращает список всех подписок для рассылки."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT user_id, city FROM subscriptions")
        return cursor.fetchall()