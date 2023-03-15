# -*- coding: UTF-8 -*-

import requests
import json
import sys
import exception_handler as ex
from datetime import datetime, timedelta, date, time

try:
    with open('api-keys/api-keys.json') as f:                       # Получаем параметры для отправки запроса на сервер
        api_params = json.load(f)['api_moysklad']
except IOError:
    print('File "api-keys/api-keys.json" is MISSING.')
    wait = input("PRESS ENTER TO EXIT.")
    # raise SystemExit(1)
    sys.exit(1)  # TODO найти правильный код выхода с ошибкой, вместо стандартного '0'
except Exception as e:
    ex.unexpected(e)

api_key = api_params['api_key']                                # Получаем ключ API MoySklad
api_domain = api_params['api_domain']                          # Получаем домен API
api_url = api_params['api_url']                                # Получаем основной путь для работы с API
api_name_product = api_params['product']['name']               # Имя объекта, для добавления в URL запроса Товара
api_name_retailShift = api_params['retailShift']['name']       # Имя объекта, для добавления в URL запроса Розн. смены
api_name_retailDemand = api_params['retailDemand']['name']     # Имя объекта, для добавления в URL запроса Розн. продажи

headers = {'Authorization': 'Bearer ' + api_key}

# Для сопоставления артикула товара ОЗОН с кодом товара в МойСклад необходимо использовать таблицу соответствий
with open('data/product-id_corr-table.json') as f:
    try:
        product_id_table = json.load(f)['ozon-to-moysklad']     # Таблица соответствия артикула ОЗОН с кодом товара МС
    except Exception as e:
        print(e)
        wait = input('\nОшибка СИНТАКСИСА в таблице "data/product_id-corr_table.json". Невозможно прочитать JSON'
                     '\nPress ENTER to Exit.')
        sys.exit(1)  # TODO найти правильный код выхода с ошибкой, вместо стандартного '0'


# Функция для определения meta-идентификатора товара в МойСклад по его артикулу из ОЗОН
# TODO Использовать файл data/product_id-corr_table.json для того, чтобы заменить Код товара МойСклад на артикулы ОЗОН,
#   в случае, если эти артикулы соответствуют ШК Вайлдберриз
def ozon_moysklad_id_converter(ozon_product_code):
    try:
        print("Searching for OZON Product code {}".format(ozon_product_code))
        moysklad_product_code = product_id_table[ozon_product_code]     # сопоставляем код МойСклад с артикулом ОЗОН
        print("MoySklad Product code is: {}".format(moysklad_product_code))
    except Exception as e:
        print(e)
        print('\nОшибка в таблице "data/product_id-corr_table.json". Отсутствует необходимый ID OZON')
        wait = input("PRESS ENTER TO EXIT.")
        sys.exit(1)

    try:
        print('MoySklad product: Start get request for: {}'.format(moysklad_product_code))
        response_product = requests.get(api_domain + api_url + api_name_product, headers=headers,
                                    params='filter=code=' + moysklad_product_code)
        if response_product.json()['rows'] == []:   # если у товара нет вариантов размера или цвета
            return moysklad_product_code            # тогда возвращаем ID самого товара
        else:
            return response_product.json()['rows'][0]['id']  # иначе возвращаем ID соответствующего варианта товара
    except IndexError as e:
        print("Товар не имеет Вариантов/Торговых предложений. ")
        wait = input("PRESS ENTER TO EXIT.")
        sys.exit(1)
    except Exception as e:
        print(response_product.json())
        ex.unexpected(e)


