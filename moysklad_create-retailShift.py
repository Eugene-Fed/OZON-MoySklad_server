import requests
import json

with open('api-keys/api-keys.json') as f:               # Закрытый от индекса файл с ключами API и командами запросов
    api_params = json.load(f)['api_moysklad']

api_key = api_params['api_key']                                     # Получаем из файла api-ключ moysklad
api_domain = api_params['url_domain']                               # Получаем домен для работы с API
api_command = api_params['url_api']
id_organization = api_params['organisation']['id']                  # Получаем ID Юр. лица
id_store = api_params['store']['id']                                # Получаем ID Склада
id_retailStore = api_params['retailStore']['id']                    # Получаем ID Точки продаж

# Формируем команду для работы с Параметрами
api_com_retailShift = api_params['url_api'] + api_params['retailShift']['url_command']      # Розничная смена

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
