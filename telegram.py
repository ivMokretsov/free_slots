import requests


def send_telegram_message(
        bot_token,
        chat_id,
        message,
        disable_notification):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
        'disable_notification': disable_notification
    }
    response = requests.post(url, data=payload)
    return response.json()
