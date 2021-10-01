import requests
import json

with open('api-keys/api-keys.json') as f:
    api_params = json.load(f)['api_ozon']   # выбираем только данные объекта api_ozon

# Параметры для запроса к серверу API
client_id = api_params['client_id']
api_key = api_params['api_key']
api_domain = api_params['api_domain']
api_url = api_params['api_url']

dir_to = 'asc'                          # порядок сортировки: asc - по возрастанию, desc - по убыванию
date_from = '2021-07-13T00:00:00Z'      # Начальная и конечная дата для выгрузки заказов
# date_from = '2021-09-30T00:00:00Z'
date_to = '2021-10-30T23:59:59Z'        # Z = UTF+0 для того, чтобы смена открывалась/закрывалась в 3 ночи по МСК
# status = 'delivered'                    # delivered - только доставленные/выкупленные заказы *не обязательный параметр
status = ''
limit = 1000                               # Макс. количество выгружаемых заказов от 1 до 1000
offset = 0                              # Кол-во пропускаемых элементов. Если offset = 10, то ответ начнется с 11 заказа
translit = True                         # True, если включена транслитерация адреса из кириллицы в латиницу
analytics_data = False                  # Не включать данные аналитики в ответ
financial_data = True                   # Включить финансовые данные в ответ, чтобы посчитать общую комиссию с продажи

filter_ = {'since': date_from, 'status': status, 'to': date_to}     # Фильтр для поиска отправленийпо параметрам
with_ = {'analytics_data': analytics_data, 'financial_data': financial_data}    # Доп. поля, для добавления в ответ

# Формируем заголовок и тело запроса к серверу
headers = {'Client-Id': client_id, 'Api-Key': api_key}
request_body = {'dir': dir_to, 'filter': filter_, 'limit': limit, 'offset': offset, 'translit': translit, 'with': with_}

# Отправляем запрос к API ОЗОН для получения списка заказов за указанный ранее период
response_orders = requests.post(api_domain + api_url, headers=headers, json=request_body)
print(response_orders.status_code)              # Вывод в консоль старус ответа сервера
json_orders = response_orders.json()

format_data = json.dumps(json_orders, indent=2, ensure_ascii=False)  # Преобразуем ответ сервера в JSON

print(json.dumps(json_orders, indent=2, ensure_ascii=False))
print('\nКоличество заказов: ' + str(len(json_orders['result'])))
# print(json_orders['result'][0]['order_id'])                            # Номер заказа
# print(json_orders['result'][1]['products'][0]['offer_id'])             # Артикул товара в заказе
# print(response.headers)

for element in json_orders['result']:
    print(element['status'])

with open('data/ozon_orders.json', 'w') as outfile:
    json.dump(json_orders, outfile, indent=4, ensure_ascii=False)
#      print(format_data)
