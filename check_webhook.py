import requests

TELEGRAM_BOT_TOKEN = "7366514318:AAFNSvdBe5L9RM27mY9OnBEwRIH2dmizUVs"

# Проверяем текущие настройки webhook
info_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"
response = requests.get(info_url)
print("\nТекущие настройки webhook:")
print(response.json())
