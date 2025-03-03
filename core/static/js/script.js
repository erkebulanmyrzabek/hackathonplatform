// Данные пользователя
const user = {
    name: 'Сейтжанов Темирлан',
    avatar: "img/07216f9d9cd9b08b142ef14da40f5476.jpg"
};

// Данные уведомлений
const notifications = [
    { id: 1, message: 'Напоминание: Хакатон AI Solutions начнётся через 24 часа' },
    { id: 2, message: 'Ваша команда прошла в следующий этап!' }
];

// Данные событий
const events = [
    {
        id: 1,
        type: 'Хакатон',
        title: 'AI Solutions 2025',
        date: '2025-03-15',
        participants: 352,
        format: 'Онлайн',
        image: 'img/360_F_245562410_PmIEyr1I3WkcwMVC6vBwrXctULQ4sA28.jpg'
    },
    {
        id: 2,
        type: 'Вебинар',
        title: 'Введение в машинное обучение',
        date: '2025-03-10',
        participants: 128,
        format: 'Онлайн',
        image: "img/premium_photo-1682124651258-410b25fa9dc0.avif"
    },
    {
        id: 3,
        type: 'Кейс-чемпионат',
        title: 'FinTech Challenge',
        date: '2025-03-20',
        participants: 214,
        format: 'Гибридный',
        image: "img/photo-1522202176988-66273c2fd55f.avif"
    },
    {
        id: 4,
        type: 'Хакатон',
        title: 'Web3 Hackathon',
        date: '2025-04-05',
        participants: 182,
        format: 'Офлайн, Алматы',
        image: "img/photo-1670269069776-a1337c703669.avif"
    }
];

// Маппинг фильтров
const filterMapping = {
    'all': 'Все',
    'hackathon': 'Хакатон',
    'casecamp': 'Кейс-чемпионат',
    'webinar': 'Вебинар'
};

// Текущий активный фильтр
let activeFilter = 'all';
// Текущий активный пункт навигации
let activeNavItem = 'main';

// DOM-элементы
const userAvatarElement = document.getElementById('userAvatar');
const userNameElement = document.getElementById('userName');
const notificationIconElement = document.getElementById('notificationIcon');
const notificationBadgeElement = document.getElementById('notificationBadge');
const filtersElement = document.getElementById('filters');
const eventsListElement = document.getElementById('eventsList');
const noEventsElement = document.getElementById('noEvents');
const eventCardTemplate = document.getElementById('eventCardTemplate');
const navItems = document.querySelectorAll('.nav-item');

// Инициализация данных пользователя
function initUserData() {
    userAvatarElement.style.backgroundImage = `url(${user.avatar})`;
    userNameElement.textContent = user.name;
    notificationBadgeElement.textContent = notifications.length;
    
    if (notifications.length === 0) {
        notificationBadgeElement.style.display = 'none';
    }
}

// Форматирование даты
function formatDate(dateString) {
    const options = { day: 'numeric', month: 'long', year: 'numeric' };
    return new Date(dateString).toLocaleDateString('ru-RU', options);
}

// Отображение событий с учетом фильтра
function renderEvents() {
    // Очищаем список событий
    eventsListElement.innerHTML = '';
    
    // Фильтруем события
    let filteredEvents = events;
    if (activeFilter !== 'all') {
        filteredEvents = events.filter(event => {
            return event.type === filterMapping[activeFilter];
        });
    }
    
    // Если нет событий, показываем уведомление
    if (filteredEvents.length === 0) {
        noEventsElement.style.display = 'block';
        return;
    } else {
        noEventsElement.style.display = 'none';
    }
    
    // Создаем карточки для событий
    filteredEvents.forEach(event => {
        // Клонируем шаблон
        const eventCard = document.importNode(eventCardTemplate.content, true);
        
        // Заполняем данными
        const cardElement = eventCard.querySelector('.event-card');
        const imageElement = eventCard.querySelector('.event-image');
        const typeElement = eventCard.querySelector('.event-type');
        const titleElement = eventCard.querySelector('.event-title');
        const dateElement = eventCard.querySelector('.date-text');
        const participantsElement = eventCard.querySelector('.participants-text');
        const formatElement = eventCard.querySelector('.format-text');
        
        // Устанавливаем значения
        cardElement.setAttribute('data-id', event.id);
        imageElement.style.backgroundImage = `url(${event.image})`;
        typeElement.textContent = event.type;
        titleElement.textContent = event.title;
        dateElement.textContent = formatDate(event.date);
        participantsElement.textContent = `${event.participants} участников`;
        formatElement.textContent = event.format;
        
        // Добавляем обработчик клика
        //cardElement.addEventListener('click', () => {
        //   openEventDetails(event.id);
        // });
        
        // Добавляем в DOM
        eventsListElement.appendChild(eventCard);
    });
}

// Обработка клика по фильтру
function handleFilterClick(event) {
    if (event.target.tagName === 'BUTTON') {
        // Убираем активный класс у всех кнопок
        const buttons = filtersElement.querySelectorAll('button');
        buttons.forEach(button => button.classList.remove('active'));
        
        // Добавляем активный класс выбранной кнопке
        event.target.classList.add('active');
        
        // Обновляем активный фильтр
        activeFilter = event.target.getAttribute('data-filter');
        
        // Перерисовываем события
        renderEvents();
    }
}

// Обработка клика по навигации
function handleNavClick(event) {
    const navItem = event.target.closest('.nav-item');
    if (navItem) {
        // Убираем активный класс у всех пунктов
        navItems.forEach(item => item.classList.remove('active'));
        
        // Добавляем активный класс выбранному пункту
        navItem.classList.add('active');
        
        // Обновляем активный пункт
        activeNavItem = navItem.getAttribute('data-nav');
        
        // Здесь будет навигация между разделами
        console.log(`Переход на раздел: ${activeNavItem}`);
    }
}

// Открытие уведомлений
function showNotifications() {
    const notificationsHtml = notifications.map(n => `<li>${n.message}</li>`).join('');
    alert(`Уведомления:\n\n${notifications.map(n => n.message).join('\n')}`);
}

// Открытие страницы события
function openEventDetails(eventId) {
    alert(`Открыть страницу события ${eventId}`);
    // Здесь будет навигация на страницу конкретного события
}

// Инициализация обработчиков событий
function initEventListeners() {
    // Клик по фильтрам
    filtersElement.addEventListener('click', handleFilterClick);
    
    // Клик по навигации
    document.querySelector('.bottom-nav').addEventListener('click', handleNavClick);
    
    // Клик по иконке уведомлений
    //notificationIconElement.addEventListener('click', showNotifications);
}

// Инициализация приложения
function init() {
    initUserData();
    initEventListeners();
    renderEvents();
}

// Запуск приложения после загрузки DOM
document.addEventListener('DOMContentLoaded', init);