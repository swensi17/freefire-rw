// Дата начала турнира
const TOURNAMENT_START = new Date('2025-02-01T00:00:00').getTime();

// Функция для добавления ведущего нуля
const padZero = (num) => num.toString().padStart(2, '0');

// Функция обновления статического числа
function updateStaticNumber(element, value) {
    const formattedValue = value.toString().padStart(2, '0');
    element.textContent = formattedValue;
}

// Функция обновления секунд с улучшенной анимацией
function updateSeconds(element, value) {
    const formattedValue = value.toString().padStart(2, '0');
    if (element.textContent !== formattedValue) {
        // Добавляем класс для начала анимации
        element.classList.add('changing');
        
        // Синхронизируем мигание двоеточий
        document.querySelectorAll('.countdown-separator').forEach(separator => {
            separator.classList.add('pulse');
            // Сбрасываем анимацию через то же время, что и у секунд
            setTimeout(() => {
                separator.classList.remove('pulse');
            }, 400);
        });
        
        // Ждем половину времени анимации перед обновлением числа
        setTimeout(() => {
            element.textContent = formattedValue;
            
            // Используем requestAnimationFrame для плавного возврата
            requestAnimationFrame(() => {
                element.classList.remove('changing');
            });
        }, 200);
    }
}

// Функция обновления таймера
function updateCountdown() {
    const now = new Date().getTime();
    const targetDate = new Date('February 1, 2025 00:00:00').getTime();
    const timeLeft = targetDate - now;

    if (timeLeft <= 0) {
        document.querySelector('.countdown-timer').innerHTML = '<div class="expired">Турнир начался!</div>';
        return;
    }

    const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

    // Update static numbers
    updateStaticNumber(document.getElementById('days'), days);
    updateStaticNumber(document.getElementById('hours'), hours);
    updateStaticNumber(document.getElementById('minutes'), minutes);

    // Update seconds with enhanced animation
    const secondsElement = document.getElementById('seconds');
    if (secondsElement) {
        updateSeconds(secondsElement, seconds);
    }
}

// Синхронизируем начальную анимацию двоеточий
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.countdown-separator').forEach((separator, index) => {
        separator.style.animationDelay = `${index * 0.1}s`;
    });
});

// Initial update
updateCountdown();

// Update every second
setInterval(updateCountdown, 1000);
