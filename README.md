# Hack Platform

Универсальная платформа для проведения хакатонов, кейс-капов и вебинаров с интеграцией через Telegram mini-app.

## Описание проекта

Hack Platform - это универсальная платформа для проведения хакатонов, кейс-капов и вебинаров с интеграцией через Telegram mini-app. Платформа позволяет участникам просматривать актуальные мероприятия, регистрироваться на них, отслеживать личную статистику и достижения, а организаторам – создавать, модерировать и анализировать результаты мероприятий.

### Основные функции

- **Для участников**:
  - Просмотр актуальных мероприятий
  - Регистрация на мероприятия (индивидуально или командой)
  - Отслеживание личной статистики и достижений
  - Получение сертификатов за участие
  - Обмен кристаллов на мерч в магазине
  - Общение с другими участниками

- **Для организаторов**:
  - Создание и модерирование хакатонов
  - Просмотр и оценка решений участников
  - Аналитика по проводимым мероприятиям
  - Модерация регистрационных запросов

- **Для администраторов**:
  - Управление пользователями и их ролями
  - Модерирование контента
  - Аналитика по платформе

## Технический стек

- **Backend**: Django, Django REST Framework
- **Frontend**: React/Vue.js (для Mini App)
- **База данных**: PostgreSQL
- **Telegram Bot**: aiogram
- **Деплой**: Docker, Nginx

## Установка и запуск

### Требования

- Python 3.11+
- PostgreSQL
- Vue.js (для фронтенда)
- Telegram Bot Token

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/erkebulanmyrzabek/hackathonplatform.git
cd hackathonplatform
```

2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env в корневой директории проекта со следующими переменными:
```
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/hackathonplatform
TOKEN=your_telegram_bot_token
```

5. Примените миграции:
```bash
cd core
python manage.py migrate
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

7. Запустите сервер:
```bash
python manage.py runserver
```

8. В отдельном терминале запустите Telegram-бота:
```bash
python bot.py
```

## Структура проекта

```
hackathonplatform/
├── core/                  # Основной Django проект
│   ├── core/              # Настройки проекта
│   ├── user/              # Приложение для пользователей
│   ├── hackathon/         # Приложение для хакатонов
│   ├── feed/              # Приложение для ленты событий
│   ├── shop/              # Приложение для магазина
│   ├── community/         # Приложение для сообщества
│   ├── rating/            # Приложение для рейтинга
│   ├── admin_panel/       # Приложение для админ-панели
│   ├── templates/         # HTML шаблоны
│   ├── static/            # Статические файлы
│   └── manage.py          # Скрипт управления Django
├── bot.py                 # Telegram-бот
├── requirements.txt       # Зависимости Python
├── Dockerfile             # Dockerfile для контейнеризации
└── README.md              # Документация проекта
```

## Разработка

### Миграции

Для создания миграций после изменения моделей:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Запуск тестов

```bash
python manage.py test
```

### Запуск с помощью Docker

1. Соберите образ:
```bash
docker build -t hackathonplatform .
```

2. Запустите контейнер:
```bash
docker run -p 8000:8000 hackathonplatform
```

## Лицензия

MIT 