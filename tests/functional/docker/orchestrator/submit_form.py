import requests
import random
import string

from src.utils.files import encode_files

random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

"""
file1 = open('artefacts/cni.jpg', 'rb')
file2 = open('artefacts/cni2.jpg', 'rb')
encoded_files = encode_files([file1, file2])
"""

file1 = open('artefacts/cni.jpg', 'rb')
encoded_files = encode_files([file1])

url = 'http://localhost:9091/predict'
data_dict = {
    "reference": random_string,
    "files": encoded_files
}
headers = {'Content-Type': 'application/json'}
response = requests.post(
    url=url,
    json=data_dict,
    headers=headers
)

#print(response.json())