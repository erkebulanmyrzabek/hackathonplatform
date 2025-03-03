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
WEB_APP_URL = "https://bd36-92-47-231-47.ngrok-free.app/feed"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@sync_to_async
def get_or_create_user(telegram_id, name):
    user, created = User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={"name": name, "hash_code": uuid.uuid4().hex[:16]},
    )
    return user

@sync_to_async
def get_user(telegram_id):
    try:
        return User.objects.get(telegram_id=telegram_id)
    except ObjectDoesNotExist:
        return None

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    telegram_id = message.from_user.id
    name = message.from_user.full_name or message.from_user.username

    user = await get_or_create_user(telegram_id, name)
    user_url = f"{WEB_APP_URL}?hash={user.hash_code}"

    keyboard = InlineKeyboardMarkup()
    web_app_button = InlineKeyboardButton("Открыть Mini App", web_app=WebAppInfo(url=user_url))
    keyboard.add(web_app_button)

    await message.answer(f"Привет, {name}! Нажми кнопку ниже, чтобы открыть Mini App:", reply_markup=keyboard)

@dp.message_handler(commands=["stats"])
async def stats_command(message: types.Message):
    user = await get_user(message.from_user.id)
    if user:
        await message.answer(f"📊 Твоя статистика:\n🏆 Уровень: {user.level}\n⭐ XP: {user.xp}")
    else:
        await message.answer("Ты еще не зарегистрирован. Введи /start, чтобы начать!")

@dp.message_handler(commands=["next-level"])
async def next_level_command(message: types.Message):
    user = await get_user(message.from_user.id)
    if user:
        xp_needed = (user.level + 1) * 100 - user.xp
        await message.answer(f"🎯 До следующего уровня осталось {xp_needed} XP!")
    else:
        await message.answer("Ты еще не зарегистрирован. Введи /start, чтобы начать!")

@dp.message_handler(commands=["report"])
async def report_command(message: types.Message):
    await message.answer("📢 Сообщить о проблеме можно, написав в поддержку: @erkemyrzaa")

@dp.message_handler(commands=["FAQ"])
async def faq_command(message: types.Message):
    faq_text = "❓ Часто задаваемые вопросы:\n1️⃣ Как пользоваться ботом?\n➡ Просто введи /start!\n2️⃣ Где моя статистика?\n➡ Введи /stats!\n3️⃣ Как узнать, сколько осталось до следующего уровня?\n➡ Используй /next-level!\n4️⃣ Как сообщить о проблеме?\n➡ Введи /report и напиши в поддержку!"
    await message.answer(faq_text)

@dp.message_handler(commands=["setpicture"])
async def setpicture_command(message: types.Message):
    await message.answer("🎨 Отправьте фото которую вы хотите установить")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
