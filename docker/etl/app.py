from fastapi import FastAPI, HTTPException
from starlette.responses import PlainTextResponse
from prometheus_fastapi_instrumentator import Instrumentator
from src.data.ingest_etl import ingest_train, ingest_prediction
from src.data.clean_etl import clean_train, clean_prediction

app = FastAPI()
Instrumentator().instrument(app).expose(app)

@app.post("/ingest", response_class = PlainTextResponse)
def ingest(prediction_folder:str = None):
    try:
        if prediction_folder:
            ingest_prediction(prediction_folder)
        else:
            ingest_train()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clean", response_class = PlainTextResponse)
def clean(prediction_folder:str = None):
    try:
        if prediction_folder:
            clean_prediction(prediction_folder)
        else :
            clean_train()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))