import requests
import json
from datetime import datetime, timedelta, date, time

with open('api-keys/api-keys.json') as f:                       # Получаем параметры для отправки запроса на сервер
    api_params = json.load(f)['api_moysklad']

api_key = api_params['api_key']                                 # Получаем ключ API MoySklad
api_domain = api_params['api_domain']                           # Получаем домен API
api_url = api_params['api_url']                                 # Получаем основной путь для работы с API
api_name_product = api_params['product']['name']                # Имя бъекта, для добавление в URL запроса Товара

headers = {'Authorization': 'Bearer ' + api_key}


# Функция для определения meta-идентификатора товара в МойСклад по его артикулу из ОЗОН
def ozon_moysklad_id_converter(vendor_code):
    response_product = requests.get(api_domain + api_url + api_name_product + '/metadata', headers=headers,
                                    params='filter=article~'+vendor_code[:5])
    print("Статус запроса Мета Товара: " + str(response_product.status_code))
    print(json.dumps(response_product.json(), indent=4, ensure_ascii=False))
    # moysklad_product_id = response_product.json()['attributes'][0]['id']   # Получаем мета-id первого товара из списка
    # print("Статус запроса Мета Товара: " + str(response_product.status_code) + ', Артикул: ' + vendor_code +
    #       ' соответствует MoySklad ID: ' + moysklad_product_id)
    # return moysklad_product_id
    return vendor_code


with open('data/retailShifts.json') as f:                       # Файл с открытыми сменами МойСклад
    moysklad_retailShifts = json.load(f)

retailShift_create_date = moysklad_retailShifts['retailShifts'][0]['created']      # ДатаВремя создания смены в МойСклад

print('Список открытых смен:')
print(json.dumps(moysklad_retailShifts, indent=2, ensure_ascii=False))

with open('data/ozon_orders.json') as f:                        # Открываем файл с заказами ОЗОН за все время
    ozon_orders = json.load(f)

# Создаем переменную формата ДатаВремя со значением 1 минута для того, чтобы в цикле выгрузки заказов озон
# в смену МойСклад, каждый следующий заказ приходил на 1 минуту позже, чем предыдущий, начиная с момента открытия смены
# Эта головомойка нужна временно для выгрузки старых заказов, созданных ранее, т.к. в МойСклад дата оформления заказа
# Должна быть позже даты открытия смены. При этом невозможно октрыть смену задним числом. По идее, возможно отправить
# Все заказы с одним значением времени, но дабы избежать возможных проблем сделаем это с зареджкой в 1 минуту
increase_time = timedelta(minutes=1)

# order_date - "виртуальное" время заказа. Время первого заказа считается от времени открытия смены.
order_date = datetime.strptime(retailShift_create_date, "%Y-%m-%d %H:%M:%S.%f")  # Преобразуем строку в ДатаВремя

# TODO Для начала выгрузить только товары со статусом 'delivered', чтобы не получить неоправданную выручку в МойСклад
# TODO далее сверять заказы с учетом статусов и изменять их при необходимости.
for order in ozon_orders['result']:
    order_date += increase_time                # Время заказа = +1 минута к созданию смены и созданию предыдущего заказа
    order_date_export = datetime.strftime(order_date, "%Y-%m-%d %H:%M:%S")  # Строка с датой/временем заказа для МойСкад

    for product in order['products']:
        # TODO В этом цикле нужно сформировать список всех мета-id товаров в заказе, чтобы далее передать его в заказ
        product_id = ozon_moysklad_id_converter(product['offer_id'])    # получаем мета-id МойСклад по Артикулу товара
        print(str(order['order_id']) + ': ' + order_date_export + ', Status: ' + order['status'] + ', Order Name: ' +
              order['order_number'] + ', Артикул: ' + product['offer_id'], 'ID товара: ' + product_id)
# order_date_export = datetime.fromisoformat(order_date[:-1])  # преобразуем в формата даты/времени, убирая конечный Z

# МойСклад не принимает формат ДатаВремя с конечным Z, поэтому убираем его перед отправкой запроса
# Надо иметь ввиду, что в МойСклад нельзя отправит заказ с датой раньше, чем дата открытия смены,
# Как следствие при выгрузке нам практически не пригодится поле с датой оформления заказа из файла выгрузки ОЗОН
# Только если мы будем скриптом по расписанию ежесуточно открывать смену в полночь и в дальнейшем в смену
# на соответствуюущую дату отправлять оформленные заказы
# order_date = ozon_orders['result'][0]['created_at'] # получаем строку с датой/временем первого заказа из списка
# order_date = datetime.fromisoformat(order_date[:-1])     # преобразуем в формата даты/времени, убирая конечный Z
# print('Тип переменной order_date: ' + str(type(order_date)))
# print(order_date)


# utc3 = datetime.time(3, 0, 0)
# orders_data = datetime.strftime("%Y-%m-%d %H:%M:%S", orders_data)


# print(order_data.strftime("%Y-%m-%d %H:%M:%S"))


# filter_ = {'since':date_from, 'status':status, 'to':date_to}
# with_ = {'analytics_data':analytics_data, 'financial_data':financial_data}

# 'Content-Type': 'application/json' - указывать не обязательно,
# если реквест используется с декодером (request.post(json=dataset))
# request_body = {'dir':dir_to, 'filter':filter_, 'limit':limit, 'offset':offset,\
#                    'translit':translit, 'with':with_}
request_body = {}

# response = requests.post(api_domain + api_url + 'retaildemand', headers=headers, json=request_body)
# data = response.json()
# print(response.status_code)

# print(data)
