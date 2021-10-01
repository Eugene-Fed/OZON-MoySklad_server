import requests
import json
from datetime import datetime, timedelta, date, time

with open('api-keys/api-keys.json') as f:                       # Получаем параметры для отправки запроса на сервер
    api_params = json.load(f)['api_moysklad']

api_key = api_params['api_key']                                 # Получаем ключ API MoySklad
api_domain = api_params['api_domain']                           # Получаем домен API
api_url = api_params['api_url']                                 # Получаем основной путь для работы с API

with open('data/retailShifts.json') as f:                            # Файл с открытыми сменами МойСклад
    moysklad_retailShifts = json.load(f)
print('Список открытых смен:')
print(json.dumps(moysklad_retailShifts, indent=2, ensure_ascii=False))

with open('data/ozon_orders.json') as f:                        # Открываем файл с заказами ОЗОН за все время
    ozon_orders = json.load(f)

# МойСклад не принимает формат ДатаВремя с конечным Z, поэтому убираем его перед отправкой запроса
# Надо иметь ввиду, что в МойСклад нельзя отправит заказ с датой раньше, чем дата открытия смены,
# Как следствие при выгрузке нам практически не пригодится поле с датой оформления заказа из файла выгрузки ОЗОН
# Только если мы будем скриптом по расписанию ежесуточно открывать смену в полночь и в дальнейшем в смену
# на соответствуюущую дату отправлять оформленные заказы
order_date = ozon_orders['result'][0]['created_at']        # получаем строку с датой/временем первого заказа из списка
order_date = datetime.fromisoformat(order_date[:-1])      # преобразуем в формата даты/времени, убирая конечный Z
print('Тип переменной order_date: ' + str(type(order_date)))
print(order_date)

# Создаем переменную формата ДатаВремя со значением 1 минута для того, чтобы в цикле выгрузки заказов озон
# в смену МойСклад, каждый следующий заказ приходил на 1 минуту позже, чем предыдущий, начиная с момента открытия смены
# Эта головомойка нужна временно для выгрузки старых заказов, созданных ранее, т.к. в МойСклад дата оформления заказа
# Должна быть позже даты открытия смены. При этом невозможно октрыть смену задним числом. По идее, возможно отправить
# Все заказы с одним значением времени, но дабы избежать возможных проблем сделаем это с зареджкой в 1 минуту
increase_time = timedelta(minutes=1)
print('Тип переменной increase_time: ' + str(type(increase_time)))
print(increase_time)
new_time = order_date + increase_time
print(new_time)

# utc3 = datetime.time(3, 0, 0)
# orders_data = datetime.strftime("%Y-%m-%d %H:%M:%S", orders_data)


# print(order_data.strftime("%Y-%m-%d %H:%M:%S"))


# filter_ = {'since':date_from, 'status':status, 'to':date_to}
# with_ = {'analytics_data':analytics_data, 'financial_data':financial_data}

# 'Content-Type': 'application/json' - указывать не обязательно,
# если реквест используется с декодером (request.post(json=dataset))
headers = {'Authorization': 'Bearer ' + api_key}
# request_body = {'dir':dir_to, 'filter':filter_, 'limit':limit, 'offset':offset,\
#                    'translit':translit, 'with':with_}
request_body = {}

# response = requests.post(api_domain + api_url + 'retaildemand', headers=headers, json=request_body)
# data = response.json()
# print(response.status_code)

# print(data)

