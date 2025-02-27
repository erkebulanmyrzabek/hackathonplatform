import os
import django
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from user.models import User

TOKEN = settings.TOKEN
WEB_APP_URL = "https://27e6-185-250-31-99.ngrok-free.app/feed"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@sync_to_async
def get_or_create_user(telegram_id, name):
    user, created = User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={"name": name, "hash_code": uuid.uuid4().hex[:16]},
    )
    return user


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    telegram_id = message.from_user.id
    name = message.from_user.full_name or message.from_user.username

    user = await get_or_create_user(telegram_id, name)

    user_url = f"{WEB_APP_URL}?hash={user.hash_code}"

    keyboard = InlineKeyboardMarkup()
    web_app_button = InlineKeyboardButton(
        "Открыть Mini App", web_app=WebAppInfo(url=user_url)
    )
    keyboard.add(web_app_button)

    await message.answer(
        f"Привет, {name}! Нажми кнопку ниже, чтобы открыть Mini App:",
        reply_markup=keyboard,
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
