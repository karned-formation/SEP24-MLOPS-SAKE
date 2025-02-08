import requests

uri = 's3://datascientest-mlops-classif/007f9b53-d253-4abf-a6b4-07c5ef6f0d6c/'

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