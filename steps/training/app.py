from fastapi import FastAPI
from train import train

app = FastAPI()

@app.post('/train')
def training():
    return train