# Метод для определения, была ли это продажа выгружена в МойСклад ранее. Не выгружать, если данные о продаже уже есть.
def moysklad_retail_demand_search(ozon_retail_demand_name: str):
    """
    :param ozon_retail_demand_name: str - идентификатор продажи в ОЗОН
    :return: Bool
    В ответе Склада мы проверяем параметр /meta/size. Если он = 1, значит такое имя продажи в МойСклад уже встречается,
    в противном случае - это новая продажа. Можно конечно возвращать само значение размера, т.к. 0 == False, 1 == True,
    но с дополнительной переменной читаемость кода выше
    """
    is_uploaded = True
    try:
        print('MoySklad retail search: Start request.')
        response_ozon_retail_demand = requests.get(api_domain + api_url + api_name_retailDemand, headers=headers,
                                             params='filter=name='+ozon_retail_demand_name)
        is_uploaded = True if response_ozon_retail_demand.json()['meta']['size'] > 0 else False
    except Exception as e:
        # Если получаем ошибку сети во время попытки найти заказ на Моем Складе - тогда просто его пропускаем
        print("\nThe request to MySklad to search for a sale by ID returned with an error.")
        print(e)                              # Выводим подробности ошибки

    # print("Статус запроса наличия Продажи: " + str(response_ozon_retail_demand.status_code))
    # print(json.dumps(response_ozon_retail_demand.json(), indent=2, ensure_ascii=False))

    return is_uploaded


# TODO 1: Создать класс moysklad_retailShifts-open
# TODO 2: Использовать получение данных о существующих сменах с использования этого класса, вместо данных из файла
try:
    with open('data/moysklad_retail_shift.json') as f:                       # Файл с открытыми сменами МойСклад
        moysklad_retailShifts = json.load(f)
except IOError:
    print('File "data/moysklad_retail_shift.json" is MISSING.')
    wait = input("PRESS ENTER TO EXIT.")
    sys.exit(1)  # TODO найти правильный код выхода с ошибкой, вместо стандартного '0'
except Exception as e:
    ex.unexpected(e)

# Получаем дату создания и ID последней существующей смены
# TODO 1 Проверить в каком порядке смены выгружаются в список. Если каждая новая встает в начало списка, а старые
# todo смещаются назад, то необходимо брать в работу индекс [0]. В противном случае - [-1]
# TODO 2 Если список смен пустой - необходимо создать новую смену
# retailShift_create_date = moysklad_retailShifts['retailShifts'][0]['created']    # ДатаВремя создания смены в МойСклад
# retailShift_create_id = moysklad_retailShifts['retailShifts'][0]['id']           # ID смены в МойСклад
# retailShift_close_date = moysklad_retailShifts['retailShifts'][0]['closed']      # Дата закрытия смены.
retailShift_create_date = moysklad_retailShifts['created']     # ДатаВремя создания смены в МойСклад
retailShift_create_id = moysklad_retailShifts['id']            # ID смены в МойСклад

# если Дата смены == True, т.е. принимает значение - необходимо открыть новую смену, т.к. она уже закрыта
# если Дата закрытия смены == False (фактически == 0), значит смена еще открыта и можно данные выгружать в нее
# if retailShift_close_date:
#     # TODO moysklad_retail_shifts.create()
#     print("Необходимо создать новую смену")
# else:
#     # TODO moysklad_retail_shifts.open()
#     print("Старая смена еще открыта, выгружаем в нее.")
# в данные момент смены закрываются и открываются полностью под управлением скрипта moysklad_retail_shifts.py.
# возможно этого и достаточно

# print('Retail shifts list:')
# print(json.dumps(moysklad_retailShifts, indent=2, ensure_ascii=False))

try:
    with open('data/ozon_orders.json') as f:                        # Открываем файл с заказами ОЗОН за все время
        ozon_orders = json.load(f)
except IOError:
    print('File "data/ozon_orders.json" is MISSING.')
    wait = input("PRESS ENTER TO EXIT.")
    sys.exit(1)  # TODO найти правильный код выхода с ошибкой, вместо стандартного '0'
except Exception as e:
    ex.unexpected(e)

