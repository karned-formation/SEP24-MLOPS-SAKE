import logging
from typing import List
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

from src.orchestrator.orchestrator import treat

app = FastAPI(
    title="Predict API (frontend)",
    description="API de prédiction de classe d'un ou plusieurs documents.",
    version="1.0.0"
)
Instrumentator().instrument(app).expose(
    app=app,
    endpoint="/metrics"
)


class PredictionRequest(BaseModel):
    files: List[str]
    reference: str


class PredictionResult(BaseModel):
    uuid: str
    prediction: dict


@app.post(
    path="/predict",
    response_model=PredictionResult,
    tags=["Prediction"])
async def upload_images( request: PredictionRequest ):
    reference = request.reference

    uuid, prediction = treat(request.files)

    return {
        "message": "Files saved successfully",
        "reference": reference,
        "uuid": uuid,
        "prediction": prediction
    }
