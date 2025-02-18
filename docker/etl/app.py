from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from typing import List

from src.data.clean_etl import transform
from src.data.ingest_etl import extract
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

class InputTransformItem(BaseModel):
    name: str
    text: str


class OutputTransformItem(BaseModel):
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
    response_model=List[OutputTransformItem],
    tags=["ETL"])
def api_transform( files: List[InputTransformItem] ):
    try:
        return transform(files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

