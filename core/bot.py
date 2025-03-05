import os
import django
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db.models import Count, Sum, Avg

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from user.models import User, UserNotification
from hackathon.models import Hackathon, Team, Solution
from feed.models import Webinar, Casecup
from admin_panel.models import HackathonRequest

TOKEN = settings.TOKEN
WEB_APP_URL = "https://8c2b-2a03-32c0-a001-c5fd-610d-4a9-e041-d4e6.ngrok-free.app/feed"
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Состояния для FSM
class ReportState(StatesGroup):
    waiting_for_report = State()

class HackathonRequestState(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_start_date = State()
    waiting_for_end_date = State()
    waiting_for_participants = State()
    waiting_for_prize_pool = State()
    waiting_for_confirmation = State()

@sync_to_async
def get_or_create_user(telegram_id, name):
    user, created = User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={"name": name, "hash_code": uuid.uuid4().hex[:16]},
    )
    return user, created

@sync_to_async
def get_user(telegram_id):
    try:
        return User.objects.get(telegram_id=telegram_id)
    except ObjectDoesNotExist:
        return None

@sync_to_async
def get_user_notifications(user, limit=5):
    return list(UserNotification.objects.filter(user=user, is_read=False).order_by('-created_at')[:limit])

@sync_to_async
def mark_notification_as_read(notification_id):
    try:
        notification = UserNotification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return True
    except ObjectDoesNotExist:
        return False

@sync_to_async
def get_upcoming_hackathons(limit=5):
    now = timezone.now().date()
    return list(Hackathon.objects.filter(
        start_hackathon__gt=now
    ).order_by('start_hackathon')[:limit])

@sync_to_async
def get_user_hackathons(user, limit=5):
    return list(user.hackathons.all().order_by('-start_hackathon')[:limit])

@sync_to_async
def create_hackathon_request(user, title, description, start_date, end_date, participants, prize_pool):
    request = HackathonRequest.objects.create(
        user=user,
        title=title,
        description=description,
        expected_start_date=start_date,
        expected_end_date=end_date,
        expected_participants=participants,
        prize_pool=prize_pool
    )
    return request

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    telegram_id = message.from_user.id
    name = message.from_user.full_name or message.from_user.username

    user, created = await get_or_create_user(telegram_id, name)
    user_url = f"{WEB_APP_URL}?hash={user.hash_code}"

    keyboard = InlineKeyboardMarkup(row_width=1)
    web_app_button = InlineKeyboardButton("Открыть Mini App", web_app=WebAppInfo(url=user_url))
    keyboard.add(web_app_button)

    welcome_text = f"Привет, {name}! Добро пожаловать на платформу для хакатонов!"
    
    if created:
        welcome_text += "\n\nЯ вижу, что ты здесь впервые. Пожалуйста, заполни свой профиль в Mini App, чтобы получить доступ ко всем функциям платформы."
    
    welcome_text += "\n\nДоступные команды:\n/stats - Твоя статистика\n/next-level - Сколько до следующего уровня\n/report - Сообщить о проблеме\n/FAQ - Часто задаваемые вопросы\n/notifications - Уведомления\n/upcoming - Предстоящие хакатоны\n/my_hackathons - Мои хакатоны\n/request_hackathon - Запросить проведение хакатона"

    await message.answer(welcome_text, reply_markup=keyboard)

@dp.message_handler(commands=["stats"])
async def stats_command(message: types.Message):
    user = await get_user(message.from_user.id)
    if user:
        hackathons_count = await sync_to_async(user.participation_count)()
        
        stats_text = f"📊 Твоя статистика:\n"
        stats_text += f"🏆 Уровень: {user.level}\n"
        stats_text += f"⭐ XP: {user.xp}\n"
        stats_text += f"💎 Кристаллы: {user.coin}\n"
        stats_text += f"🎯 Участие в хакатонах: {hackathons_count}\n"
        
        # Получаем количество достижений
        achievements_count = await sync_to_async(lambda: user.achievements.count())()
        stats_text += f"🏅 Достижения: {achievements_count}\n"
        
        await message.answer(stats_text)
    else:
        await message.answer("Ты еще не зарегистрирован. Введи /start, чтобы начать!")

