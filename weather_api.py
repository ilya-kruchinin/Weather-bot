# weather_api.py
import aiohttp

async def get_weather(city: str, api_key: str) -> dict | str:
    """Получает текущую погоду из OpenWeatherMap."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric", # Цельсии
        "lang": "ru"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "city": data["name"],
                        "temp": round(data["main"]["temp"]),
                        "feels_like": round(data["main"]["feels_like"]),
                        "description": data["weather"][0]["description"],
                        "wind": data["wind"]["speed"]
                    }
                elif response.status == 404:
                    return "Город не найден. Проверьте название."
                else:
                    return "Ошибка API погоды."
        except Exception as e:
            return f"Ошибка соединения: {e}"