from django.conf import settings

import requests


def send_telegram_notification(chat_id, text):
    """
    Отправляет текстовое сообщение в указанный чат Telegram.
    """
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://telegram.org{token}/sendMessage"

    payload = {"chat_id": chat_id, "text": text}

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки в Telegram: {e}")
        return False
