import requests
import json

with open('api-keys/api-keys.json') as f:           # файл настроек/api-ключей для работы запросов к серверу
    api_params = json.load(f)['api_moysklad']

# Дальнейшее усложнение для получения ссылки запроса создано для того, чтобы в дальнейшем не пришлось лезть в код\
# при появлении изменений в API. Достаточно будет лишь внести корректировку в код api-keys.json, чтобы все скрипты\
# начали работать корректно.
api_key = api_params['api_key']
url_domain = api_params['url_domain']
url_command_organization = api_params['url_api'] + api_params['organisation']['url_command']    # ID Юр. лица
url_command_store = api_params['url_api'] + api_params['store']['url_command']                  # ID Склада
url_command_retailStore = api_params['url_api'] + api_params['retailStore']['url_command']      # ID Точки продаж

headers = {'Authorization': 'Bearer '+api_key}
request_body = {}


response_organization = requests.get(url_domain+url_command_organization, headers=headers)  # получаем данные юр. лиц
print("Статус запроса Юр.лиц: " + str(response_organization.status_code))

response_store = requests.get(url_domain+url_command_store, headers=headers,
                              params='filter=name=OZON_Khorugvino')                # получаем данные склада в Хоругвино
print("Статус запроса Складов: " + str(response_store.status_code))

response_retailStore = requests.get(url_domain+url_command_retailStore, headers=headers)  # получаем данные Точки продаж
print("Статус запроса Точек продаж: " + str(response_retailStore.status_code))


with open('meta/moysklad_ids.json') as f:            # открываем файл, чтобы внести в него мета-данные организации
    ozon_ids = json.load(f)

ozon_ids['accountId'] = response_organization.json()['rows'][0]['accountId']        # получаем значение ID пользователя
ozon_ids['organizationId'] = response_organization.json()['rows'][0]['id']          # получаем значение ID Организации
ozon_ids['storeId'] = response_store.json()['rows'][0]['id']                        # получаем значение ID Склада
ozon_ids['retailStoreId'] = response_retailStore.json()['rows'][0]['id']            # получаем значение ID Точки продаж

response_data = response_retailStore.json()
format_data = json.dumps(response_data, indent=4, ensure_ascii=False)               # красивый вывод в консоль

with open('meta/moysklad_ids.json', 'w') as outfile:    # Запись в файл ID аккаунта, организации, склада, точки продаж
    json.dump(ozon_ids, outfile, indent=4, ensure_ascii=False)
    # print(format_data)
    # print('\n\n ### Содержимое moysklad_ids.json ###')
    # print(json.dumps(ozon_ids, indent=4, ensure_ascii=False))
