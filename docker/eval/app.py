from fastapi import FastAPI, HTTPException, Depends
from prometheus_fastapi_instrumentator import Instrumentator

from src.eval.eval import main

app = FastAPI()
Instrumentator().instrument(app).expose(app)

@app.post('/eval')
def eval(prediction_folder_S3:str = None):
    try:
        # Run the main evaluation function
        main(prediction_folder_S3)
    except FileNotFoundError as e:
        # Handle missing files
        raise HTTPException(status_code=404, detail=f"File not found: {e}")
    except Exception as e:
        # Handle any other exceptions
        raise HTTPException(status_code=500, detail=f"An error occurred during evaluation: {e}")