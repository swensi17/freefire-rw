from flask import Flask, request, jsonify, render_template, redirect
import requests
import os
import json
import logging
from werkzeug.utils import secure_filename
from database import init_db, save_application, get_application_status

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

TELEGRAM_BOT_TOKEN = "7366514318:AAFNSvdBe5L9RM27mY9OnBEwRIH2dmizUVs"
TELEGRAM_CHAT_ID = "-1002255169087"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_to_telegram(data, photo_path):
    # Форматируем сообщение с HTML-разметкой
    message = f"""<b>🎮 Новая заявка в гильдию RW WOLVES!</b>

<b>👤 Игрок:</b> {data['nickname']}
<b>🆔 ID:</b> {data['account_id']}
<b>👑 Ранг:</b> {data['rank']}
<b>📊 Уровень:</b> {data['level']}
<b>⏳ Опыт игры:</b> {data['experience']} мес.

<b>📈 Статистика:</b>
• K/D: {data['kd']}
• Винрейт: {data['winrate']}
• Игровое время: {data['playtime']} ч/день

<b>📱 Контакты:</b>
• Telegram: {data['telegram']}
• Телефон: {data['phone']}"""

    # Создаем кнопку для связи с кандидатом
    telegram_username = data['telegram'].replace('@', '')
    keyboard = {
        "inline_keyboard": [[
            {
                "text": "💬 Написать кандидату",
                "url": f"https://t.me/{telegram_username}"
            }
        ]]
    }

    try:
        # Отправляем фото
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            params = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': message,
                'parse_mode': 'HTML',
                'reply_markup': json.dumps(keyboard)
            }
            response = requests.post(
                f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto',
                data=params,
                files=files
            )
            
        if response.status_code == 200:
            message_id = response.json()['result']['message_id']
            return True, message_id
        else:
            logger.error(f"Failed to send message to Telegram: {response.text}")
            return False, None
            
    except Exception as e:
        logger.error(f"Error sending message to Telegram: {str(e)}")
        return False, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Получаем данные формы
        data = {
            'nickname': request.form['nickname'],
            'account_id': request.form['account_id'],
            'rank': request.form['rank'],
            'level': request.form['level'],
            'experience': request.form['experience'],
            'telegram': request.form['telegram'],
            'phone': request.form['phone'],
            'kd': request.form['kd'],
            'winrate': request.form['winrate'],
            'playtime': request.form['playtime']
        }

        # Проверяем, загружено ли фото
        if 'profile_photo' not in request.files:
            return jsonify({'success': False, 'error': 'Не загружено фото профиля'})
            
        photo = request.files['profile_photo']
        if photo.filename == '':
            return jsonify({'success': False, 'error': 'Не выбран файл'})
            
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Создаем директорию, если она не существует
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            # Сохраняем фото
            photo.save(photo_path)
            
            # Отправляем в Telegram
            success, message_id = send_to_telegram(data, photo_path)
            if success:
                # Сохраняем в базу данных
                save_application(
                    account_id=data['account_id'],
                    nickname=data['nickname'],
                    telegram=data['telegram'],
                    message_id=message_id
                )
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Ошибка отправки в Telegram'})
        else:
            return jsonify({'success': False, 'error': 'Недопустимый формат файла'})
            
    except Exception as e:
        logger.error(f"Error processing submission: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/check_status', methods=['POST'])
def check_status():
    try:
        account_id = request.json.get('account_id')
        status = get_application_status(account_id)
        return jsonify({'status': status if status else 'not_found'})
    except Exception as e:
        logger.error(f"Ошибка при проверке статуса: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    # Инициализируем базу данных при запуске
    init_db()
    # Создаем папку для загрузок, если её нет
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
