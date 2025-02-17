import logging
from uuid import uuid4
from typing import List
import time
from fastapi import FastAPI, BackgroundTasks
from prometheus_fastapi_instrumentator import Instrumentator
from src.custom_logger import logger
from pydantic import BaseModel

from src.orchestrator.orchestrator import treat
from collections import defaultdict

# En attendant la mise en place d'une vraie BDD
reference_uuid_map = defaultdict(list)
database = {}

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
    message: str
    reference: str
    uuid: str
    nb: int
    time: float


def process_images(batch_uuid: str, files: list):
    logger.info("Lancement de la Background Task")
    database[batch_uuid]['status'] = 'IN_PROGRESS'
    database[batch_uuid]['prediction'] = treat(batch_uuid, files)
    logger.info("Prediction ajoutée à la database")
    database[batch_uuid]['status'] = 'COMPLETED'


@app.post(
    path="/predict",
    response_model=PredictionResult,
    tags=["Prediction"])
async def upload_images(background_task: BackgroundTasks, request: PredictionRequest ):
    reference = request.reference
    batch_uuid = str(uuid4())
    database[batch_uuid] = {
        'status': 'PENDING',
        'metadata': None ,
        'prediction': None
    }

    metadata = dict()
    metadata['n_files'] = len(request.files)
    metadata['time'] = time.time()
    metadata['uuid'] = batch_uuid
    database[batch_uuid]['metadata'] = metadata

    reference_uuid_map[reference].append(batch_uuid)
    reference_uuid_map[batch_uuid].append(batch_uuid)
    background_task.add_task(process_images, batch_uuid, request.files)
    return {"message": "Files saved successfully", "reference": reference, "uuid": batch_uuid, "nb": metadata['n_files'], "time": metadata['time']}