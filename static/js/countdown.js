// Дата начала турнира
const TOURNAMENT_START = new Date('2025-02-01T00:00:00').getTime();

// Функция для добавления ведущего нуля
function padZero(num) {
    return num < 10 ? `0${num}` : num;
}

// Функция обновления статического числа
function updateStaticNumber(element, value) {
    if (element) {
        element.textContent = padZero(value);
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
        document.querySelector('.countdown-timer').innerHTML = '<div class="expired">Турнир начался!</div>';
        return;
    }

    const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

    const daysElement = document.getElementById('days');
    const hoursElement = document.getElementById('hours');
    const minutesElement = document.getElementById('minutes');
    const secondsElement = document.getElementById('seconds');

    if (daysElement) updateStaticNumber(daysElement, days);
    if (hoursElement) updateStaticNumber(hoursElement, hours);
    if (minutesElement) updateStaticNumber(minutesElement, minutes);
    if (secondsElement) updateSeconds(secondsElement, seconds);
}

// Запускаем таймер
document.addEventListener('DOMContentLoaded', () => {
    // Запускаем первое обновление
    updateCountdown();
    
    // Обновляем каждую секунду
    setInterval(updateCountdown, 1000);
});
