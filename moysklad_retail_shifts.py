import requests
import json
from datetime import datetime, timedelta

with open('api-keys/api-keys.json') as f_api:              # Закрытый от индекса файл с ключами API и командами запросов
    api_params = json.load(f_api)['api_moysklad']

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
headers = {'Authorization': api_key}   # Заголовок запроса

# Проверка наличия файла настроект. Если файл отсутствует - создаем его со значением по-умолчанию
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
    # Кроме того создаем и сам файл по-умолчанию
    settings_json = {"days_to_download_orders": 45, "day_start_time": "03:00",
                     "retail_shift_duration": retail_shift_duration}
    with open('settings.json', 'w') as settings_file:
        json.dump(settings_json, settings_file, indent=4, ensure_ascii=False)
    # print("Файл отсутствовал, был создан. Длительность смены равна {}".format(str(increase_time)))


def create_retail_shift():
    # Открываем файл со структурой тела запроса на создание розничной смены, и формируем request_body
    with open('scheme/templates/retailShift_create.json') as f_shift:
        request_body = json.load(f_shift)
    request_body['organization']['meta']['href'] = api_com_organization + '/' + id_organization
    request_body['organization']['meta']['metadataHref'] = api_com_organization + '/metadata'
    request_body['store']['meta']['href'] = api_com_store + '/' + id_store
    request_body['store']['meta']['metadataHref'] = api_com_store + '/metadata'
    request_body['retailStore']['meta']['href'] = api_com_retailStore + '/' + id_retailStore
    request_body['retailStore']['meta']['metadataHref'] = api_com_retailStore + '/metadata'

    print(json.dumps(request_body, indent=4, ensure_ascii=False))

    # Создаем новую смену
    response_retail_shift = requests.post(api_com_retailShift, headers=headers, json=request_body)
    print("Статус запроса на создание смены: " + str(response_retail_shift.status_code))  # Вывод статуса запроса
    retail_shift_id = response_retail_shift.json()['id']  # ID открытой смены
    retail_shift_name = response_retail_shift.json()['name']  # Имя открытой смены
    retail_shift_time_created = response_retail_shift.json()['created']  # Время открытия смены

    # Дебажный вывод в консоль
    # print("\nРозничная смена открыта, даные смены таковы:\n" +
    #       json.dumps(response_retail_shift.json(), indent=4, ensure_ascii=False))
    print('ID открытой смены: ' + retail_shift_id + '\nИмя розничной смены: ' + retail_shift_name +
          '\nСмена открыта в: ' + retail_shift_time_created)


def open_retail_shifts():
    # Получаем список открытых розничных смен
    response_retail_shift = requests.get(api_com_retailShift, headers=headers)
    retail_shifts_list = response_retail_shift.json()['rows']
    print("Статус запроса на создание смены: " + str(response_retail_shift.status_code))  # Вывод статуса запроса
    # print(json.dumps(retail_shifts_list, indent=4, ensure_ascii=False))

    retail_shifts_meta = []                             # Список открытых смен
    for element in retail_shifts_list:                   # Проходим по списку открытых смен из респонса
        # Создаем объект, содержащие мета смены
        retail_shifts_element = {'name': element['name'], 'id': element['id'], 'created': element['created']}

        # Проверяем статус смены. Если смена уже была закрыта - в ответе существует параметр 'closeDate'.
        # Если параметр не задан, значит смена еще открыта.
        if 'closeDate' in element:
            retail_shifts_element['closed'] = element['closeDate']
        else:
            retail_shifts_element['closed'] = 0  # 0 == False, можно заменить на пустую строку ''
            # Если дата закрытия смены отсутствует == 0, значит смена открыта и нужно ее закрыть
            close_retail_shift(retail_shift_id=element['id'], create_date=element['created'])

        # Считаем количество продаж в смене. Если параметр 'operations' не задан, значит продаж не было и их кол-во == 0
        if 'operations' in element:
            retail_shifts_element['sales count'] = len(element['operations'])
        else:
            retail_shifts_element['sales count'] = 0

        retail_shifts_meta.append(retail_shifts_element)                        # Добавляем объект с мета в список смен

    print("\nРозничные смены получены:\n" + json.dumps(retail_shifts_meta, indent=4, ensure_ascii=False))

    with open('data/moysklad_retail_shifts_list.json', 'w') as outfile:
        json.dump({'retailShifts': retail_shifts_meta}, outfile, indent=4, ensure_ascii=False)  # запись данных в файл
        print('\n\n ### Содержимое moysklad_retail_shifts_list.json ###')
        print(json.dumps(retail_shifts_meta, indent=4, ensure_ascii=False))


def close_retail_shift(retail_shift_id, create_date):
    increase_date = datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S.%f")  # получаем дату/время открытия смены из стр
    increase_date += increase_time                                  # прибавляем к дате/времени открытия смены 1 сутки
    close_date = datetime.strftime(increase_date, "%Y-%m-%d %H:%M:%S")      # преобразуем строку в ДатаВремя
    print('Закрываем открытую смену {} с датой {}'.format(retail_shift_id, close_date))

    response_body = {"closeDate": close_date}
    response_retail_shift = requests.put(api_com_retailShift + "/" + retail_shift_id, headers=headers,
                                         json=response_body)
    print("Статус запроса на закрытие смены: " + str(response_retail_shift.status_code))  # Вывод статуса запроса


open_retail_shifts()    # открываем список смен, проверяем есть ли среди них открытые и зарывае их
create_retail_shift()   # создаем новую смену
