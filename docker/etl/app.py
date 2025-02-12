import logging

from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.responses import PlainTextResponse
from typing import List

from src.data.clean_etl import clean_prediction, clean_train
from src.data.ingest_etl import extract, ingest_train
from pydantic import BaseModel

app = FastAPI(
    title="ETL",
    description="API Etract Transform Load.",
    version="1.0.0"
)
Instrumentator().instrument(app).expose(
    app=app,
    endpoint="/metrics"
)

class InputExtractItem(BaseModel):
    name: str
    content: str


class OutputExtractItem(BaseModel):
    name: str
    text: str


@app.post(
    path="/extract",
    response_model=List[OutputExtractItem],
    tags=["ETL"])
def api_extract( files: List[InputExtractItem] ):
    try:
        return extract(files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    path="/transform",
    tags=["ETL"])
def api_transform(  ):
    try:
        clean_prediction("uri")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    path="/etl/ingest/train",
    tags=["ETL : train"])
def ingest():
    try:
        ingest_train()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    path="/etl/clean/train",
    response_class=PlainTextResponse,
    tags=["ETL : train"])
def clean():
    try:
        clean_train()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
