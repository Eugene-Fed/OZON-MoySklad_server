import requests
import json

with open('api-keys/api-keys.json') as f:               # Закрытый от индекса файл с ключами API и командами запросов
    api_params = json.load(f)['api_moysklad']

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

# Формируем заголовок и тело запроса на создание розничной смены
# headers = {'Authorization': 'Basic '+api_key, 'Content-Type': 'application/json'}   # Заголовок запроса
headers = {'Authorization': api_key, 'Content-Type': 'application/json'}   # Заголовок запроса

# Тело запроса
with open('data/retailShift_create.json') as f:           # Файл со структурой тела запроса на создание розничной смены
    request_body = json.load(f)
request_body['organization']['meta']['href'] = api_com_organization + '/' + id_organization
request_body['organization']['meta']['metadataHref'] = api_com_organization + '/metadata'
request_body['store']['meta']['href'] = api_com_store + '/' + id_store
request_body['store']['meta']['metadataHref'] = api_com_store + '/metadata'
request_body['retailStore']['meta']['href'] = api_com_retailStore + '/' + id_retailStore
request_body['retailStore']['meta']['metadataHref'] = api_com_retailStore + '/metadata'

print(json.dumps(request_body, indent=4, ensure_ascii=False))

# Открываем смену
response_retailShift = requests.post(api_com_retailShift, headers=headers, json=request_body)
print("Статус запроса на создание смены: " + str(response_retailShift.status_code))  # Вывод статуса запроса
retailShift_ID = response_retailShift.json()['id']                      # ID открытой смены
retailShift_name = response_retailShift.json()['name']                  # Имя открытой смены
retailShift_time_created = response_retailShift.json()['created']         # Время открытия смены

# Дебажный вывод в консоль
print("\nРозничная смена открыта, даные смены таковы:\n" +
      json.dumps(response_retailShift.json(), indent=4, ensure_ascii=False))
print('ID открытой смены: ' + retailShift_ID + '\nИмя розничной смены: ' + retailShift_name +
      '\nСмена открыта в: ' + retailShift_time_created)

