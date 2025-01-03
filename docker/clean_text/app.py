from starlette.responses import PlainTextResponse
from fastapi import FastAPI

from src.data.clean_text import tokenize_data

app = FastAPI()

@app.post("/clean", response_class = PlainTextResponse)
def clean(text: str):
    return tokenize_data(text)
