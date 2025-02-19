from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from src.train.train import main
from pydantic import BaseModel

app = FastAPI()
Instrumentator().instrument(app).expose(app)

class ProcessItem(BaseModel):
    X_train: str
    y_train: str

class ProcessResponse(BaseModel):
    ovrc: str # modèle entrainé 

@app.post('/train', response_model=ProcessResponse)
def train(item: ProcessItem):
    """
    Trains the model using the specified data and returns a trained model
    """
    try:
        # Execute training process
        ovrc_bytes = main(item.X_train, item.y_train)

        response = ProcessResponse(
            ovrc=ovrc_bytes
        )    

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")