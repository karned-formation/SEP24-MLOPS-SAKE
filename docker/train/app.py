from fastapi import FastAPI, HTTPException
from train import main

DEFAULT_DATA_DIR = '/app/data/processed/train'
DEFAULT_MODEL_PATH = '/app/models/ovrc.joblib'

app = FastAPI()

@app.get('/train')
def train(data_dir: str = DEFAULT_DATA_DIR, model_path: str = DEFAULT_MODEL_PATH):
    """
    Trains the model using the specified data directory and saves it to the specified model path.
    """
    try:
        # Execute training process
        main(data_dir, model_path)
        return {"message": f"Model trained and saved successfully to {model_path}"}
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")