import os
import django
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from asgiref.sync import sync_to_async  # Позволяет работать с Django ORM в асинхронном контексте
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

# Настроим Django, чтобы можно было использовать её модели
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  # Укажи свое имя проекта
django.setup()

from user.models import User  # Подтягиваем модель

TOKEN = settings.TOKEN  # Убедись, что в settings.py прописан правильный токен
WEB_APP_URL = "https://ffb4-2a03-32c0-a001-7af0-429-7471-a509-3188.ngrok-free.app/feed"  # Измени на свою ссылку Mini App
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Асинхронная работа с Django ORM
@sync_to_async
def get_or_create_user(telegram_id, name):
    user, created = User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={"name": name, "hash_code": uuid.uuid4().hex[:16]}  # Генерация уникального хэша
    )
    return user

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    telegram_id = message.from_user.id  # ID пользователя в Telegram
    name = message.from_user.full_name or message.from_user.username

    # Получаем или создаем пользователя в БД
    user = await get_or_create_user(telegram_id, name)

    # Формируем ссылку с уникальным хэшем пользователя для Mini App
    user_url = f"{WEB_APP_URL}?hash={user.hash_code}"

    keyboard = InlineKeyboardMarkup()
    web_app_button = InlineKeyboardButton("Открыть Mini App", web_app=WebAppInfo(url=user_url))
    keyboard.add(web_app_button)

    await message.answer(
        f"Привет, {name}! Нажми кнопку ниже, чтобы открыть Mini App:",
        reply_markup=keyboard
    )

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
