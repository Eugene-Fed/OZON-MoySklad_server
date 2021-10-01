import requests
import json
import datetime

with open('api-keys/api-keys.json') as f:
    api_params = json.load(f)['api_ozon']   # выбираем только данные объекта api_ozon

# Параметры для запроса к серверу API
client_id = api_params['client_id']
api_key = api_params['api_key']
api_domain = api_params['api_domain']
api_url = api_params['api_url']

# Начальная и конечная дата для выгрузки заказов. Текст формата '2021-07-13T00:00:00Z'
# Z на конце = UTF+0 для того, чтобы смена открывалась в 3 ночи по МСК
# Смена начинается и заканчивается в 00:00 для того, чтобы избежать потери заказов между 23:59 и 00:00
date_from = '2021-07-13T00:00:00Z'
date_today = datetime.date.today().strftime("%Y-%m-%d")     # Получаем текущую дату и преобразуем в текст понятный API
date_to = date_today + 'T00:00:00Z'

dir_to = 'asc'                      # Порядок сортировки: asc - по возрастанию, desc - по убыванию
status = ''                         # delivered, cancelled, delivering, awaiting_deliver, awaiting_packaging *не обязат.
limit = 1000                        # Макс. количество выгружаемых заказов от 1 до 1000
offset = 0                          # Кол-во пропускаемых элементов. Если offset = 10, то ответ начнется с 11 заказа
translit = True                     # True, если включена транслитерация адреса из кириллицы в латиницу
analytics_data = False              # Не включать данные аналитики в ответ
financial_data = True               # Включить финансовые данные в ответ, чтобы посчитать общую комиссию с продажи

filter_ = {'since': date_from, 'status': status, 'to': date_to}     # Фильтр для поиска отправленийпо параметрам
with_ = {'analytics_data': analytics_data, 'financial_data': financial_data}    # Доп. поля, для добавления в ответ

# Формируем заголовок и тело запроса к серверу
headers = {'Client-Id': client_id, 'Api-Key': api_key}
request_body = {'dir': dir_to, 'filter': filter_, 'limit': limit, 'offset': offset, 'translit': translit, 'with': with_}

# Отправляем запрос к API ОЗОН для получения списка заказов за указанный ранее период
response_orders = requests.post(api_domain + api_url, headers=headers, json=request_body)
print('Статус запроса: ' + str(response_orders.status_code))                # Вывод в консоль старус ответа сервера
json_orders = response_orders.json()

format_data = json.dumps(json_orders, indent=2, ensure_ascii=False)         # Преобразуем ответ сервера в JSON

print(json.dumps(json_orders, indent=2, ensure_ascii=False))
print('\nКоличество заказов: ' + str(len(json_orders['result'])))
# print(json_orders['result'][0]['order_id'])                            # Номер заказа
# print(json_orders['result'][1]['products'][0]['offer_id'])             # Артикул товара в заказе
# print(response.headers)

# for element in json_orders['result']:
#     print(element['status'] + '\t' + element['created_at'])
#
# with open('data/ozon_orders.json', 'w') as outfile:
#     json.dump(json_orders, outfile, indent=4, ensure_ascii=False)
#      print(format_data)
