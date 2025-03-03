import requests
import random
import string

from src.utils.files import encode_files

random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJQOVpLWnkyX2M3Sjh1aTJBcXRnTGk2NTNOTWVQcDBYbjg4Q1pHNjRjLVlnIn0.eyJleHAiOjE3NDA0MDcxODAsImlhdCI6MTc0MDQwNTY4MCwianRpIjoiNDY5NWU1NzAtMTBhZS00ZDZlLWFmNmUtYjhmZjMyMmE1MmQ4IiwiaXNzIjoiaHR0cHM6Ly9pYW0ua2FybmVkLmJ6aC9yZWFsbXMvS2FybmVkIiwiYXVkIjpbImthcm5lZCIsImFjY291bnQiXSwic3ViIjoiYzY2ZjM2NzEtN2U2NC00MDE3LWIwZTEtZTg0OGZjZWY1ZGRiIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoia2FybmVkIiwic2lkIjoiM2Y2NGUxNmYtM2M5OS00NzY4LTkyOGQtYjg1NGIwOWNiMGY5IiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL3Nha2Uua2FybmVkLmJ6aCIsImh0dHA6Ly9sb2NhbGhvc3Q6ODUwMSIsImh0dHA6Ly9sb2NhbGhvc3QiLCJodHRwOi8vbG9jYWxob3N0OjgwMDAiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iLCJkZWZhdWx0LXJvbGVzLWthcm5lZCJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoicHJvZmlsZSBlbWFpbCIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJuYW1lIjoidG90byBsYWJvdXJkZSIsInByZWZlcnJlZF91c2VybmFtZSI6InRvdG8iLCJnaXZlbl9uYW1lIjoidG90byIsImZhbWlseV9uYW1lIjoibGFib3VyZGUiLCJlbWFpbCI6InRvdG9AZXhhbXBsZS5jb20ifQ.S9purDio7i3LIq5ksk45mMWkJbyKVBxVr-k-aikDbFxUcyuvdGiIr3dGmZNtUQlkiR0E72oKuk75as8qFfltW_ZiCL38G3JbgP_2JyNi3sxAm6woSoGkjL1vlo6ZFeQulE-X_iTkU3PP9ksnEccdBaiu4LexzcKfW8rOjr7RieHDAJ8Gd71ZLzCUeAIoQqYbtyc0MZlmE_WcCDHkHsyMJa39yz9rKRDCTKWtWswnALrE3ROmJUYnFNkPTWJo3mBSVP6s77GpX639BRX42lo_4H-uj60C6VtULyJod5wPzl5VIpjD-IHpys3vtTiCuSpawCnxINghBW4BRErvXwk2Mw"

"""
file1 = open('artefacts/cni.jpg', 'rb')
file2 = open('artefacts/cni2.jpg', 'rb')
encoded_files = encode_files([file1, file2])
"""

file1 = open('artefacts/cni.jpg', 'rb')
encoded_files = encode_files([file1])
names = ['cni.jpg']
datas = []
for i in range(len(encoded_files)):
    datas.append({
        "name": names[i],
        "content": encoded_files[i]
    })

url = 'http://localhost:9091/predict'
data_dict = {
    "reference": random_string,
    "files": datas
}
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
}
try:
    response = requests.post(
        url=url,
        json=data_dict,
        headers=headers
    )
    print(response.json())
except Exception as e:
    print(e)
    print("Error in request")