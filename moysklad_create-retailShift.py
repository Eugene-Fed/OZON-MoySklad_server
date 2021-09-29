import requests
import json

# ЭТО ПОЛНАЯ КОПИПАСТА MOYSKLAD_IMPORT-ID!!!!! ИЗМЕНИТЬ!

with open('api-keys/api-keys.json') as f:
    api_params = json.load(f)['api_moysklad']

api_key = api_params['api_key']
url_domain = api_params['url_domain']
url_command_organization = '/api/remap/1.2/entity/organization'     # мета-данные организации (юр. лица)
url_command_store = '/api/remap/1.2/entity/store'                   # мета-данные склада
url_command_retailStore = '/api/remap/1.2/entity/retailstore'       # мета-данные точки продаж
url_command_retailShift = '/api/remap/1.2/entity/retailshift/'      # мета-данные смены

# filter_ = {'since':date_from, 'status':status, 'to':date_to}
# with_ = {'analytics_data':analytics_data, 'financial_data':financial_data}

headers = {'Authorization': 'Bearer '+api_key}
request_body = {}

response_organization = requests.get(url_domain+url_command_organization, headers=headers)  # получаем данные юр. лиц
print("Статус запроса Юр.лиц: " + str(response_organization.status_code))

response_store = requests.get(url_domain+url_command_store, headers=headers,
                              params='filter=name=OZON_Khorugvino')                # получаем данные склада в Хоругвино
print("Статус запроса Складов: " + str(response_store.status_code))

response_retailStore = requests.get(url_domain+url_command_retailStore, headers=headers)  # получаем данные Точки продаж
print("Статус запроса Точек продаж: " + str(response_retailStore.status_code))

response_retailShift = requests.get(url_domain+url_command_retailShift, headers=headers)  # получаем данные Точки продаж
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
