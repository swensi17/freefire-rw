import requests

TELEGRAM_BOT_TOKEN = "7366514318:AAFNSvdBe5L9RM27mY9OnBEwRIH2dmizUVs"

# Сначала удалим текущий webhook
delete_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
print("Удаляем текущий webhook...")
response = requests.get(delete_url)
print(response.json())

# Теперь установим новый webhook
ngrok_url = input("Введите ваш ngrok URL (https://...): ")
webhook_url = f"{ngrok_url}/webhook"
set_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
data = {
    "url": webhook_url,
    "allowed_updates": ["callback_query", "message"]
}

print("\nУстанавливаем новый webhook...")
response = requests.post(set_url, json=data)
print(response.json())

# Проверим информацию о webhook
info_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"
print("\nПроверяем информацию о webhook...")
response = requests.get(info_url)
print(response.json())
