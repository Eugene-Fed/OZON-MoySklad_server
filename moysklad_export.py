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
# todo в случае, если эти артикулы соответствуют ШК Вайлдберриз
def ozon_moysklad_id_converter(ozon_product_code):
    moysklad_product_code = product_id_table[ozon_product_code]     # сопоставляем код МойСклад с артикулом ОЗОН
    response_product = requests.get(api_domain + api_url + api_name_product, headers=headers,
                                    params='filter=code=' + moysklad_product_code)
    # print("Статус запроса данных Товара: " + str(response_product.status_code))
    return response_product.json()['rows'][0]['id']     # Получаем ID варианта товара


# Метод для определения, была ли это продажа выгружена в МойСклад ранее. Не выгружать, если данные о продаже уже есть.
def moysklad_retail_demand_search(ozon_retail_demand_name):
    response_ozon_retail_demand = requests.get(api_domain + api_url + api_name_retailDemand, headers=headers,
                                         params='filter=name='+ozon_retail_demand_name)
    # print("Статус запроса наличия Продажи: " + str(response_ozon_retail_demand.status_code))
    # print(json.dumps(response_ozon_retail_demand.json(), indent=2, ensure_ascii=False))
    # Если размер параметра /meta/size = 1, значит такое имя продажи в МойСклад уже встречается,
    # в противном случае - это новая продажа. Можно конечно возвращать само значение размера, т.к. 0=False, 1=True,
    # но с дополнительной переменной читаемость кода выше
    is_uploaded = True if response_ozon_retail_demand.json()['meta']['size'] > 0 else False
    return is_uploaded


# TODO 1: Создать класс moysklad_retailShifts-open
# TODO 2: Использовать получение данных о существующих сменах с использования этого класса, вместо данных из файла
with open('data/retailShifts.json') as f:                       # Файл с открытыми сменами МойСклад
    moysklad_retailShifts = json.load(f)

# Получаем дату создания и ID последней существующей смены
# TODO 1 Проверить в каком порядке смены выгружаются в список. Если каждая новая встает в начало списка, а старые
# todo смещаются назад, то необходимо брать в работу индекс [0]. В противном случае - [-1]
# TODO 2 Если список смен пустой - необходимо создать новую смену
retailShift_create_date = moysklad_retailShifts['retailShifts'][0]['created']     # ДатаВремя создания смены в МойСклад
retailShift_create_id = moysklad_retailShifts['retailShifts'][0]['id']            # ID смены в МойСклад
retailShift_close_date = moysklad_retailShifts['retailShifts'][0]['closed']        # Дата закрытия смены.

# если Дата смены == True, т.е. принимает значение - необходимо открыть новую смену, т.к. она уже закрыта
# если Дата закрытия смены == False (фактически == 0), занчит смена еще открыта и можно данные выгружать в нее
if retailShift_close_date:
    # TODO createNewShift
    print("Необходимо создать новую смену")
else:
    # TODO используем отрытую смену
    print("Старая смена еще открыта")

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

