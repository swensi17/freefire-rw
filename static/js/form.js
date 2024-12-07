document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('applicationForm');
    const successMessage = document.getElementById('successMessage');
    const errorMessage = document.getElementById('errorMessage');
    const screenshotInput = document.getElementById('screenshot');
    const imagePreview = document.getElementById('imagePreview');

    // Функция для предпросмотра изображения
    screenshotInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.style.display = 'block';
                imagePreview.querySelector('img').src = e.target.result;
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
                } else {
                    errorMessage.textContent = result.error || 'Произошла ошибка при отправке заявки';
                    errorMessage.style.display = 'block';
                }
            } catch (error) {
                console.error('Error:', error);
                loadingOverlay.remove();
                errorMessage.textContent = 'Произошла ошибка при отправке заявки';
                errorMessage.style.display = 'block';
            }
        });
    }
});
