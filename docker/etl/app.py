from ingest_all import ingest_all
from clean_all import clean_all
from fastapi import FastAPI, HTTPException
import os

app = FastAPI()

@app.post("/ingest")
def ingest():
    try:
        ingest_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clean")
def clean():
    try:
        clean_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))