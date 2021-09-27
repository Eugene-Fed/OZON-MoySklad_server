import requests
import json

with open('api-keys/api-keys.json') as f:
    api_params = json.load(f)['api_moysklad']

api_key = api_params['api_key']
url_domain = api_params['url_domain']
url_command = '/api/remap/1.2/entity/organization'

# filter_ = {'since':date_from, 'status':status, 'to':date_to}
# with_ = {'analytics_data':analytics_data, 'financial_data':financial_data}

headers = {'Authorization': 'Bearer '+api_key}
request_body = {}

response_organization = requests.get(url_domain+'/api/remap/1.2/entity/organization', headers=headers)
print("Статус запроса Юр.лиц: " + str(response_organization.status_code))

response_data = response_organization.json()
format_data = json.dumps(response_data['rows'][0], indent=4)  # красивый вывод в консоль

with open('meta/meta_ozon_input.json') as f:
    big_data = json.load(f)
# big_data['organization']['href'] = response_data['rows'][0]['meta']['href']
# big_data['organization']['id'] = response_data['rows']['id']
# big_data['organization']['accountId'] = response_data['rows']['accountId']

# 'rows' --> 'meta' --> 'href'
# 'rows' --> 'id'
# 'rows' --> 'accountId'

with open('meta/meta_ozon_input.json', 'w') as outfile:
    json.dump(big_data, outfile)
    print(format_data)
    #print(big_data)