# TODO предварительно проверить наличие параметра 'result', который может отсутстовать, если заказов не было
retailDemands_total = len(ozon_orders['result'])        # Общее количество загруженных продаж
retailDemands_count = 0                                 # Количество выгруженных продаж
# TODO Для начала выгрузить только товары со статусом 'delivered', чтобы не получить завышенную выручку в МойСклад
# todo далее сверять заказы с учетом статусов и изменять их при необходимости.
for order in ozon_orders['result']:

    if moysklad_retail_demand_search(order['order_number']):    # проверяем была ли выгрузка этого заказа в МойСклад
        print("Заказ № {} был выгружен ранее".format(order['order_number']))
        continue

    print("Заказ № {} будет выгружен в активную смену".format(order['order_number']))
    with open('data/retailDemand_create.json') as f:  # Файл с шаблоном заказа для выгрузки в МойСклад
        moysklad_retailDemand = json.load(f)
    moysklad_retailDemand['retailShift']['meta']['href'] = api_domain + api_url + api_name_retailShift + '/' +\
                                                           retailShift_create_id

    order_date += increase_time                # Время заказа = +1 минута к созданию смены и созданию предыдущего заказа
    order_date_export = datetime.strftime(order_date, "%Y-%m-%d %H:%M:%S")  # Строка с датой/временем заказа для МойСкад
    moysklad_retailDemand['moment'] = order_date_export                 # Дата и время создания заказа на ОЗОН
    moysklad_retailDemand['name'] = str(order['order_number'])          # Номер заказа - строка
    moysklad_retailDemand['code'] = str(order['order_id'])              # Код заказа - строка

    # product_quantity = 0  # Есть два разных поля quantity, одно в products, другое - в financial_data

    for product in order['products']:   # проходим по циклу список продуктов с основными данными
        # TODO В этом цикле нужно сформировать список всех мета-id товаров в заказе, чтобы далее передать его в заказ
        product_id = ozon_moysklad_id_converter(product['offer_id'])  # получаем id товара МойСклад по Арт. товара ОЗОН

        # Находим общую стоимость заказа как сумму всех тваров в заказе, умноженную на их количество, т.к. ОЗОН
        # не передает ИТОГ отдельным полем - только по артикульно.
        # moysklad_retailDemand['sum'] += float(product['price']) * int(product['quantity'])
        # product_quantity = int(product['quantity'])  # TODO - временный костыль, разобраться с количеством корректнее
        # Вычисляем накладные расходы, чтобы добавить о них инфо для каждого отдельного товара

        # for product in order['financial_data']['products']: # проходим по циклу второй список продуктов с доп. данными
        # total_cost = float(product['commission_amount'])       # приравниваем общим расходам по товару размер комиссии
        # Считаем полную сумму заказа сложением цены всех товаров в заказе
        moysklad_retailDemand['sum'] += float(product['price']) * int(product['quantity'])

        # for item in product['item_services']:
        #     # Добавляем к комиссии прочие расходы, которые передаются ОЗОН с отриц. знач.
        #     total_cost += -float(product['item_services'][item])    # Комиссия с пролажи - не учитывается МойСклад

        moysklad_retailDemand['positions'].append({
            # todo - quantity пофиксить, сейчас берется значение только первого товара в заказе
            # цену товара из ОЗОН умножаем на 100, т.к. судя по всему МойСклад принимает цену товара в коейках
            'quantity': int(product['quantity']), 'price': float(product['price']) * 100, 'assortment': {
                'meta': {"href": api_domain+api_url+api_name_product+'/'+product_id,
                         'type': api_name_product,
                         "mediaType": "application/json"}
            }   # , 'cost': total_cost  # Комиссия с продажи номенклатуры - не учитывается в системе МойСклад
        })

    # TODO 1 Попробовать использовать поле 'payedSum' для того, чтобы учесть комиссию с продажи ОЗОН
    # TODO 2 Можно посчитать total_cost, вычесть ее из 'sum' и записать это значение в параметр 'payedSum'
    moysklad_retailDemand['payedSum'] = moysklad_retailDemand['sum']  # Пока не разобрался для чего поле, поэтому так
    # print(json.dumps(moysklad_retailDemand, indent=2, ensure_ascii=False))

    response_retailDemand = requests.post(api_domain + api_url + api_name_retailDemand, headers=headers,
                                    json=moysklad_retailDemand)
    print("Статус создания Розничной Продажи: " + str(response_retailDemand.status_code))
    # print('Ответ сервера МойСклад:')
    # print(json.dumps(response_retailDemand.json(), indent=2, ensure_ascii=False))
    retailDemands_count += 1    # Если выгрузка прошла успешно - суммируем ее к общему количеству

print('Всего заказов загружено: {}, из них выгружено в МойСклад: {}'.format(retailDemands_total, retailDemands_count))

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
# request_body = {}

# response = requests.post(api_domain + api_url + 'retaildemand', headers=headers, json=request_body)
# data = response.json()
# print(response.status_code)

# print(data)
