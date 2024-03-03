import platform

import aiohttp
import asyncio

import sys
import json
from copy import deepcopy
from datetime import datetime, timedelta

# Змінні
API_PB_archive = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='
CURRENCIES = ['EUR', 'USD']
dict_rates_one_day = {}
list_result_all_days = []
for curr in CURRENCIES:
    dict_rates_one_day.update ({curr: {
                        'sale': None,
                        'purchase': None}
                        })

# Функція із аналізом тіла відповіді від АПІ Приватбанку
def needed_dict (result_from_api_pb):
    dict_result_one_day = {}
    date = result_from_api_pb ['date']
    rates_of_day_from_result = result_from_api_pb ['exchangeRate']

    for curr in dict_rates_one_day.keys():
        for each_curr in rates_of_day_from_result:
            if each_curr ['currency'] == curr:
                dict_rates_one_day [curr] = {'sale': each_curr ['saleRate'], 
                                     'purchase': each_curr ['purchaseRate']}
    dict_result_one_day [date] = dict_rates_one_day
    return dict_result_one_day

# Функція із запитом до АПІ Приватбанку
async def request_exch_rates_to_privat(day):
    API_PB_archive_full = f'{API_PB_archive}{day}'
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(API_PB_archive_full) as response:
                if response.status == 200:
                    result_full = await response.json()
                else:
                    print(f"Error status: {response.status} for {API_PB_archive_full} for day {day}")
                try:
                    return needed_dict (result_full)
                except UnboundLocalError:
                    print ('Server error')
        except aiohttp.ClientConnectorError as err:
            print(f'Connection error: {API_PB_archive_full}', str(err))

# Функція із розрахунком інтервалу днів для запиту і власне запиту
def main (days_as_str):
    period_for_request = []

    for day in range (0, int(days_as_str)):
        date_for_add = datetime.today().date() - timedelta(days=day)
        period_for_request.append (date_for_add.strftime('%d.%m.%Y'))

    for each_day in period_for_request:
        print ('--------------------------------------------------')
        print (f'Calc for {each_day}')
        each_day_rates = asyncio.run(request_exch_rates_to_privat(each_day))
        each_day_rates = deepcopy (each_day_rates) # deepcopy(), бо інакше міняє курси усіх днів на останній
        list_result_all_days.append (each_day_rates)
    
    print (f'\nExchange rates of EUR and USD for {days_as_str} last days')
    print(json.dumps (list_result_all_days, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    days = sys.argv [1]
    while True:
        try:
            if not (1 <= int (days) <= 10):
                days = input ('Введіть ціле число днів між 1 та 10: ')
            else:
                break
        except ValueError:
            days = input ('Введіть ціле число днів між 1 та 10: ')
    main (days)
