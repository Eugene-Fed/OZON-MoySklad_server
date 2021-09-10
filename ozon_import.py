import requests
import json

with open('api-keys/api-keys.json') as f:
    templates = json.load(f)

client_id = templates['client_id']
api_key = templates['api_key']
url_domain = templates['url_domain']
url_command = templates['url_command']

dir_to = 'asc'
date_from = '2021-08-30T00:00:00+03:00'
date_to = '2021-09-05T23:59:59+03:00'
status = 'delivered'
limit = 5
offset = 0
translit = True
analytics_data = False
financial_data = False

filter_ = {'since':date_from, 'status':status, 'to':date_to}
with_ = {'analytics_data':analytics_data, 'financial_data':financial_data}

headers = {'Client-Id':client_id, 'Api-Key':api_key}
request_body = {'dir':dir_to, 'filter':filter_, 'limit':limit, 'offset':offset,\
                    'translit':translit, 'with':with_}

response = requests.post(url_domain+url_command, headers=headers, json=request_body)
json = response.json()

print(response.status_code)
print(json['result'][0]['order_id'])
print(json['result'][1]['products'][0]['offer_id'])
print(response.headers)
