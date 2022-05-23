import requests
import json
from datetime import datetime, timedelta

try:
    with open('api-keys/api-keys.json') as f_api:      # Закрытый от индекса файл с ключами API и командами запросов
        api_params = json.load(f_api)['api_moysklad']
except IOError:
    # TODO Прописать подробную инструкцию для получения данных для файла api-keys.json
    print("File 'api-keys.json' IS MISSED. Add this file to folder '/api-keys/'")

api_key = api_params['api_key']                                 # Получаем ключ API MoySklad
api_domain = api_params['api_domain']                           # Получаем домен API
api_url = api_params['api_url']                                 # Получаем основной путь для работы с API

api_name_organization = api_params['organization']['name']      # Имя бъекта, для добавление в URL запроса Организации
api_name_store = api_params['store']['name']                    # Имя бъекта, для добавление в URL запроса Склада
api_name_retailStore = api_params['retailStore']['name']        # Имя бъекта, для добавление в URL запроса Точки продаж
api_name_retailShift = api_params['retailShift']['name']        # Имя бъекта, для добавление в URL запроса Розн. смены

id_organization = api_params['organization']['id']              # Получаем ID Юр. лица
id_store = api_params['store']['id']                            # Получаем ID Склада
id_retailStore = api_params['retailStore']['id']                # Получаем ID Точки продаж

# Формируем URLы для отправки JSON на сервер
api_com_organization = api_domain + api_url + api_name_organization         # Команда для работы с Организацией
api_com_store = api_domain + api_url + api_name_store                       # Команда для работы со Складом
api_com_retailStore = api_domain + api_url + api_name_retailStore           # Команда для работы с точкой продаж
api_com_retailShift = api_domain + api_url + api_name_retailShift           # Розничная смена

# Формируем заголовок запроса для работы с розничными сменами
headers = {'Authorization': api_key}                                        # Заголовок запроса

# Проверка наличия файла настроект. Если файл отсутствует - создаем его со значением по-умолчанию
# TODO создание файла со значениями по-умолчанию можно вынести в отдельный класс aka отделение настроек от кода
try:
    with open('settings.json', 'r') as settings_file:
        # Если файл существует - значение длительности смены берем из него
        increase_time = timedelta(hours=json.load(settings_file)['retail_shift_duration'])
    # print('Файл существует, длительность смены равна {}'.format(str(increase_time)))
except IOError:
    # Если файл отсутствует, то в режиме 'r' - получим исключение.
    # Тогда в качестве длительности смены задаем 24 часа
    retail_shift_duration = 24
    increase_time = timedelta(hours=retail_shift_duration)
    # Кроме того создаем и сам файл по-умолчанию. day_start_time = 00:00:00, так как часовой UTC = 3 часа по МСК
    settings_json = {"days_to_download_orders": 45, "day_start_time": "00:00:00",
                     "retail_shift_duration": retail_shift_duration}
    with open('settings.json', 'w') as settings_file:
        json.dump(settings_json, settings_file, indent=4, ensure_ascii=False)
    # print("Файл отсутствовал, был создан. Длительность смены равна {}".format(str(increase_time)))


# TODO Закрыть все открытые смены. Открыть новую и выгрузиить только ее данные в файл.
def create_retail_shift():
    # В первый раз открываем список всех смен и закрываем все ранее открытые за ненадобностью.
    open_retail_shifts()   # Получаем список смен в МойСклад. Если обнаружены открытые смены - закрыть

    # Открываем файл со структурой тела запроса на создание розничной смены, и формируем request_body
    with open('scheme/templates/retailShift_create.json') as f_shift:
        request_body = json.load(f_shift)
    request_body['organization']['meta']['href'] = api_com_organization + '/' + id_organization
    request_body['organization']['meta']['metadataHref'] = api_com_organization + '/metadata'
    request_body['store']['meta']['href'] = api_com_store + '/' + id_store
    request_body['store']['meta']['metadataHref'] = api_com_store + '/metadata'
    request_body['retailStore']['meta']['href'] = api_com_retailStore + '/' + id_retailStore
    request_body['retailStore']['meta']['metadataHref'] = api_com_retailStore + '/metadata'
    # print(json.dumps(request_body, indent=4, ensure_ascii=False))

    # Создаем новую смену
    response_retail_shift = requests.post(api_com_retailShift, headers=headers, json=request_body)
    print("Create shift request Status: " + str(response_retail_shift.status_code))  # Вывод статуса запроса
    # Во второй раз получаем список смен уже с учетом только что открытой - ее нет необходимости закрывать
    # open_retail_shifts(close_shifts=False)  # Еще раз получаем список всех смен, в этот раз не закрывая открытые

    # Дебажный вывод в консоль
    # retail_shift_id = response_retail_shift.json()['id']  # ID открытой смены
    # retail_shift_name = response_retail_shift.json()['name']  # Имя открытой смены
    # retail_shift_time_created = response_retail_shift.json()['created']  # Время открытия смены
    #
    # print("\nРозничная смена открыта, даные смены таковы:\n" +
    #       json.dumps(response_retail_shift.json(), indent=4, ensure_ascii=False))
    # print('ID открытой смены: ' + retail_shift_id + '\nИмя розничной смены: ' + retail_shift_name +
    #       '\nСмена открыта в: ' + retail_shift_time_created)
    new_retail_shift_json = response_retail_shift.json()
    new_retail_shift_data = {'name': new_retail_shift_json['name'],
                             'id': new_retail_shift_json['id'],
                             'created': new_retail_shift_json['created']}
    export_retail_shifts(new_retail_shift_data)


