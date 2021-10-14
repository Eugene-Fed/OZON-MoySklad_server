import requests
import json
import datetime
from datetime import timedelta

with open('api-keys/api-keys.json') as f:
    api_params = json.load(f)['api_ozon']   # выбираем только данные объекта api_ozon

# Параметры, необходимые для запроса к серверу API
client_id = api_params['client_id']
api_key = api_params['api_key']
api_domain = api_params['api_domain']
api_url = api_params['api_url']

# Начальная и конечная дата для выгрузки заказов. Текст формата '2021-07-13T00:00:00Z'
# Z на конце = UTF+0 для того, чтобы смена открывалась в 3 ночи по МСК
# Смена начинается и заканчивается в 00:00 для того, чтобы избежать потери заказов между 23:59 и 00:00
# TODO вынести количество дней для выгрузки в отдельный файл настроек
date_from_decrease_time = timedelta(days=45)        # Количество дней от текущего для расчета диапазона загрузки заказов
date_today = datetime.date.today().strftime("%Y-%m-%d")     # Получаем текущую дату и преобразуем в текст понятный API
date_start_day = datetime.date.today() - date_from_decrease_time  # Получаем дату за N дней до сегодняшней
# TODO вынесли время начала/завершения смены (3 часа ночи) в отдельный файл настроек
date_from = date_start_day.strftime("%Y-%m-%d") + 'T03:00:00Z'    # Дата начала выгрузки заказов
date_to = date_today + 'T03:00:00Z'                         # Добавляем время начала суток в формате, понятном OZON
# Загружаем только заказы по вчерашний день включительно, заказы за сегодня нам не нужны.

dir_to = 'asc'                      # Порядок сортировки: asc - по возрастанию, desc - по убыванию
status = 'delivered'                # delivered, cancelled, delivering, awaiting_deliver, awaiting_packaging *не обязат.
limit = 1000                        # Макс. количество выгружаемых заказов от 1 до 1000
offset = 0                          # Кол-во пропускаемых элементов. Если offset = 10, то ответ начнется с 11 заказа
translit = True                     # True, если включена транслитерация адреса из кириллицы в латиницу
analytics_data = False              # Не включать данные аналитики в ответ
financial_data = False               # Включить финансовые данные в ответ, чтобы посчитать общую комиссию с продажи

filter_ = {'since': date_from, 'status': status, 'to': date_to}     # Фильтр для поиска отправленийпо параметрам
with_ = {'analytics_data': analytics_data, 'financial_data': financial_data}    # Доп. поля, для добавления в ответ

# Формируем заголовок и тело запроса к серверу
headers = {'Client-Id': client_id, 'Api-Key': api_key}
request_body = {'dir': dir_to, 'filter': filter_, 'limit': limit, 'offset': offset, 'translit': translit, 'with': with_}

# Отправляем запрос к API ОЗОН для получения списка заказов за указанный ранее период
response_orders = requests.post(api_domain + api_url, headers=headers, json=request_body)
print('Статус запроса: ' + str(response_orders.status_code))                # Статус ответа сервера - вывод в консоль

json_orders = response_orders.json()                                        # Преобразуем ответ сервера в json
format_data = json.dumps(json_orders, indent=2, ensure_ascii=False)         # Преобразуем json в формат с отступами
# print(format_data)                                                        # Дебажный коммент

print('\nКоличество заказов: ' + str(len(json_orders['result'])))
# print(json_orders['result'][0]['order_id'])                            # Номер заказа
# print(json_orders['result'][1]['products'][0]['offer_id'])             # Артикул товара в заказе
# print(response.headers)

# for element in json_orders['result']:
#     print(element['status'] + '\t' + element['created_at'])
#
# TODO заменить использование файла на прямую передачу данных из объекта класса Ozon_Import в скрипт moysklad_export.py
with open('data/ozon_orders.json', 'w') as outfile:  # Проверка наличия файла не требуется, т.к. 'w' создает файл
    json.dump(json_orders, outfile, indent=4, ensure_ascii=False)
    print(format_data)
