// Дата начала турнира (1 февраля 2025 года)
const TOURNAMENT_START = new Date('2025-02-01T00:00:00+03:00').getTime();

// Склонение числительных
function declOfNum(number, titles) {
    const cases = [2, 0, 1, 1, 1, 2];
    return titles[(number % 100 > 4 && number % 100 < 20) ? 2 : cases[(number % 10 < 5) ? number % 10 : 5]];
}

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

    const labels = {
        days: document.querySelector('.countdown-section:nth-child(1) .number-label'),
        hours: document.querySelector('.countdown-section:nth-child(3) .number-label'),
        minutes: document.querySelector('.countdown-section:nth-child(5) .number-label'),
        seconds: document.querySelector('.countdown-section:nth-child(7) .number-label')
    };

    // Обновляем числа
    if (elements.days) updateStaticNumber(elements.days, days);
    if (elements.hours) updateStaticNumber(elements.hours, hours);
    if (elements.minutes) updateStaticNumber(elements.minutes, minutes);
    if (elements.seconds) updateSeconds(elements.seconds, seconds);

    // Обновляем подписи с правильными склонениями
    if (labels.days) labels.days.textContent = declOfNum(days, ['день', 'дня', 'дней']);
    if (labels.hours) labels.hours.textContent = declOfNum(hours, ['час', 'часа', 'часов']);
    if (labels.minutes) labels.minutes.textContent = declOfNum(minutes, ['минута', 'минуты', 'минут']);
    if (labels.seconds) labels.seconds.textContent = declOfNum(seconds, ['секунда', 'секунды', 'секунд']);
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
