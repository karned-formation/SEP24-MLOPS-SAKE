from fastapi import APIRouter, FastAPI, File, UploadFile, Form
from src.orchestrator.orchestrator import *
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

app = FastAPI(
    title="/predict",
    description="Predict API (frontend)",
    version="1.0.0"
)
Instrumentator().instrument(app).expose(app=app, endpoint="/predict/metrics")

database = {}

class PredictionRequest(BaseModel):
    files: List[str]
    reference: str

class PredictionResult(BaseModel):
    uuid: str
    prediction: dict

@app.post("/predict", response_model=PredictionResult, tags=["Prediction"])
async def upload_images(request: PredictionRequest):
    files = request.files
    reference = request.reference
    if database.get(reference, 0):
        return {"message": "Reference should be unique. Try again."}
    uuid, prediction = main(files)
    database[reference] = uuid
    print(database) #TODO Delete
    return {"message": "Files saved successfully", "reference": reference, "uuid": uuid, "prediction": prediction}
