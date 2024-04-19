import os
import traceback
import logging
from dotenv import load_dotenv
from datetime import datetime
from func import (
    fetch_free_time_slots,
    convert_to_datetime,
    is_time_within_target,
    slots_have_changed
)
from telegram import send_telegram_message

# Настройка логгера
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)

# Загрузка переменных окружения
load_dotenv()

# Получение токена бота и идентификатора чата из переменных окружения
bot_token = os.getenv('BOT_TOKEN')
chat_id = os.getenv('CHAT_ID')

# Идентификаторы сотрудника и клуба
employee_id = '76f2f0e6-2626-11ee-8bf7-005056833ca1'
club_id = 'a0816762-f3c3-11ec-7f9d-00505683b2c0'

# Целевое время для проверки доступности слотов
target_time_start = datetime.strptime('08:00', '%H:%M').time()
target_time_end = datetime.strptime('21:00', '%H:%M').time()

# Первоначальная настройка уведомлений
disable_notification = False

try:
    free_slots = fetch_free_time_slots(employee_id, club_id)
    if not free_slots:
        if slots_have_changed(free_slots):
            message = 'Нет доступных слотов'
            send_telegram_message(
                bot_token=bot_token,
                chat_id=chat_id,
                message=message,
                disable_notification=disable_notification
            )
            logging.info(f'Sending message: {message}')
        else:
            message = 'Без изменений. Нет доступных слотов'
            logging.info(f'{message}')

    else:
        # Конвертация слотов в формат datetime
        free_slots_dt = [
            convert_to_datetime(date_str, time_range_str)
            for date_str, time_range_str in free_slots
        ]
        sorted_time_slots = sorted(free_slots_dt, key=lambda x: x[0])

        target_slots = []
        for start, end in sorted_time_slots:
            if is_time_within_target(
                target_time_start,
                target_time_end,
                start,
                end
            ):
                slot_str = (
                    f'{start.strftime("%d-%m-%Y %H:%M")} - '
                    f'{end.strftime("%H:%M")}'
                )
                target_slots.append(slot_str)

        if slots_have_changed(target_slots):
            intro_text = 'Доступные слоты в удобное время:'
            message = f'{intro_text}\n' + '\n'.join(target_slots)
            send_telegram_message(
                bot_token=bot_token,
                chat_id=chat_id,
                message=message,
                disable_notification=disable_notification
            )
            logging.info(f'Sending message: {message}')
        else:
            message = 'Без изменений'
            logging.info(f'{message}')


except Exception as e:
    traceback_details = traceback.format_exc()
    logging.error(f'An error occurred: {e}\n'
                  f'Detailed traceback:\n{traceback_details}')

    message = (f'An error occurred: {e}\n'
               f'For more details, please check the server logs.')
    send_telegram_message(
        bot_token=bot_token,
        chat_id=chat_id,
        message=message,
        disable_notification=disable_notification
    )
