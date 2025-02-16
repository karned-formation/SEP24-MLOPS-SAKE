from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from src.preprocessing.preprocessing import main, generate_objects
from fastapi.responses import StreamingResponse
from io import BytesIO


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


class ProcessItem(BaseModel):
    clean_csv: str # Fichiers csv fusionnés

class ProcessResponse(BaseModel):
    X_train: str
    y_train: str
    X_test: str
    y_test: str
    tfidf_vectorizer: str

@app.post("/process_train", response_model=ProcessResponse)
async def process_train(item: ProcessItem):
    try:
        X_train_bytes, y_train_bytes,X_test_bytes,y_test_bytes, tfidf_vectorizer_bytes = generate_objects(item.clean_csv)

        response = ProcessResponse(
            X_train= X_train_bytes,
            y_train=y_train_bytes,
            X_test=X_test_bytes,
            y_test=y_test_bytes,
            tfidf_vectorizer=tfidf_vectorizer_bytes
        )
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during processing: {e}")