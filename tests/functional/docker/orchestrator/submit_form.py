import requests
import random
import string

from src.utils.files import encode_files

random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
file_path = 'artefacts/cni.jpg'

with open(file_path, 'rb') as file:
    encoded_files = encode_files([file])

endpoint_url = 'http://localhost:9091/predict'
data_dict = {
    "reference": random_string,
    "files": encoded_files
}
headers = {'Content-Type': 'application/json'}
response = requests.post(
    url=endpoint_url,
    json=data_dict,
    headers=headers
)

print(response.json())