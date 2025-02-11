import joblib
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from typing import List

from config import MODEL_PATH
from src.predict.predict import predict

app = FastAPI(
    title="Predict",
    description="API Predict.",
    version="1.0.0"
)
Instrumentator().instrument(app).expose(
    app=app,
    endpoint="/predict/metrics"
)


class PredictionItem(BaseModel):
    ref: str
    data: str

class ClassProbability(BaseModel):
    id_class: int
    confidence: float

class PredictionResponse(BaseModel):
    ref: str
    probabilities: List[ClassProbability]

@app.post(
    path="/predict",
    response_model=List[PredictionResponse],
    tags=["Predict"]
)
async def predict_folder( request: List[PredictionItem] ):
    try:
        results = []
        model = joblib.load(MODEL_PATH)
        for item in request:
            prediction = predict(item.data)

            probabilities = [
                ClassProbability(id_class=cls, confidence=confidence)
                for cls, confidence in zip(model.classes_, prediction[0])
            ]

            results.append(PredictionResponse(ref=item.ref, probabilities=probabilities))

        return results

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error during processing: {str(e)}")
