from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from pathlib import Path
from src.orchestrator.orchestrator import save_images, main
from collections import defaultdict
from src.custom_logger import logger
import time

app = FastAPI()

# En attendant la mise en place d'une vraie BDD
reference_uuid_map = defaultdict(list)
database = {}
 

def process_images(uuid: str):
    logger.info("Lancement de la Background Task")
    database[uuid]['status'] = 'IN_PROGRESS'
    database[uuid]['prediction'] = main(uuid)
    logger.info("Prediction ajoutée à la databse")
    database[uuid]['status'] = 'COMPLETED'


# Endpoint to receive and save images
@app.post("/predict")
async def upload_images(background_task: BackgroundTasks, 
                        files: list[UploadFile] = File(...),
                        reference: str = Form(...)
                        ):
    uuid = save_images(files)
    database[uuid] = {
        'status': 'PENDING',
        'metadata': None ,
        'prediction': None
    }

    metadata = dict()
    metadata['n_files'] = len(files)
    metadata['time'] = time.time()
    metadata['uuid'] = uuid
    database[uuid]['metadata'] = metadata
    reference_uuid_map[reference].append(uuid)
    reference_uuid_map[uuid].append(uuid)
    background_task.add_task(process_images, uuid)
    return {"message": "Files saved successfully", "reference": reference, "uuid": uuid, "len": metadata['n_files'], "time": metadata['time']}

@app.get('/predict/{reference}')
def get_prediction(reference):
    predictions = []
    for uuid in reference_uuid_map[reference]:
        predictions.append(database[uuid])
    return predictions 