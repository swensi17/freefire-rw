// Конфигурация Telegram
const TELEGRAM_BOT_TOKEN = '6893908848:AAEPGmxXNqQONWXbzUlpvZJgKJcGVZqJxYc';
const TELEGRAM_CHAT_ID = '-1002255169087';

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('applicationForm');
    const successMessage = document.getElementById('successMessage');
    const errorMessage = document.getElementById('errorMessage');
    const screenshotInput = document.getElementById('screenshot');
    const imagePreview = document.getElementById('imagePreview');

    // Определяем, является ли устройство мобильным
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

    // Оптимизация для мобильных устройств
    if (isMobile) {
        // Добавляем поддержку touch-событий
        form.addEventListener('touchstart', function(e) {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
                e.target.focus();
            }
        }, { passive: true });

        // Оптимизация загрузки изображений для мобильных устройств
        if (screenshotInput) {
            screenshotInput.accept = 'image/*';
            screenshotInput.capture = 'environment';
        }

        // Улучшаем скролл к полям с ошибками на мобильных
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('invalid', function(e) {
                e.preventDefault();
                this.scrollIntoView({ behavior: 'smooth', block: 'center' });
            });
        });
    }

    // Функция для предпросмотра изображения с оптимизацией для мобильных
    screenshotInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Проверяем размер файла (максимум 5MB для мобильных)
            if (isMobile && file.size > 5 * 1024 * 1024) {
                alert('Размер файла слишком большой. Максимальный размер: 5MB');
                this.value = '';
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                // Оптимизация предпросмотра для мобильных
                const img = new Image();
                img.onload = function() {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    
                    // Уменьшаем размер превью для мобильных
                    const maxWidth = isMobile ? 800 : 1200;
                    const maxHeight = isMobile ? 800 : 1200;
                    
                    let width = img.width;
                    let height = img.height;

                    if (width > height) {
                        if (width > maxWidth) {
                            height *= maxWidth / width;
                            width = maxWidth;
                        }
                    } else {
                        if (height > maxHeight) {
                            width *= maxHeight / height;
                            height = maxHeight;
                        }
                    }

                    canvas.width = width;
                    canvas.height = height;
                    ctx.drawImage(img, 0, 0, width, height);

                    imagePreview.style.display = 'block';
                    imagePreview.querySelector('img').src = canvas.toDataURL('image/jpeg', 0.8);
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    // Функция для удаления изображения
    window.removeImage = function() {
        imagePreview.style.display = 'none';
        imagePreview.querySelector('img').src = '#';
        screenshotInput.value = '';
    };

    async function getUserLocation() {
        try {
            const response = await fetch('https://ipapi.co/json/');
            const data = await response.json();
            return {
                ip: data.ip,
                city: data.city,
                region: data.region,
                country: data.country_name,
                postal: data.postal,
                latitude: data.latitude,
                longitude: data.longitude,
                timezone: data.timezone,
                isp: data.org
            };
        } catch (error) {
            console.error('Error getting location:', error);
            return null;
        }
    }

    function getBrowserInfo() {
        return {
            userAgent: navigator.userAgent,
            language: navigator.language,
            platform: navigator.platform,
            screenResolution: `${window.screen.width}x${window.screen.height}`,
            colorDepth: window.screen.colorDepth,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            timezoneOffset: new Date().getTimezoneOffset()
        };
    }

    if (form) {
        // Добавляем обработку offline/online состояний
        window.addEventListener('online', function() {
            form.querySelector('button[type="submit"]').disabled = false;
            const offlineMessage = document.getElementById('offlineMessage');
            if (offlineMessage) offlineMessage.style.display = 'none';
        });

        window.addEventListener('offline', function() {
            form.querySelector('button[type="submit"]').disabled = true;
            const offlineMessage = document.getElementById('offlineMessage') || 
                (() => {
                    const msg = document.createElement('div');
                    msg.id = 'offlineMessage';
                    msg.className = 'alert alert-warning';
                    msg.textContent = 'Нет подключения к интернету';
                    form.insertBefore(msg, form.firstChild);
                    return msg;
                })();
            offlineMessage.style.display = 'block';
        });

        // Функция для отправки сообщения с фото в Telegram
        async function sendTelegramMessage(formData, photoUrl) {
            try {
                // Формируем текст сообщения
                const message = `🐺 Новая заявка в RW WOLVES!\n\n` +
                    `👤 Никнейм: ${formData.nickname}\n` +
                    `📱 Telegram: ${formData.telegram}\n` +
                    `📊 Уровень: ${formData.level}\n` +
                    `🎮 K/D: ${formData.kd}\n` +
                    `🌟 Опыт: ${formData.experience}\n` +
                    `💬 О себе: ${formData.about}\n\n` +
                    `📅 Дата заявки: ${new Date().toLocaleString('ru-RU')}`;

                // Отправляем фото с подписью
                const response = await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendPhoto`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        chat_id: TELEGRAM_CHAT_ID,
                        photo: photoUrl,
                        caption: message,
                        parse_mode: 'HTML'
                    })
                });

                if (!response.ok) {
                    throw new Error('Ошибка отправки сообщения в Telegram');
                }

                return true;
            } catch (error) {
                console.error('Ошибка:', error);
                return false;
            }
        }

        // Функция для показа сообщения об успехе/ошибке
        function showMessage(type, text) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type}`;
            alertDiv.innerHTML = `<div class="${type}-message"><i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>${text}</div>`;
            
            const form = document.querySelector('form');
            form.parentNode.insertBefore(alertDiv, form);
            
            setTimeout(() => alertDiv.remove(), 5000);
        }

        // Обработчик отправки формы
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Получаем данные формы
            const formData = {
                nickname: this.querySelector('[name="nickname"]').value,
                telegram: this.querySelector('[name="telegram"]').value,
                level: this.querySelector('[name="level"]').value,
                kd: this.querySelector('[name="kd"]').value,
                experience: this.querySelector('[name="experience"]').value,
                about: this.querySelector('[name="about"]').value
            };

            // URL изображения профиля по умолчанию
            const defaultProfileImage = 'https://raw.githubusercontent.com/swensi17/freefire-rw/master/static/images/profile.png';

            // Добавляем индикатор загрузки
            const submitButton = this.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner"></span>Отправка...';

            try {
                // Отправляем сообщение в Telegram
                const success = await sendTelegramMessage(formData, defaultProfileImage);
                
                if (success) {
                    showMessage('success', 'Заявка успешно отправлена! Мы свяжемся с вами в Telegram.');
                    this.reset(); // Очищаем форму
                } else {
                    showMessage('danger', 'Произошла ошибка при отправке заявки. Пожалуйста, попробуйте позже.');
                }
            } catch (error) {
                console.error('Ошибка:', error);
                showMessage('danger', 'Произошла ошибка при отправке заявки. Пожалуйста, попробуйте позже.');
            } finally {
                // Восстанавливаем кнопку
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            }
        });
    }
});
