import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime
from bs4 import BeautifulSoup


load_dotenv()


def fetch_free_time_slots(employee_id, club_id):
    URL = 'https://reservi.ru/api-fit1c/json/v2/'
    API_KEY = os.getenv('API_KEY')
    HEADERS = {'Content-Type': 'application/json'}
    LANG = 'ru'

    data = {
        'method': 'getFitCalendar',
        'params': {
            'calendarType': 'personal',
            'employee_id': employee_id
        },
        'clubs': {
            club_id: {'id': club_id}
        },
        'api_key': API_KEY,
        'lang': LANG
    }

    response = requests.post(URL, headers=HEADERS, data=json.dumps(data))
    response.raise_for_status()
    response_data = response.json()['SLIDER']['BODY']

    soup = BeautifulSoup(response_data, 'html.parser')
    date_elements = soup.find_all('td', attrs={'data-date': True})
    free_time_slots = []

    for date_element in date_elements:
        date = date_element['data-date']
        time_schedule = date_element.find('div', class_='tm-s')
        if time_schedule:
            free_time_slots.append((date, time_schedule.text.strip()))

    return free_time_slots


def convert_to_datetime(date_str, time_range_str):
    date_format = '%d-%m-%y'
    date = datetime.strptime(date_str, date_format).date()

    start_time_str, end_time_str = time_range_str.split('-')
    time_format = '%H:%M'
    start_time = datetime.strptime(start_time_str, time_format).time()
    end_time = datetime.strptime(end_time_str, time_format).time()

    start_datetime = datetime.combine(date, start_time)
    end_datetime = datetime.combine(date, end_time)

    return start_datetime, end_datetime


def is_time_within_target(target_time_start,
                          target_time_end,
                          slot_start,
                          slot_end):
    slot_start_time = slot_start.time()
    slot_end_time = slot_end.time()

    return (slot_start_time >= target_time_start and
            slot_end_time <= target_time_end)


def slots_have_changed(current_slots):
    base_path = os.path.dirname(__file__)
    slots_file = os.path.join(base_path, 'slots.json')
    if not os.path.exists(slots_file):
        with open(slots_file, 'w') as file:
            json.dump(current_slots, file)
        return True

    with open(slots_file, 'r') as file:
        old_slots = json.load(file)

    if old_slots != current_slots:
        with open(slots_file, 'w') as file:
            json.dump(current_slots, file)
        return True

    return False
