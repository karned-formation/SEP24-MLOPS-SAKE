from pydantic import BaseModel
from starlette.responses import PlainTextResponse
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.data.clean_text import tokenize_data

app = FastAPI(
    title="Clean",
    description="API Clean text.",
    version="1.0.0"
)
Instrumentator().instrument(app).expose(
    app=app,
    endpoint="/metrics"
)


class InputText(BaseModel):
    text: str



@app.post(
    path="/clean",
    response_class = PlainTextResponse,
    tags=["Clean"]
)
def clean(data: InputText):
    return tokenize_data(data.text)
