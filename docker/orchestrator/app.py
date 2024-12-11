from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from pathlib import Path
from src.orchestrator.orchestrator import save_images, main

app = FastAPI()

# En attendant la mise en place de BDD
database = {}

def process_images(uuid: str):
    print("Lancement de la Background Task")
    prediction = main(uuid)
    print(prediction)
    return prediction

# Endpoint to receive and save images
@app.post("/predict")
async def upload_images(background_task: BackgroundTasks, 
                        files: list[UploadFile] = File(...),
                        reference: str = Form(...)
                        ):
    if database.get(reference, 0):
        return {"message": "Reference should be unique. Try again."}
    uuid = save_images(files)
    database[reference] = uuid
    print(database) #TODO Delete
    background_task.add_task(process_images, uuid)
    return {"message": "Files saved successfully", "reference": reference, "uuid": uuid}