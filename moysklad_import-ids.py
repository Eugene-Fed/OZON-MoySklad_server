import requests
import json

with open('api-keys/api-keys.json') as f:           # Закрытый от индекса файл с ключами API и командами запросов
    api_params = json.load(f)['api_moysklad']

# Дальнейшее усложнение для получения ссылки запроса создано для того, чтобы в дальнейшем не пришлось лезть в код\
# при появлении изменений в API. Достаточно будет лишь внести корректировку в код f_api-keys.json, чтобы все скрипты\
# начали работать корректно.
api_key = api_params['api_key']                                 # Получаем ключ API MoySklad
api_domain = api_params['api_domain']                           # Получаем домен API
api_url = api_params['api_url']                                 # Получаем основной путь для работы с API
api_name_organization = api_params['organization']['name']      # Имя бъекта, для добавление в URL запроса Организации
api_name_store = api_params['store']['name']                    # Имя бъекта, для добавление в URL запроса Склада
api_name_retailStore = api_params['retailStore']['name']        # Имя бъекта, для добавление в URL запроса Точки продаж

headers = {'Authorization': 'Bearer '+api_key}
request_body = {}   # Не используется в этом скрипте

# получаем данные Юр.лица / Организации
response_organization = requests.get(api_domain + api_url + api_name_organization, headers=headers)
print("Статус запроса Юр.лиц: " + str(response_organization.status_code))

# получаем данные склада ОЗОН в Хоругвино
response_store = requests.get(api_domain + api_url + api_name_store, headers=headers,
                              params='filter=name=ozon_khorugvino')
print("Статус запроса складов: " + str(response_store.status_code))

# получаем данные точки продаж
response_retailStore = requests.get(api_domain + api_url + api_name_retailStore, headers=headers)
print("Статус запроса точек продаж: " + str(response_retailStore.status_code))

with open('api-keys/moysklad_ids.json') as f:            # получаем файл, чтобы внести в него все полученные мета-данные
    moySklad_ids = json.load(f)
# TODO - Добавить проверку на пустой файл. Если данных нет, то забирать их из файла /scheme/~f_api-keys/moysklad_ids.json


moySklad_ids['accountId'] = response_organization.json()['rows'][0]['accountId']    # получаем значение ID пользователя
moySklad_ids['organizationId'] = response_organization.json()['rows'][0]['id']      # получаем значение ID Организации
moySklad_ids['storeId'] = response_store.json()['rows'][0]['id']                    # получаем значение ID Склада
moySklad_ids['retailStoreId'] = response_retailStore.json()['rows'][0]['id']        # получаем значение ID Точки продаж

# format_data = json.dumps(response_retailStore.json(), indent=4, ensure_ascii=False)    # красивый вывод в консоль
# print(format_data)

with open('api-keys/moysklad_ids.json', 'w') as outfile:  # Запись в файл ID аккаунта, организации, склада, точки продаж
    json.dump(moySklad_ids, outfile, indent=4, ensure_ascii=False)
    print('\n ### Содержимое moysklad_ids.json ###')
    print(json.dumps(moySklad_ids, indent=4, ensure_ascii=False))
