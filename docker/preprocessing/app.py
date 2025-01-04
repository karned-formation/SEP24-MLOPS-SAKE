from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator

from src.preprocessing.preprocessing import main

app = FastAPI()
Instrumentator().instrument(app).expose(app)

@app.post("/process")
async def process_data(prediction_folder_S3:str = None):
    try:
        main(prediction_folder_S3)
        return {"message": "Data successfully preprocessed and vectorized. Outputs saved to specified directory."}

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during processing: {e}")

    