# Создаем переменную формата ДатаВремя со значением 1 минута для того, чтобы в цикле выгрузки заказов озон
# в смену МойСклад, каждый следующий заказ приходил на 1 минуту позже, чем предыдущий, начиная с момента открытия смены
# Эта головомойка нужна временно для выгрузки старых заказов, созданных ранее, т.к. в МойСклад дата оформления заказа
# Должна быть позже даты открытия смены. При этом невозможно открыть смену задним числом. По идее, возможно отправить
# Все заказы с одним значением времени, но дабы избежать возможных проблем сделаем это с задержкой в 1 минуту
increase_time = timedelta(minutes=1)

# order_date - "виртуальное" время заказа. Время первого заказа считается от времени открытия смены.
order_date = datetime.strptime(retailShift_create_date, "%Y-%m-%d %H:%M:%S.%f")  # Преобразуем строку в ДатаВремя

# TODO предварительно проверить наличие параметра 'result', который может отсутствовать, если заказов не было
retailDemands_total = len(ozon_orders['result'])        # Общее количество загруженных продаж
retailDemands_count = 0                                 # Количество выгруженных продаж
# TODO Для начала выгрузить только товары со статусом 'delivered', чтобы не получить завышенную выручку в МойСклад
#   Далее сверять заказы с учетом статусов и изменять их при необходимости.
for order in ozon_orders['result']:

    if moysklad_retail_demand_search(order['order_number']):    # проверяем была ли выгрузка этого заказа в МойСклад
        print("Order # {} has been uploaded before".format(order['order_number']))
        continue

    print("Order # {} will be uploaded on the active shift".format(order['order_number']))
    try:
        with open('scheme/templates/retailDemand_create.json') as f:  # Файл с шаблоном заказа для выгрузки в МойСклад
            moysklad_retailDemand = json.load(f)
    except IOError:
        print('File "scheme/templates/retailDemand_create.json" is MISSING.')
        wait = input("PRESS ENTER TO EXIT.")
        sys.exit(1)  # TODO найти правильный код выхода с ошибкой, вместо стандартного '0'
    except Exception as e:
        ex.unexpected(e)
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

        # Находим общую стоимость заказа как сумму всех товаров в заказе, умноженную на их количество, т.к. ОЗОН
        # не передает ИТОГ отдельным полем - только по артикульно.
        # moysklad_retailDemand['sum'] += float(product['price']) * int(product['quantity'])
        # product_quantity = int(product['quantity'])  # TODO - временный костыль, разобраться с количеством корректнее
        # Вычисляем накладные расходы, чтобы добавить о них инфо для каждого отдельного товара

        # for product in order['financial_data']['products']: # проходим по циклу второй список продуктов с доп. данными
        # total_cost = float(product['commission_amount'])       # приравниваем общим расходам по товару размер комиссии
        # Считаем полную сумму заказа сложением цены всех товаров в заказе
        # TODO выяснить, не нужно ли умножать цену товара на 100, как это сделано при подсчете стоимости ниже
        moysklad_retailDemand['sum'] += float(product['price']) * int(product['quantity'])

        # for item in product['item_services']:
        #     # Добавляем к комиссии прочие расходы, которые передаются ОЗОН с отриц. знач.
        #     total_cost += -float(product['item_services'][item])    # Комиссия с пролажи - не учитывается МойСклад

        moysklad_retailDemand['positions'].append({
            # TODO - quantity пофиксить, сейчас берется значение только первого товара в заказе
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

    try:
        response_retailDemand = requests.post(api_domain + api_url + api_name_retailDemand, headers=headers,
                                        json=moysklad_retailDemand)
    except Exception as e:
        ex.unexpected(e)
    # print('Ответ сервера МойСклад:')
    # print(json.dumps(response_retailDemand.json(), indent=2, ensure_ascii=False))
    retailDemands_count += 1    # Если выгрузка прошла успешно - суммируем ее к общему количеству

print('Total orders loaded: {}, of which uploaded to MySklad: {}'.format(retailDemands_total, retailDemands_count))
# wait = input("PRESS ENTER TO CONTINUE.")


def export_orders():
    pass


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

if __name__ == "__main__":
    export_orders()   # создаем новую смену
else:
    pass
