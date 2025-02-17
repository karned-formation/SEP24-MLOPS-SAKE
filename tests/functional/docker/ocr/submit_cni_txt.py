import requests
from src.utils.files import encode_files

def call_endpoint(url, data_dict):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
        url=url,
        json=data_dict,
        headers=headers
    )
    return response

file_path = 'artefacts/cni.jpg'

with open(file_path, 'rb') as file:
    encoded_files = encode_files([file])

data_dict = {
    "file": encoded_files[0]
}

endpoint_url = 'http://localhost:9093/txt/blocks-words'
response = call_endpoint(endpoint_url, data_dict)
print(response.status_code)
print(response.text)


endpoint_url = 'http://localhost:9093/csv/words'
response = call_endpoint(endpoint_url, data_dict)
print(response.status_code)
print(response.text)

endpoint_url = 'http://localhost:9093/json/all'
response = call_endpoint(endpoint_url, data_dict)
print(response.status_code)
print(response.json())