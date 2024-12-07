document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всплывающих подсказок
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip, {
            placement: 'top',
            trigger: 'hover'
        });
    });

    // Обработка отправки формы
    const form = document.getElementById('applicationForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Собираем данные формы
            const formData = new FormData(this);
            
            // Формируем сообщение для Telegram
            let message = '🎮 Новая заявка в RW WOLVES!\n\n';
            message += `👤 Имя: ${formData.get('name')}\n`;
            message += `📱 Telegram: ${formData.get('telegram')}\n`;
            message += `📊 Ранг: ${formData.get('rank')}\n`;
            message += `📈 K/D: ${formData.get('kd')}\n`;
            message += `📞 Телефон: ${formData.get('phone')}\n`;
            message += `🌐 VK: ${formData.get('vk') || 'Не указан'}\n`;
            message += `💭 Комментарий: ${formData.get('comment') || 'Нет комментария'}\n`;
            
            try {
                // Отправляем в Telegram
                const botToken = '7366514318:AAFNSvdBe5L9RM27mY9OnBEwRIH2dmizUVs';
                const chatId = '-1002255169087';
                
                const response = await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        chat_id: chatId,
                        text: message,
                        parse_mode: 'HTML'
                    })
                });

                const result = await response.json();
                
                if (result.ok) {
                    // Показываем уведомление об успехе
                    Swal.fire({
                        title: 'Успешно!',
                        text: 'Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время!',
                        icon: 'success',
                        confirmButtonColor: '#ff4d00'
                    });
                    
                    // Очищаем форму
                    form.reset();
                } else {
                    throw new Error('Ошибка отправки');
                }
            } catch (error) {
                // Показываем уведомление об ошибке
                Swal.fire({
                    title: 'Ошибка!',
                    text: 'Произошла ошибка при отправке заявки. Пожалуйста, попробуйте позже или свяжитесь с администратором.',
                    icon: 'error',
                    confirmButtonColor: '#ff4d00'
                });
            }
        });
    }

    // Анимация для полей формы
    const formInputs = document.querySelectorAll('.form-control');
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
        
        // Проверяем начальное состояние
        if (input.value) {
            input.parentElement.classList.add('focused');
        }
    });
});
