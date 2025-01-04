from fastapi import FastAPI, File, UploadFile, Form
from pathlib import Path
from src.orchestrator.orchestrator import *
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)

# En attendant la mise en place de BDD
database = {}

# Endpoint to receive and save images
@app.post("/predict")
async def upload_images(
    files: list[UploadFile] = File(...),
    reference: str = Form(...)
):
    if database.get(reference, 0):
        return {"message": "Reference should be unique. Try again."}
    uuid, prediction = main(files)
    database[reference] = uuid
    print(database) #TODO Delete
    return {"message": "Files saved successfully", "reference": reference, "uuid": uuid, "prediction": prediction}

    