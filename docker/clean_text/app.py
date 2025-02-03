from starlette.responses import PlainTextResponse
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.data.clean_text import tokenize_data

app = FastAPI()

Instrumentator().instrument(app).expose(app)

@app.post("/clean", response_class = PlainTextResponse)
def clean(text: str):
    return tokenize_data(text)
