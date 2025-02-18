import requests

uri = 's3://datascientest-mlops-classif/debug_killian/'

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

print(response.json())