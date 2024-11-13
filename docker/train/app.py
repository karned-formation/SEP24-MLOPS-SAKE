from fastapi import FastAPI, HTTPException
from train import main

app = FastAPI()

@app.get('/train')
def train():
    """
    Trains the model using the specified data directory and saves it to the specified model path.
    """
    try:
        # Execute training process
        main()
        return {"message": "Model trained and saved successfully"}
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")