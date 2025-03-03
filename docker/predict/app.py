import joblib
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from typing import List
import hashlib

from config import MODEL_PATH
from src.predict.predict import predict


def get_model_md5(filepath):
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(4096):  # Lecture par blocs de 4 KB
            hasher.update(chunk)
    return hasher.hexdigest()

app = FastAPI(
    title="Predict",
    description="API Predict.",
    version="1.0.0"
)
Instrumentator().instrument(app).expose(
    app=app,
    endpoint="/metrics"
)


class PredictionItem(BaseModel):
    name: str
    text: str

class ClassProbability(BaseModel):
    id_class: int
    confidence: float

class PredictionResponse(BaseModel):
    name: str
    probabilities: List[ClassProbability]

class PredictionResponseWithHash(BaseModel):
    model_hash: str
    predictions: List[PredictionResponse]


model = joblib.load(MODEL_PATH)
model_hash = get_model_md5(MODEL_PATH)

@app.post(
    path="/predict",
    response_model=PredictionResponseWithHash,
    tags=["Predict"]
)
async def predict_folder( request: List[PredictionItem] ):
    try:
        results = []
        for item in request:
            prediction = predict(item.text)

            probabilities = [
                ClassProbability(id_class=cls, confidence=confidence)
                for cls, confidence in zip(model.classes_, prediction[0])
            ]

            results.append(PredictionResponse(name=item.name, probabilities=probabilities))
        return PredictionResponseWithHash(model_hash=model_hash, predictions=results)

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error during processing: {str(e)}")
