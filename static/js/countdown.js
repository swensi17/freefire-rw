// Дата начала турнира (1 февраля 2025 года)
const TOURNAMENT_START = new Date('2025-02-01T00:00:00+03:00').getTime();

// Функция для добавления ведущего нуля
function padZero(num) {
    return num < 10 ? `0${num}` : num;
}

// Функция обновления статического числа
function updateStaticNumber(element, value) {
    if (element) {
        const formattedValue = padZero(value);
        if (element.textContent !== formattedValue) {
            element.textContent = formattedValue;
            element.classList.add('number-updated');
            setTimeout(() => {
                element.classList.remove('number-updated');
            }, 300);
        }
    }
}

// Функция обновления секунд с улучшенной анимацией
function updateSeconds(element, value) {
    if (element) {
        const formattedValue = padZero(value);
        if (element.textContent !== formattedValue) {
            element.classList.add('changing');
            element.textContent = formattedValue;
            
            // Синхронизируем мигание двоеточий
            document.querySelectorAll('.countdown-separator').forEach(separator => {
                separator.classList.add('pulse');
                setTimeout(() => {
                    separator.classList.remove('pulse');
                }, 400);
            });
            
            setTimeout(() => {
                element.classList.remove('changing');
            }, 200);
        }
    }
}

// Функция обновления таймера
function updateCountdown() {
    const now = new Date().getTime();
    const timeLeft = TOURNAMENT_START - now;

    if (timeLeft <= 0) {
        const timerContainer = document.querySelector('.countdown-timer');
        if (timerContainer) {
            timerContainer.innerHTML = '<div class="expired">Турнир начался!</div>';
        }
        return;
    }

    const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

    const elements = {
        days: document.getElementById('days'),
        hours: document.getElementById('hours'),
        minutes: document.getElementById('minutes'),
        seconds: document.getElementById('seconds')
    };

    // Проверяем существование элементов перед обновлением
    if (elements.days) updateStaticNumber(elements.days, days);
    if (elements.hours) updateStaticNumber(elements.hours, hours);
    if (elements.minutes) updateStaticNumber(elements.minutes, minutes);
    if (elements.seconds) updateSeconds(elements.seconds, seconds);
}

// Инициализация таймера
function initCountdown() {
    // Проверяем наличие элементов таймера
    const timerElements = document.querySelectorAll('.countdown-timer .number-block');
    if (timerElements.length === 0) {
        console.warn('Timer elements not found');
        return;
    }

    // Первое обновление
    updateCountdown();
    
    // Обновляем каждую секунду
    const interval = setInterval(updateCountdown, 1000);
    
    // Синхронизируем анимацию разделителей
    document.querySelectorAll('.countdown-separator').forEach((separator, index) => {
        separator.style.animationDelay = `${index * 0.1}s`;
    });

    // Сохраняем interval ID для возможной очистки
    window.countdownInterval = interval;
}

// Запускаем таймер после загрузки DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCountdown);
} else {
    initCountdown();
}