@dp.message_handler(commands=["next-level"])
async def next_level_command(message: types.Message):
    user = await get_user(message.from_user.id)
    if user:
        xp_needed = await sync_to_async(user.xp_to_next_level)()
        current_level = user.level
        next_level = current_level + 1
        
        await message.answer(f"🎯 Твой текущий уровень: {current_level}\n📈 До уровня {next_level} осталось {xp_needed} XP!")
    else:
        await message.answer("Ты еще не зарегистрирован. Введи /start, чтобы начать!")

@dp.message_handler(commands=["report"])
async def report_command(message: types.Message):
    await ReportState.waiting_for_report.set()
    await message.answer("📢 Опиши проблему, с которой ты столкнулся. Мы постараемся решить ее как можно скорее!")

@dp.message_handler(state=ReportState.waiting_for_report)
async def process_report(message: types.Message, state: FSMContext):
    report_text = message.text
    user = await get_user(message.from_user.id)
    
    if user:
        # Здесь можно добавить логику сохранения отчета в базу данных
        
        await message.answer("Спасибо за сообщение о проблеме! Мы рассмотрим его в ближайшее время.")
    else:
        await message.answer("Ты еще не зарегистрирован. Введи /start, чтобы начать!")
    
    await state.finish()

@dp.message_handler(commands=["FAQ"])
async def faq_command(message: types.Message):
    faq_text = "❓ Часто задаваемые вопросы:\n\n"
    faq_text += "1️⃣ Как пользоваться ботом?\n➡ Просто введи /start!\n\n"
    faq_text += "2️⃣ Где моя статистика?\n➡ Введи /stats!\n\n"
    faq_text += "3️⃣ Как узнать, сколько осталось до следующего уровня?\n➡ Используй /next-level!\n\n"
    faq_text += "4️⃣ Как сообщить о проблеме?\n➡ Введи /report и опиши проблему!\n\n"
    faq_text += "5️⃣ Как зарегистрироваться на хакатон?\n➡ Открой Mini App и выбери интересующий хакатон!\n\n"
    faq_text += "6️⃣ Как создать команду?\n➡ В Mini App на странице хакатона есть кнопка 'Создать команду'!\n\n"
    faq_text += "7️⃣ Как получить кристаллы?\n➡ Участвуй в хакатонах и выигрывай призовые места!"
    
    await message.answer(faq_text)

