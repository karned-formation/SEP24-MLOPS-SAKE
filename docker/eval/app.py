from fastapi import FastAPI, HTTPException, Depends
from eval import main
import os

MODEL_PATH = '/app/models/ovrc.joblib'
X_TEST_PATH = '/app/data/processed/test/X_test.joblib'
Y_TEST_PATH = '/app/data/processed/test/y_test.joblib'
METRICS_DIR = '/app/metrics/'

app = FastAPI()

def get_paths():
    paths = {
        "model_path": MODEL_PATH,
        "X_test_path": X_TEST_PATH,
        "y_test_path": Y_TEST_PATH,
        "metrics_dir": METRICS_DIR,
    }

    # Ensure the metrics directory exists
    os.makedirs(paths["metrics_dir"], exist_ok=True)
    return paths

@app.get('/eval')
def eval(paths: dict = Depends(get_paths)):
    try:
        # Run the main evaluation function
        main(paths["model_path"], paths["X_test_path"], paths["y_test_path"], paths["metrics_dir"])
        return {"message": f"Metrics saved successfully to {paths['metrics_dir']}"}
    except FileNotFoundError as e:
        # Handle missing files
        raise HTTPException(status_code=404, detail=f"File not found: {e}")
    except Exception as e:
        # Handle any other exceptions
        raise HTTPException(status_code=500, detail=f"An error occurred during evaluation: {e}")