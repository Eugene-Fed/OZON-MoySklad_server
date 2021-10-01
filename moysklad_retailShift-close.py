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
api_com_retailShift = api_domain + api_url + api_name_retailShift           # Розничная смена

# Формируем заголовок и тело запроса на создание розничной смены
# headers = {'Authorization': 'Basic '+api_key, 'Content-Type': 'application/json'}   # Заголовок запроса
headers = {'Authorization': api_key}   # Заголовок запроса

# Получаем список открытых розничных смен
response_retailShift = requests.get(api_com_retailShift, headers=headers)
retailShifts_list = response_retailShift.json()['rows']
print("Статус запроса на создание смены: " + str(response_retailShift.status_code))  # Вывод статуса запроса

retailShifts_meta = []                             # Список открытых смен
for element in retailShifts_list:                   # Проходим по списку открытых смен из респонса
    # print('Название смены: ' + element['name'])
    # print('ID Смены: ' + element['id'])
    retailShifts_element = {'name': element['name'], 'id': element['id']}   # Создаем объект, содержащие мета смены
    retailShifts_meta.append(retailShifts_element)                          # Добавляем объект с мета в список смен

# print("\nРозничные смены получены:\n" + json.dumps(response_retailShift.json(), indent=4, ensure_ascii=False))
with open('data/retailShifts.json', 'w') as outfile:
    json.dump({'retailShifts': retailShifts_meta}, outfile, indent=4, ensure_ascii=False) # запись данных смен в файл
    print('\n\n ### Содержимое retailShifts.json ###')
    print(json.dumps(retailShifts_meta, indent=4, ensure_ascii=False))
