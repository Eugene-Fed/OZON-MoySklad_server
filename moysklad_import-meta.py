import requests
import json

with open('api-keys/api-keys.json') as f:
    api_params = json.load(f)['api_moysklad']

api_key = api_params['api_key']
url_domain = api_params['url_domain']
url_command_organization = '/api/remap/1.2/entity/organization'     # мета-данные организации (юр. лица)
url_command_store = '/api/remap/1.2/entity/store'                   # мета-данные склада
url_command_retailStore = '/api/remap/1.2/entity/retailstore'       # мета-данные точки продаж
url_command_retailShift = ''                                        # мета-данные смены

# filter_ = {'since':date_from, 'status':status, 'to':date_to}
# with_ = {'analytics_data':analytics_data, 'financial_data':financial_data}

headers = {'Authorization': 'Bearer '+api_key}
request_body = {}

response_organization = requests.get(url_domain+url_command_organization, headers=headers)  # получаем данные юр. лиц
response_store = requests.get(url_domain+url_command_store, headers=headers,
                              params='filter=name=OZON_Khorugvino')                # получаем данные склада в Хоругвино
response_retailStore = requests.get(url_domain+url_command_retailStore, headers=headers)  # получаем данные юр. лиц

print("Статус запроса Юр.лиц: " + str(response_organization.status_code))
print("Статус запроса Складов: " + str(response_store.status_code))
print("Статус запроса Точек продаж: " + str(response_retailStore.status_code))

with open('meta/meta_ozon_input.json') as f:            # открываем файл, чтобы внести в него мета-данные организации
    big_data = json.load(f)

# получаем json из ответа сервера, с полными данными ОРГАНИЗАЦИИ #
response_data = response_organization.json()
big_data['accountId'] = response_data['rows'][0]['accountId']       # получаем значение ID пользователя
big_data['organization']['href'] = response_data['meta']['href']    # получаем URL для апи Организации
big_data['organization']['id'] = response_data['rows'][0]['id']     # получаем значение ID Организации

# получаем json из ответа сервера, с полными данными СКЛАДА
response_data = response_store.json()                                   # ID пользователя уникально для api-ключа
big_data['store']['href'] = response_data['meta']['href']               # получаем URL для апи Склада
big_data['store']['id'] = response_data['rows'][0]['id']                # получаем значение ID Склада

# получаем json из ответа сервера, с полными данными ТОЧЕК ПРОДАЖ
response_data = response_retailStore.json()
format_data = json.dumps(response_data, indent=4, ensure_ascii=False)  # красивый вывод в консоль
big_data['retailStore']['href'] = response_data['meta']['href']         # получаем URL для апи Точки продаж
big_data['retailStore']['id'] = response_data['rows'][0]['id']          # получаем значение ID Точки продаж

with open('meta/meta_ozon_input.json', 'w') as outfile:
    json.dump(big_data, outfile, indent=4, ensure_ascii=False)
    print(format_data)
    print('\n\n ### Содержимое meta_ozon_input.json ###')
    print(json.dumps(big_data, indent=4, ensure_ascii=False))
