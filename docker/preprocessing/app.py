from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from src.preprocessing.preprocessing import generate_objects

app = FastAPI()
Instrumentator().instrument(app).expose(app)

class ProcessItem(BaseModel):
    clean_csv: str # Fichiers csv fusionnés

class ProcessResponse(BaseModel):
    X_train: str
    y_train: str
    X_test: str
    y_test: str
    tfidf_vectorizer: str

@app.post("/process", response_model=ProcessResponse)
async def process(item: ProcessItem):
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