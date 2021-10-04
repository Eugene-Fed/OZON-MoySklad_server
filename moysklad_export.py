import requests
import json
from datetime import datetime, timedelta, date, time

with open('api-keys/api-keys.json') as f:                       # Получаем параметры для отправки запроса на сервер
    api_params = json.load(f)['api_moysklad']

api_key = api_params['api_key']                                 # Получаем ключ API MoySklad
api_domain = api_params['api_domain']                           # Получаем домен API
api_url = api_params['api_url']                                 # Получаем основной путь для работы с API
api_name_product = api_params['product']['name']                # Имя бъекта, для добавление в URL запроса Товара
api_name_retailShift = api_params['retailShift']['name']        # Имя бъекта, для добавление в URL запроса Розн. смены
api_name_retailDemand = api_params['retailDemand']['name']      # Имя бъекта, для добавление в URL запроса Розн. продажи

headers = {'Authorization': 'Bearer ' + api_key}

# Для сопоставления артикула товара ОЗОН с кодом товара в МойСклад необходимо использовать таблицу соответствий
with open('data/product-id_corr-table.json') as f:
    product_id_table = json.load(f)['ozon-to-moysklad']     # Таблица соответствия артикула ОЗОН с кодом товара МС


# Функция для определения meta-идентификатора товара в МойСклад по его артикулу из ОЗОН
# TODO Использовать файл data/product_id-corr_table.json для того, чтобы заменить Код товара МойСклад на артикулы ОЗОН,
# TODO в случае, если эти артикулы соответствуют ШК Вайлдберриз
def ozon_moysklad_id_converter(ozon_product_code):
    moysklad_product_code = product_id_table[ozon_product_code]     # сопоставляем код МойСклад с артикулом ОЗОН
    response_product = requests.get(api_domain + api_url + api_name_product, headers=headers,
                                    params='filter=code=' + moysklad_product_code)
    print("Статус запроса данных Товара: " + str(response_product.status_code))
    return response_product.json()['rows'][0]['id']     # Получаем ID варианта товара


with open('data/retailShifts.json') as f:                       # Файл с открытыми сменами МойСклад
    moysklad_retailShifts = json.load(f)

retailShift_create_date = moysklad_retailShifts['retailShifts'][0]['created']      # ДатаВремя создания смены в МойСклад
retailShift_create_id = moysklad_retailShifts['retailShifts'][0]['id']             # ID смены в МойСклад

print('Список открытых смен:')
print(json.dumps(moysklad_retailShifts, indent=2, ensure_ascii=False))

with open('data/ozon_orders.json') as f:                        # Открываем файл с заказами ОЗОН за все время
    ozon_orders = json.load(f)

with open('data/retailDemand_create.json') as f:                       # Файл с шаблоном заказа для выгрузки в МойСклад
    moysklad_retailDemand = json.load(f)

moysklad_retailDemand['retailShift']['meta']['href'] = api_domain + api_url + api_name_retailShift + '/' +\
                                                       retailShift_create_id

# Создаем переменную формата ДатаВремя со значением 1 минута для того, чтобы в цикле выгрузки заказов озон
# в смену МойСклад, каждый следующий заказ приходил на 1 минуту позже, чем предыдущий, начиная с момента открытия смены
# Эта головомойка нужна временно для выгрузки старых заказов, созданных ранее, т.к. в МойСклад дата оформления заказа
# Должна быть позже даты открытия смены. При этом невозможно октрыть смену задним числом. По идее, возможно отправить
# Все заказы с одним значением времени, но дабы избежать возможных проблем сделаем это с зареджкой в 1 минуту
increase_time = timedelta(minutes=1)

# order_date - "виртуальное" время заказа. Время первого заказа считается от времени открытия смены.
order_date = datetime.strptime(retailShift_create_date, "%Y-%m-%d %H:%M:%S.%f")  # Преобразуем строку в ДатаВремя

# TODO Для начала выгрузить только товары со статусом 'delivered', чтобы не получить завышенную выручку в МойСклад
# TODO далее сверять заказы с учетом статусов и изменять их при необходимости.
for order in ozon_orders['result']:
    order_date += increase_time                # Время заказа = +1 минута к созданию смены и созданию предыдущего заказа
    order_date_export = datetime.strftime(order_date, "%Y-%m-%d %H:%M:%S")  # Строка с датой/временем заказа для МойСкад
    moysklad_retailDemand['moment'] = order_date_export                 # Дата и время создания заказа на ОЗОН
    moysklad_retailDemand['name'] = str(order['order_number'])          # Номер заказа - строка
    moysklad_retailDemand['code'] = str(order['order_id'])              # Код заказа - строка

    product_quantity = 0  # TODO костыль, т.к. есть два разных поля quantity, одно в products, другое - в financial_data

    for product in order['products']:   # проходим по циклу список продуктов с основными данными
        # TODO В этом цикле нужно сформировать список всех мета-id товаров в заказе, чтобы далее передать его в заказ
        product_id = ozon_moysklad_id_converter(product['offer_id'])  # получаем id товара МойСклад по Арт. товара ОЗОН

        # Находим общую стоимость заказа как сумму всех тваров в заказе, умноженную на их количество, т.к. ОЗОН
        # не передает ИТОГ отдельным полем - только по артикульно.
        moysklad_retailDemand['sum'] += float(product['price']) * int(product['quantity'])
        product_quantity = int(product['quantity'])     # TODO - временный костыль, разобраться с количеством корректнее
        # Вычисляем накладные расходы, чтобы добавить о них инфо для каждого отдельного товара

    for product in order['financial_data']['products']:     # проходим по циклу второй список продуктов с доп. данными
        total_cost = float(product['commission_amount'])       # приравниваем общим расходам по товару размер комиссии
        for key in product['item_services']:
            # Добавляем к комиссии прочие расходы, которые передаются ОЗОН с отриц. знач.
            total_cost += -float(product['item_services'][key])

        moysklad_retailDemand['positions'].append({
            'quantity': product_quantity, 'price': float(product['price']), 'assortment': {  # todo - quantity пофиксить
                'meta': {"href": api_domain+api_url+api_name_product+'/'+product_id,
                         'type': api_name_product,
                         "mediaType": "application/json"}
            }, 'cost': total_cost
        })

    moysklad_retailDemand['payedSum'] = moysklad_retailDemand['sum']  # Пока не разобрался для чего поле, поэтому так
    print(json.dumps(moysklad_retailDemand, indent=2, ensure_ascii=False))

    response_retailDemand = requests.post(api_domain + api_url + api_name_retailDemand, headers=headers,
                                    json=moysklad_retailDemand)
    print("Статус создания Розничной Продажи: " + str(response_retailDemand.status_code))
    print('Ответ сервера МойСклад:')
    print(json.dumps(response_retailDemand.json(), indent=2, ensure_ascii=False))


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
