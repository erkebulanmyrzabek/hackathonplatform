from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

TOKEN = "7756865994:AAF0z8QIx8rFXDG5VQnqQZBSmolqlWFzZXc"
WEB_APP_URL = "https://650f-2a03-32c0-a000-8232-94ee-8794-29ac-204c.ngrok-free.app/"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    web_app_button = types.InlineKeyboardButton("Открыть Mini App", web_app=types.WebAppInfo(url=WEB_APP_URL))
    keyboard.add(web_app_button)

    await message.answer("Привет! Нажми кнопку ниже, чтобы открыть Mini App:", reply_markup=keyboard)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

