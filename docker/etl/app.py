from ingest_all import ingest_all
from clean_all import clean_all
from fastapi import FastAPI, HTTPException
import os

raw_dataset_dir = os.getenv("RAW_DATASET_DIR")
ocr_text_dir = os.getenv("OCR_TEXT_DIR")
ocr_endpoint = os.getenv("OCR_ENDPOINT")
clean_endpoint = os.getenv("CLEAN_ENDPOINT")
cleaned_datasets_dir = os.getenv("CLEANED_DATASETS_DIR")

app = FastAPI()


@app.post("/ingest")
def ingest():
    # Check if raw dataset directory exists
    if not os.path.exists(raw_dataset_dir):
        raise HTTPException(status_code=404, detail="Raw dataset directory not found")
    try:
        ingest_all(ocr_endpoint, raw_dataset_dir, ocr_text_dir)
        return {"message":"Ingestion completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clean")
def clean():
    # Check if OCR text directory exists
    if not os.path.exists(ocr_text_dir):
        raise HTTPException(status_code=404, detail="OCR text directory not found")
    try:
        clean_all(clean_endpoint, ocr_text_dir, cleaned_datasets_dir)
        return "Cleaning completed"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))