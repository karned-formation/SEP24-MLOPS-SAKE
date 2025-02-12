from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.responses import PlainTextResponse

from src.data.clean_etl import clean_prediction, clean_train
from src.data.ingest_etl import ingest_prediction, ingest_train
from pydantic import BaseModel

app = FastAPI(
    title="ETL",
    description="API Etract Transform Load.",
    version="1.0.0"
)
Instrumentator().instrument(app).expose(
    app=app,
    endpoint="/etl/metrics"
)


class InputExtract(BaseModel):
    uri: str


class InputTransform(BaseModel):
    uri: str


class InputLoad(BaseModel):
    uri: str


class OutputExtract(BaseModel):
    data: str


class OutputTransform(BaseModel):
    data: str


class OutputLoad(BaseModel):
    data: str


@app.post(
    path="/extract",
    response_class=PlainTextResponse,
    tags=["ETL"])
def extract( input_data: InputExtract ):
    try:
        ingest_prediction(input_data.uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    path="/transform",
    response_class=PlainTextResponse,
    tags=["ETL"])
def transform( input_data: InputClean ):
    try:
        clean_prediction(input_data.uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    path="/load",
    response_class=PlainTextResponse,
    tags=["ETL"])
def load( input_data: InputClean ):
    try:
        clean_prediction(input_data.uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    path="/etl/ingest/train",
    response_class=PlainTextResponse,
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