@dp.message_handler(commands=["notifications"])
async def notifications_command(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Ты еще не зарегистрирован. Введи /start, чтобы начать!")
        return
    
    notifications = await get_user_notifications(user)
    
    if not notifications:
        await message.answer("У тебя нет новых уведомлений.")
        return
    
    notifications_text = "📬 Твои уведомления:\n\n"
    
    for i, notification in enumerate(notifications, 1):
        notifications_text += f"{i}. {notification.title}\n{notification.message}\n\n"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Отметить все как прочитанные", callback_data="read_all_notifications"))
    
    await message.answer(notifications_text, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "read_all_notifications")
async def process_read_all_notifications(callback_query: types.CallbackQuery):
    user = await get_user(callback_query.from_user.id)
    if not user:
        await callback_query.answer("Ты еще не зарегистрирован.")
        return
    
    # Отмечаем все уведомления как прочитанные
    await sync_to_async(lambda: UserNotification.objects.filter(user=user, is_read=False).update(is_read=True))()
    
    await callback_query.answer("Все уведомления отмечены как прочитанные!")
    await bot.edit_message_text(
        "Все уведомления отмечены как прочитанные!",
        callback_query.from_user.id,
        callback_query.message.message_id
    )

@dp.message_handler(commands=["upcoming"])
async def upcoming_hackathons_command(message: types.Message):
    hackathons = await get_upcoming_hackathons()
    
    if not hackathons:
        await message.answer("В ближайшее время нет запланированных хакатонов.")
        return
    
    hackathons_text = "🚀 Предстоящие хакатоны:\n\n"
    
    for hackathon in hackathons:
        hackathons_text += f"🏆 {hackathon.name}\n"
        hackathons_text += f"📅 Дата: {hackathon.start_hackathon} - {hackathon.end_hackathon}\n"
        hackathons_text += f"💰 Призовой фонд: {hackathon.prize_pool}\n"
        hackathons_text += f"👥 Участников: {hackathon.participants_count}\n\n"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Открыть в Mini App", web_app=WebAppInfo(url=f"{WEB_APP_URL}/hackathons")))
    
    await message.answer(hackathons_text, reply_markup=keyboard)

@dp.message_handler(commands=["my_hackathons"])
async def my_hackathons_command(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Ты еще не зарегистрирован. Введи /start, чтобы начать!")
        return
    
    hackathons = await get_user_hackathons(user)
    
    if not hackathons:
        await message.answer("Ты еще не участвовал в хакатонах.")
        return
    
    hackathons_text = "🏆 Твои хакатоны:\n\n"
    
    for hackathon in hackathons:
        status_text = "Предстоящий" if hackathon.start_hackathon > timezone.now().date() else (
            "Активный" if hackathon.end_hackathon >= timezone.now().date() else "Завершенный"
        )
        
        hackathons_text += f"🏆 {hackathon.name}\n"
        hackathons_text += f"📅 Дата: {hackathon.start_hackathon} - {hackathon.end_hackathon}\n"
        hackathons_text += f"📊 Статус: {status_text}\n\n"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Открыть в Mini App", web_app=WebAppInfo(url=f"{WEB_APP_URL}/profile")))
    
    await message.answer(hackathons_text, reply_markup=keyboard)

@dp.message_handler(commands=["request_hackathon"])
async def request_hackathon_command(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Ты еще не зарегистрирован. Введи /start, чтобы начать!")
        return
    
    await HackathonRequestState.waiting_for_title.set()
    await message.answer("🏆 Запрос на проведение хакатона\n\nШаг 1/6: Введи название хакатона:")

@dp.message_handler(state=HackathonRequestState.waiting_for_title)
async def process_hackathon_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text
    
    await HackathonRequestState.waiting_for_description.set()
    await message.answer("Шаг 2/6: Введи описание хакатона:")

@dp.message_handler(state=HackathonRequestState.waiting_for_description)
async def process_hackathon_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    
    await HackathonRequestState.waiting_for_start_date.set()
    await message.answer("Шаг 3/6: Введи дату начала хакатона (в формате ГГГГ-ММ-ДД):")

@dp.message_handler(state=HackathonRequestState.waiting_for_start_date)
async def process_hackathon_start_date(message: types.Message, state: FSMContext):
    try:
        start_date = timezone.datetime.strptime(message.text, "%Y-%m-%d").date()
        
        if start_date < timezone.now().date():
            await message.answer("Дата начала не может быть в прошлом. Пожалуйста, введи корректную дату:")
            return
        
        async with state.proxy() as data:
            data['start_date'] = start_date
        
        await HackathonRequestState.waiting_for_end_date.set()
        await message.answer("Шаг 4/6: Введи дату окончания хакатона (в формате ГГГГ-ММ-ДД):")
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, введи дату в формате ГГГГ-ММ-ДД:")

@dp.message_handler(state=HackathonRequestState.waiting_for_end_date)
async def process_hackathon_end_date(message: types.Message, state: FSMContext):
    try:
        end_date = timezone.datetime.strptime(message.text, "%Y-%m-%d").date()
        
        async with state.proxy() as data:
            if end_date <= data['start_date']:
                await message.answer("Дата окончания должна быть позже даты начала. Пожалуйста, введи корректную дату:")
                return
            
            data['end_date'] = end_date
        
        await HackathonRequestState.waiting_for_participants.set()
        await message.answer("Шаг 5/6: Введи ожидаемое количество участников:")
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, введи дату в формате ГГГГ-ММ-ДД:")

@dp.message_handler(state=HackathonRequestState.waiting_for_participants)
async def process_hackathon_participants(message: types.Message, state: FSMContext):
    try:
        participants = int(message.text)
        
        if participants <= 0:
            await message.answer("Количество участников должно быть положительным числом. Пожалуйста, введи корректное значение:")
            return
        
        async with state.proxy() as data:
            data['participants'] = participants
        
        await HackathonRequestState.waiting_for_prize_pool.set()
        await message.answer("Шаг 6/6: Введи призовой фонд (в рублях):")
    except ValueError:
        await message.answer("Неверный формат. Пожалуйста, введи число:")

@dp.message_handler(state=HackathonRequestState.waiting_for_prize_pool)
async def process_hackathon_prize_pool(message: types.Message, state: FSMContext):
    try:
        prize_pool = int(message.text)
        
        if prize_pool < 0:
            await message.answer("Призовой фонд не может быть отрицательным. Пожалуйста, введи корректное значение:")
            return
        
        async with state.proxy() as data:
            data['prize_pool'] = prize_pool
        
        # Формируем сообщение с подтверждением
        confirmation_text = "📋 Проверь данные запроса:\n\n"
        confirmation_text += f"🏆 Название: {data['title']}\n"
        confirmation_text += f"📝 Описание: {data['description']}\n"
        confirmation_text += f"📅 Дата начала: {data['start_date']}\n"
        confirmation_text += f"📅 Дата окончания: {data['end_date']}\n"
        confirmation_text += f"👥 Ожидаемое количество участников: {data['participants']}\n"
        confirmation_text += f"💰 Призовой фонд: {data['prize_pool']} руб.\n\n"
        confirmation_text += "Все верно?"
        
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("Да", callback_data="confirm_hackathon_request"),
            InlineKeyboardButton("Нет", callback_data="cancel_hackathon_request")
        )
        
        await HackathonRequestState.waiting_for_confirmation.set()
        await message.answer(confirmation_text, reply_markup=keyboard)
    except ValueError:
        await message.answer("Неверный формат. Пожалуйста, введи число:")

@dp.callback_query_handler(lambda c: c.data == "confirm_hackathon_request", state=HackathonRequestState.waiting_for_confirmation)
async def confirm_hackathon_request(callback_query: types.CallbackQuery, state: FSMContext):
    user = await get_user(callback_query.from_user.id)
    if not user:
        await callback_query.answer("Ты еще не зарегистрирован.")
        await state.finish()
        return
    
    async with state.proxy() as data:
        await create_hackathon_request(
            user=user,
            title=data['title'],
            description=data['description'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            participants=data['participants'],
            prize_pool=data['prize_pool']
        )
    
    await callback_query.answer("Запрос успешно отправлен!")
    await bot.send_message(
        callback_query.from_user.id,
        "✅ Твой запрос на проведение хакатона успешно отправлен! Мы рассмотрим его в ближайшее время и сообщим о результате."
    )
    
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "cancel_hackathon_request", state=HackathonRequestState.waiting_for_confirmation)
async def cancel_hackathon_request(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Запрос отменен.")
    await bot.send_message(
        callback_query.from_user.id,
        "❌ Запрос на проведение хакатона отменен. Ты можешь начать заново, введя команду /request_hackathon."
    )
    
    await state.finish()

@dp.message_handler(commands=["setpicture"])
async def setpicture_command(message: types.Message):
    await message.answer("🎨 Отправьте фото которую вы хотите установить")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
