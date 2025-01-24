from src.admin.mlflow_tracking import list_mlflow_runs, git_revert_to_commit, save_to_mlflow, register_model_to_s3, run_command
from src.admin.select_images import delete_image_file,get_image_list,save_uploaded_image
from fastapi import FastAPI, UploadFile, File, Form
from src.custom_logger import logger
from fastapi.responses import JSONResponse
import json
import numpy as np 
import traceback

def load_confusion_matrix(file_path='metrics/confusion_matrix.json'):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Convert nested dict to numpy array
    matrix = np.array([[data[str(i)][str(j)] for j in range(3)] for i in range(3)])
    return matrix

def load_scores(file_path='metrics/scores.json'):
    with open(file_path, 'r') as f:
        scores = json.load(f)
    return scores

app = FastAPI()

@app.post("/train")
async def train_model():
    try:
        command_outputs = ""

        # Run DVC reproduce
        dvc_repro_output = run_command("dvc repro --force")
        logger.info(dvc_repro_output)

        # Git add and commit
        git_add_output  = run_command("git add dvc.lock data/raw_per_classes.dvc")     
        logger.info(git_add_output)

        git_commit_output = run_command('git commit -m "Training completed."')
        logger.info(git_commit_output)


        dvc_push_output = run_command("dvc push")
        logger.info(dvc_push_output)

        
        git_push_output = run_command("git push")
        logger.info(git_push_output)

        # Get commit hash
        commit_hash_output = run_command("git rev-parse HEAD")
        logger.info("COMMIT HASH "+commit_hash_output)

        # Save ml flow run                  
        run_id = save_to_mlflow(commit_hash_output)
        logger.info("RUN ID: " + run_id)

        # Load and display confusion matrix
        matrix = load_confusion_matrix()
        logger.info("CONFUSION MATRIX" + matrix)

        scores = load_scores()
        logger.info(scores)

        return JSONResponse(content={
                "message": "Training completed successfully",
                "output": str(command_outputs),
                "confusion_matrix": str(matrix),
                "scores": str(scores),
                "run_id": str(run_id)
            }
        )
    except Exception as e:

        logger.error(e.with_traceback())
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/registermodel")
async def register_model():
    try:
        success = register_model_to_s3()
        if success:
            return JSONResponse(content={"message": "Model registered successfully"})
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to register model"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/get_images")
async def get_images():
    try:
        images = get_image_list()
        return JSONResponse(content=images)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/deleteimage")
async def delete_image(folder: str, image_name: str):
    try:
        success = delete_image_file(folder, image_name)
        if success:
            return JSONResponse(content={"message": "Image deleted successfully"})
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to delete image"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/addimage")
async def add_image(file: UploadFile = File(...), folder: str = Form(...)):
    try:
        success = await save_uploaded_image(file, folder)
        if success:
            return JSONResponse(content={"message": "Image uploaded successfully"})
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to upload image"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/getmlflowruns")
async def get_runs():
    try:
        runs = list_mlflow_runs()
        return JSONResponse(content=runs)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/reverttocommit")
async def revert_to_commit(commit_hash: str):
    try:
        success, message = git_revert_to_commit(commit_hash)
        if success:
            return JSONResponse(content={"message": f"Successfully reverted to commit {commit_hash}"})
        else:
            return JSONResponse(
                status_code=500,
                content={"error": f"Revert failed: {message}"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )