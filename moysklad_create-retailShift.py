import requests
import json

with open('api-keys/api-keys.json') as f:               # Закрытый от индекса файл с ключами API и командами запросов
    api_params = json.load(f)['api_moysklad']

api_key = api_params['api_key']                                 # Получаем ключ API MoySklad
api_domain = api_params['api_domain']                           # Получаем домен API
api_url = api_params['api_url']                                 # Получаем основной путь для работы с API

api_name_organization = api_params['organisation']['name']      # Имя бъекта, для добавление в URL запроса Организации
api_name_store = api_params['store']['name']                    # Имя бъекта, для добавление в URL запроса Склада
api_name_retailStore = api_params['retailStore']['name']        # Имя бъекта, для добавление в URL запроса Точки продаж
api_name_retailShift = api_params['retailShift']['name']        # Имя бъекта, для добавление в URL запроса Розн. смены

id_organization = api_params['organisation']['id']              # Получаем ID Юр. лица
id_store = api_params['store']['id']                            # Получаем ID Склада
id_retailStore = api_params['retailStore']['id']                # Получаем ID Точки продаж

# Формируем URLы для отправки JSON на сервер
api_com_organisation = api_domain + api_url + api_name_organization         # Команда для работы с Организацией
api_com_store = api_domain + api_url + api_name_store                       # Команда для работы со Складом
api_com_retailStore = api_domain + api_url + api_name_retailStore           # Команда для работы с точкой продаж
api_com_retailShift = api_domain + api_url + api_name_retailShift           # Розничная смена

headers = {'Authorization': 'Basic '+api_key, 'Content-Type': 'application/json'}
request_body = {}

response_organization = requests.get(api_domain + url_command_organization, headers=headers)  # получаем данные юр. лиц
print("Статус запроса Юр.лиц: " + str(response_organization.status_code))

response_store = requests.get(api_domain + url_command_store, headers=headers,
                              params='filter=name=OZON_Khorugvino')                # получаем данные склада в Хоругвино
print("Статус запроса Складов: " + str(response_store.status_code))

response_retailStore = requests.get(api_domain + url_command_retailStore, headers=headers)  # получаем данные Точки продаж
print("Статус запроса Точек продаж: " + str(response_retailStore.status_code))

response_retailShift = requests.get(api_domain + api_com_retailShift, headers=headers)  # получаем данные Точки продаж
print("Статус запроса Розничных смен: " + str(response_retailShift.status_code))

with open('meta/moysklad_ids.json') as f:            # открываем файл, чтобы внести в него мета-данные организации
    ozon_ids = json.load(f)

ozon_ids['accountId'] = response_organization.json()['rows'][0]['accountId']        # получаем значение ID пользователя
ozon_ids['organizationId'] = response_organization.json()['rows'][0]['id']          # получаем значение ID Организации
ozon_ids['storeId'] = response_store.json()['rows'][0]['id']                        # получаем значение ID Склада
ozon_ids['retailStoreId'] = response_retailStore.json()['rows'][0]['id']            # получаем значение ID Точки продаж

response_data = response_retailShift.json()
format_data = json.dumps(response_data, indent=4, ensure_ascii=False)  # красивый вывод в консоль

with open('meta/moysklad_ids.json', 'w') as outfile:
    json.dump(ozon_ids, outfile, indent=4, ensure_ascii=False)
    print(format_data)
    print('\n\n ### Содержимое moysklad_ids.json ###')
    print(json.dumps(ozon_ids, indent=4, ensure_ascii=False))