def open_retail_shifts(close_shifts=True):     # Если True - запускаем команду на закрытие открытых смен, False - нет
    # Получаем список открытых розничных смен
    response_retail_shift = requests.get(api_com_retailShift, headers=headers)
    retail_shifts_list = response_retail_shift.json()['rows']
    print("MoySklad shift list Request Status: " + str(response_retail_shift.status_code))  # Вывод статуса запроса
    # print(json.dumps(retail_shifts_list, indent=4, ensure_ascii=False))

    if len(retail_shifts_list) == 0:    # Если в МойСклад нет открытых смен - возвращаемся в функцию создания смены
        return

    # retail_shifts_meta = []  # Список открытых смен

    for element in retail_shifts_list:                   # Проходим по списку открытых смен из респонса
        # Создаем объект, содержащие мета смены
        close_retail_shift(retail_shift_id=element['id'], create_date=element['created'])
        # TODO Нам больше без надобности собирать данные всех смен. В цикле только закрыть смены, остальное убрать
        # retail_shifts_element = {'name': element['name'], 'id': element['id'], 'created': element['created']}

        # Считаем количество продаж в смене. Если параметр 'operations' не задан, значит продаж не было и их кол-во == 0
        # if 'operations' in element:
        #     retail_shifts_element['sales count'] = len(element['operations'])
        # else:
        #     retail_shifts_element['sales count'] = 0
        #
        # # Проверяем статус смены. Если смена уже была закрыта - в ответе существует параметр 'closeDate'.
        # # Если параметр не задан, значит смена еще открыта.
        # if 'closeDate' in element:
        #     retail_shifts_element['closed'] = element['closeDate']
        # else:
        #     # retail_shifts_element['closed'] = 0  # 0 == False, можно заменить на пустую строку ''
        #     # Если дата закрытия смены отсутствует == 0, значит смена открыта и нужно ее закрыть
        #     if close_shifts:
        #         # Если нужно закрывать открытые смены - то закрываем и присваиваем смене дату закрытия
        #         # retail_shifts_element['closed'] = close_retail_shift(retail_shift_id=element['id'],
        #         #                                                      create_date=element['created'])
        #         close_retail_shift(retail_shift_id=element['id'], create_date=element['created'])
        #     else:
        #         retail_shifts_element['closed'] = 0  # 0 == False, можно заменить на пустую строку ''

        # retail_shifts_meta.append(retail_shifts_element)                      # Добавляем объект с мета в список смен

    # if not close_shifts:    # Выгружать список смен в файл только если запускаем эту функцию во вторй "чистовой" раз.
    #     export_retail_shifts(retail_shifts=retail_shifts_meta)

    # print("\nРозничные смены получены:\n" + json.dumps(retail_shifts_meta, indent=4, ensure_ascii=False))

    # with open('data/moysklad_retail_shift.json', 'w') as outfile:
    #     json.dump({'retailShifts': retail_shifts_meta}, outfile, indent=4, ensure_ascii=False)  # запись данных в файл
    #     print('\n\n ### Содержимое moysklad_retail_shift.json ###')
    #     print(json.dumps(retail_shifts_meta, indent=4, ensure_ascii=False))


def close_retail_shift(retail_shift_id, create_date):
    increase_date = datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S.%f")  # из строки в Дата/Время
    increase_date += increase_time  # прибавляем к дате/времени создания смены длит. смены и получаем дату закрытия
    close_date = datetime.strftime(increase_date, "%Y-%m-%d %H:%M:%S")      # из Дата/Время в строку
    print('Закрываем открытую смену {} с датой {}'.format(retail_shift_id, close_date))

    response_body = {"closeDate": close_date}
    response_retail_shift = requests.put(api_com_retailShift + "/" + retail_shift_id, headers=headers,
                                         json=response_body)
    print("Статус запроса на закрытие смены: " + str(response_retail_shift.status_code))  # Вывод статуса запроса
    # TODO по идее возврат даты закрытия уже без надобности - убрать
    # return close_date   # возвращаем строковую дату закрытия смены


def export_retail_shifts(retail_shifts):
    with open('data/moysklad_retail_shift.json', 'w') as outfile:
        json.dump(retail_shifts, outfile, indent=4, ensure_ascii=False)  # запись данных в файл
        # print('\n\n ### Содержимое moysklad_retail_shift.json ###')
        # print(json.dumps(retail_shifts, indent=4, ensure_ascii=False))


# open_retail_shifts()    # открываем список смен, проверяем есть ли среди них открытые и зарывае их
create_retail_shift()   # создаем новую смену
