from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from src.predict.predict import main

app = FastAPI()
Instrumentator().instrument(app).expose(app)

class PredictionRequest(BaseModel):
    prediction_folder: str

@app.post("/predict")
async def predict_folder(prediction_folder:str = None):
    """
    Endpoint for triggering the prediction process.
    """
    try:
        # Call the main function with the prediction folder
        prediction = main(prediction_folder)
        return {"message": "Prediction completed successfully.", "data": prediction}

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error during processing: {str(e)}")

    