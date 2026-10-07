# bot.py
import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db import init_db, add_subscription, remove_subscription
from weather_api import get_weather
from tasks import send_daily_weather

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
OWM_API_KEY = os.getenv("OWM_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Хендлеры команд ---

@dp.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        "Привет! 👋 Я бот погоды.\n\n"
        "🌤 /weather <город> — узнать погоду сейчас\n"
        "🔔 /subscribe <город> — подписаться на ежедневную погоду (в 08:00)\n"
        "🔕 /unsubscribe — отписаться от уведомлений"
    )
    await message.answer(text)

@dp.message(Command("weather"))
async def cmd_weather(message: Message):
    # Получаем название города из аргументов команды
    city = message.text.split(maxsplit=1)
    if len(city) < 2:
        await message.answer("Укажите город. Пример: /weather London")
        return
    
    weather_data = await get_weather(city[1], OWM_API_KEY)
    
    if isinstance(weather_data, str):
        await message.answer(weather_data)
    else:
        text = (
            f"🌍 Погода в городе {weather_data['city']}:\n"
            f"🌡 Температура: {weather_data['temp']}°C (ощущается как {weather_data['feels_like']}°C)\n"
            f"☁️ {weather_data['description'].capitalize()}\n"
            f"💨 Ветер: {weather_data['wind']} м/с"
        )
        await message.answer(text)

@dp.message(Command("subscribe"))
async def cmd_subscribe(message: Message):
    city = message.text.split(maxsplit=1)
    if len(city) < 2:
        await message.answer("Укажите город. Пример: /subscribe Moscow")
        return

    # Проверяем, существует ли город
    check = await get_weather(city[1], OWM_API_KEY)
    if isinstance(check, str):
        await message.answer(check)
        return

    add_subscription(message.from_user.id, city[1])
    await message.answer(f"✅ Вы подписаны на ежедневную погоду в городе {city[1]} (в 08:00 по МСК).")

@dp.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: Message):
    remove_subscription(message.from_user.id)
    await message.answer("🔕 Вы отписаны от уведомлений.")

# --- Запуск ---

async def main():
    init_db()
    
    # Настраиваем планировщик
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    # Задача на каждый день в 08:00
    scheduler.add_job(send_daily_weather, "cron", hour=8, minute=0, kwargs={"bot": bot, "api_key": OWM_API_KEY})
    scheduler.start()
    
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())