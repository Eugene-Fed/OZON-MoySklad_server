import requests
import json
import datetime
from datetime import datetime, date, time

with open('api-keys/api-keys.json') as f:
    api_params = json.load(f)['api_moysklad']

#client_id = api_params['api_ozon']['client_id']
api_key = api_params['api_key']
url_domain = api_params['url_domain']
#url_command = api_params['url_command']
url_command = '/api/remap/1.2/entity/retaildemand'
meta_href = '/api/remap/1.2/entity/retailshift'

with open('data/data.json') as f:
    orders_data = json.load(f)

orders_date = orders_data['result'][0]['created_at'] #получаем строку с датой временем заказа
orders_date = datetime.fromisoformat(orders_date[:-1]) #преобразуем в формата даты/времени, убирая конечный Z

#utc3 = datetime.time(3, 0, 0)
#orders_data = datetime.strftime("%Y-%m-%d %H:%M:%S", orders_data)

print(type(orders_date))
print(orders_date)
#print(orders_data.strftime("%Y-%m-%d %H:%M:%S"))


#filter_ = {'since':date_from, 'status':status, 'to':date_to}
#with_ = {'analytics_data':analytics_data, 'financial_data':financial_data}

#'Content-Type': 'application/json' - указывать не обязательно, если реквест используется с декодером (request.post(json=dataset))
headers = {'Authorization':'Bearer '+api_key}
#request_body = {'dir':dir_to, 'filter':filter_, 'limit':limit, 'offset':offset,\
#                    'translit':translit, 'with':with_}
request_body = {}

response = requests.post(url_domain+url_command, headers=headers, json=request_body)
data = response.json()

print(response.status_code)

#print(data)

