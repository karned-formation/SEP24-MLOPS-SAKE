from fastapi import FastAPI, HTTPException
import os
from preprocessing import main

# Paths
dataset_path = '/app/data/cleaned/cleaned_dataset.csv'
dataset_dir = '/app/data/processed/'
vectorizer_path = '/app/data/vectorizers/tfidf.joblib'

app = FastAPI()
@app.get("/process")
async def process_data():
    # Check if the dataset exists
    if not os.path.exists(dataset_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        main(dataset_path=dataset_path, dataset_dir=dataset_dir, vectorizer_path=vectorizer_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during processing: {e}")

    return {"message": "Data successfully preprocessed and vectorized. Outputs saved to specified directory."}