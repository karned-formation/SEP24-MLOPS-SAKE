from fastapi import FastAPI
from steps.preprocessing.preprocessing import train

app = FastAPI()

@app.post('/train')
def training():
    return train