# tasks.py
from aiogram import Bot
from db import get_all_subscriptions
from weather_api import get_weather

async def send_daily_weather(bot: Bot, api_key: str):
    """Функция, которая вызывается планировщиком для рассылки погоды."""
    subscriptions = get_all_subscriptions()
    
    for user_id, city in subscriptions:
        weather_data = await get_weather(city, api_key)
        
        if isinstance(weather_data, dict):
            text = (
                f"☀️ Доброе утро! Погода в {weather_data['city']} на сегодня:\n"
                f"🌡 {weather_data['temp']}°C (ощущается {weather_data['feels_like']}°C)\n"
                f"☁️ {weather_data['description'].capitalize()}\n"
                f"💨 Ветер: {weather_data['wind']} м/с\n\n"
                f"Чтобы отписаться: /unsubscribe"
            )
        else:
            text = f"⚠️ Не удалось получить погоду для {city}: {weather_data}"
            
        try:
            await bot.send_message(user_id, text)
        except Exception as e:
            # Если пользователь заблокировал бота, можно удалить его из БД
            print(f"Ошибка отправки {user_id}: {e}")