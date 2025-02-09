import requests

uri = 's3://datascientest-mlops-classif/147258c8-c6b8-4440-a7ac-3504e1da68a0/'

endpoint_url = 'http://localhost:9092/etl/ingest'
data_dict = {
    "uri": uri
}
headers = {'Content-Type': 'application/json'}
response = requests.post(
    url=endpoint_url,
    json=data_dict,
    headers=headers
)

#print(response.json())