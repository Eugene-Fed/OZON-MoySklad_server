import requests
import json

# -*- coding: utf-8 -*-
import sys
#reload(sys)
import locale
sys.setdefaultencoding(locale.getpreferredencoding())


with open('api-keys/api-keys.json') as f:
    templates = json.load(f)

client_id = templates['api_ozon']['client_id']
api_key = templates['api_ozon']['api_key']
url_domain = templates['api_ozon']['url_domain']
url_command = templates['api_ozon']['url_command']

dir_to = 'asc'
date_from = '2021-07-13T00:00:00Z' #Z = UTF+0 для того, чтобы смена открывалась/закрывалась в 3 ночи по МСК
date_to = '2021-09-05T23:59:59Z'
status = 'delivered'
limit = 2
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
data = response.json()
format_data = json.dumps(json.loads(response.content.decode('utf-8')), indent=2)

print(response.status_code)
print(data['result'][0]['order_id'])
print(data['result'][1]['products'][0]['offer_id'])
#print(response.headers)
with open('data/data.json', 'w') as outfile:
    json.dump(data, outfile)
    print("File Updated")
    print(format_data)