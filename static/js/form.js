// Конфигурация Telegram бота
const TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN';
const TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID';

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

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Показываем анимацию загрузки
            const loadingOverlay = document.createElement('div');
            loadingOverlay.className = 'loading-overlay';
            loadingOverlay.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner"></div>
                    <div class="loading-text">Отправка заявки...</div>
                </div>
            `;
            document.body.appendChild(loadingOverlay);

            // Скрываем предыдущие сообщения
            successMessage.style.display = 'none';
            errorMessage.style.display = 'none';

            try {
                const formData = new FormData(form);
                
                // Получаем информацию о местоположении
                const locationData = await getUserLocation();
                const browserInfo = getBrowserInfo();

                // Добавляем дополнительную информацию в formData
                if (locationData) {
                    Object.entries(locationData).forEach(([key, value]) => {
                        formData.append(`location_${key}`, value);
                    });
                }

                Object.entries(browserInfo).forEach(([key, value]) => {
                    formData.append(`browser_${key}`, value);
                });

                // Добавляем текущее время
                formData.append('submission_time', new Date().toISOString());

                // Добавляем индикатор мобильного устройства
                formData.append('is_mobile', isMobile);

                // Отправляем сообщение в Telegram
                const telegramMessage = `📝 Новая заявка!\n\n${formData.get('nickname')}\n${formData.get('telegram')}\n${formData.get('level')}`;
                const telegramResponse = await sendToTelegram(telegramMessage);

                if (telegramResponse.ok) {
                    const response = await fetch('/submit', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();

                    // Удаляем оверлей загрузки
                    loadingOverlay.remove();

                    if (response.ok && result.success) {
                        successMessage.innerHTML = `
                            <div class="success-animation">
                                <div class="checkmark-circle">
                                    <div class="checkmark draw"></div>
                                </div>
                                <h3>Заявка успешно отправлена!</h3>
                                <p>Мы свяжемся с вами в ближайшее время через Telegram.</p>
                            </div>
                        `;
                        successMessage.style.display = 'block';
                        form.reset();
                        removeImage();

                        // Плавный скролл к сообщению об успехе на мобильных
                        if (isMobile) {
                            successMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    } else {
                        errorMessage.textContent = result.error || 'Произошла ошибка при отправке заявки';
                        errorMessage.style.display = 'block';
                        
                        // Плавный скролл к сообщению об ошибке на мобильных
                        if (isMobile) {
                            errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }
                } else {
                    errorMessage.textContent = 'Произошла ошибка при отправке заявки в Telegram';
                    errorMessage.style.display = 'block';
                    
                    // Плавный скролл к сообщению об ошибке на мобильных
                    if (isMobile) {
                        errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                loadingOverlay.remove();
                errorMessage.textContent = 'Произошла ошибка при отправке заявки';
                errorMessage.style.display = 'block';
                
                // Плавный скролл к сообщению об ошибке на мобильных
                if (isMobile) {
                    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    }
});

// Функция отправки сообщения в Telegram
async function sendToTelegram(message) {
    const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
    const params = {
        chat_id: TELEGRAM_CHAT_ID,
        text: message,
        parse_mode: 'HTML'
    };
    
    return await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(params)
    });
}
