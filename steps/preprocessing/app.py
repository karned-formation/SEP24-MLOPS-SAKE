from fastapi import FastAPI, HTTPException
import os
from preprocessing import main

# Paths
clean_dataset_path = "/app/data/cleaned/cleaned_dataset.csv"

app = FastAPI()
@app.get("/process")
async def process_data():
    # Check if the dataset exists
    if not os.path.exists(clean_dataset_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        main(clean_dataset_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during processing: {e}")

    return {"message": "Data successfully preprocessed and vectorized. Outputs saved to specified directory."}