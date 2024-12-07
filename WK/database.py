import sqlite3
import logging

logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect('applications.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT NOT NULL,
            nickname TEXT NOT NULL,
            telegram TEXT NOT NULL,
            message_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_application(account_id, nickname, telegram, message_id):
    try:
        conn = sqlite3.connect('applications.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO applications (account_id, nickname, telegram, message_id)
            VALUES (?, ?, ?, ?)
        ''', (account_id, nickname, telegram, message_id))
        application_id = c.lastrowid
        conn.commit()
        return application_id
    except Exception as e:
        logger.error(f"Ошибка при сохранении заявки: {str(e)}")
        return None
    finally:
        conn.close()

def get_application_status(account_id):
    try:
        conn = sqlite3.connect('applications.db')
        c = conn.cursor()
        c.execute('SELECT created_at FROM applications WHERE account_id = ? ORDER BY created_at DESC LIMIT 1', (account_id,))
        result = c.fetchone()
        return "sent" if result else None
    except Exception as e:
        logger.error(f"Ошибка при получении статуса заявки: {str(e)}")
        return None
    finally:
        conn.close()
