from fastapi import FastAPI, HTTPException, Depends
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from src.eval.eval import main
from src.custom_logger import logger
import json

app = FastAPI()
Instrumentator().instrument(app).expose(app)


class ProcessItem(BaseModel):
    X_test: str
    y_test: str
    model: str

class ProcessResponse(BaseModel):
    scores: str
    confusion_matrix: str

@app.post('/eval', response_model=ProcessResponse)
def eval(item: ProcessItem):
    try:
        # Run the main evaluation function
        scores,confusion_matrix = main(item.X_test, item.y_test, item.model)
        response = ProcessResponse(
            scores=json.dumps(scores),
            confusion_matrix=json.dumps(confusion_matrix)
        )
        return response
    except Exception as e:

        # Handle any other exceptions
        logger.error(e)
        raise HTTPException(status_code=500, detail=f"An error occurred during evaluation: {e}")