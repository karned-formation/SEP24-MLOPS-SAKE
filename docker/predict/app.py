from fastapi import FastAPI, HTTPException
import os
from predict import main

app = FastAPI()
@app.get("/process")
async def process_data():
    try:
        main()
        return {"message": "Data successfully preprocessed and vectorized. Outputs saved to specified directory."}

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during processing: {e}")

    