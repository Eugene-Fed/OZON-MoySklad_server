import requests
import json

with open('api-keys/api-keys.json') as f:
    api_params = json.load(f)['api_moysklad']

api_key = api_params['api_key']
url_domain = api_params['url_domain']
url_command_organization = '/api/remap/1.2/entity/organization'     # мета-данные организации (юр. лица)
url_command_store = '/api/remap/1.2/entity/store'                   # мета-данные склада
url_command_retailStore = ''                                        # мета-данные точки продаж
url_command_retailShift = ''                                        # мета-данные смены

# filter_ = {'since':date_from, 'status':status, 'to':date_to}
# with_ = {'analytics_data':analytics_data, 'financial_data':financial_data}

headers = {'Authorization': 'Bearer '+api_key}
request_body = {}

response_organization = requests.get(url_domain+url_command_organization, headers=headers)  # получаем данные юр. лиц
response_store = requests.get(url_domain+url_command_store, headers=headers,
                              params='filter=name=OZON_Khorugvino')                # получаем данные склада в Хоругвино

print("Статус запроса Юр.лиц: " + str(response_organization.status_code))
print("Статус запроса Складов: " + str(response_store.status_code))

with open('meta/meta_ozon_input.json') as f:            # открываем файл, чтобы внести в него мета-данные организации
    big_data = json.load(f)

# получаем json из ответа сервера, с полными данными ОРГАНИЗАЦИИ #
response_data = response_organization.json()
big_data['organization']['href'] = response_data['rows'][0]['meta']['href']
big_data['organization']['id'] = response_data['rows'][0]['id']
big_data['organization']['accountId'] = response_data['rows'][0]['accountId']

# получаем json из ответа сервера, с полными данными СКЛАДА
response_data = response_store.json()
format_data = json.dumps(response_data, indent=4, ensure_ascii=False)  # красивый вывод в консоль
big_data['store']['href'] = response_data['rows'][0]['meta']['href']
big_data['store']['id'] = response_data['rows'][0]['id']
big_data['store']['accountId'] = response_data['rows'][0]['accountId']

with open('meta/meta_ozon_input.json', 'w') as outfile:
    json.dump(big_data, outfile, indent=4, ensure_ascii=False)
    print(format_data)
    print('\n\n ### Содержимое meta_ozon_input.json ###')
    print(json.dumps(big_data, indent=4, ensure_ascii=False))
