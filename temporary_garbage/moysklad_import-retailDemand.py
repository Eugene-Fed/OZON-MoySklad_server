import requests
import json


# TODO УДАЛИТЬ СКРИПТ ЗА НЕНАДОБНОСТЬЮ

with open('api-keys/api-keys.json') as f:           # Закрытый от индекса файл с ключами API и командами запросов
    api_params = json.load(f)['api_moysklad']

# Дальнейшее усложнение для получения ссылки запроса создано для того, чтобы в дальнейшем не пришлось лезть в код\
# при появлении изменений в API. Достаточно будет лишь внести корректировку в код api-keys.json, чтобы все скрипты\
# начали работать корректно.
api_key = api_params['api_key']                                 # Получаем ключ API MoySklad
api_domain = api_params['api_domain']                           # Получаем домен API
api_url = api_params['api_url']                                 # Получаем основной путь для работы с API
api_name_retailDemand = api_params['retailDemand']['name']      # Имя бъекта, для добавление в URL запроса Точки продаж

headers = {'Authorization': 'Bearer '+api_key}
request_body = {}   # Не используется в этом скрипте

# получаем данные Юр.лица / Организации
response_retailDemand = requests.get(api_domain + api_url + api_name_retailDemand, headers=headers,
                                     params='filter=name=65874548-0008')
print("Статус запроса Юр.лиц: " + str(response_retailDemand.status_code))
print(json.dumps(response_retailDemand.json(), indent=2, ensure_ascii=False))

# format_data = json.dumps(response_retailStore.json(), indent=4, ensure_ascii=False)    # красивый вывод в консоль
# print(format_data)

# with open('api-keys/moysklad_ids.json', 'w') as outfile:  # Запись в файл ID аккаунта, организации, склада, точки продаж
#     json.dump(moySklad_ids, outfile, indent=4, ensure_ascii=False)
#     print('\n ### Содержимое moysklad_ids.json ###')
#     print(json.dumps(moySklad_ids, indent=4, ensure_ascii=False))
