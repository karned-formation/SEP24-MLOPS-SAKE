from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from predict import main

app = FastAPI()

class PredictionRequest(BaseModel):
    prediction_folder: str

@app.post("/predict")
async def predict_folder(request: PredictionRequest):
    """
    Endpoint for triggering the prediction process.
    """
    try:
        # Call the main function with the prediction folder
        prediction = main(request.prediction_folder)
        return {"message": "Prediction completed successfully.", "data": prediction}

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error during processing: {str(e)}")

    