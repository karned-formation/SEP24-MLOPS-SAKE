from src.admin.mlflow_tracking import list_mlflow_runs, git_revert_to_commit, save_to_mlflow, register_model_to_s3, run_command
from src.admin.select_images import delete_image_file,get_image_list,save_uploaded_image
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import json
import numpy as np 

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
        command_outputs += f"DVC REPRO : {dvc_repro_output}"
        
        # Load and display confusion matrix
        matrix = load_confusion_matrix()
        scores = load_scores()

        # Git add and commit
        git_add_output = run_command("git add dvc.lock data/raw_per_classes.dvc")          
        command_outputs += f"GIT ADD : {git_add_output}"

        git_commit_output = run_command('git commit -m "Training completed."')
        command_outputs += f"GIT COMMIT : {git_commit_output}"

        # Get commit hash
        commit_hash_output = run_command("git rev-parse HEAD")
        
        # DVC PUSH
        dvc_push_output = run_command("dvc push")
        command_outputs += f"DVC PUSH : {dvc_push_output}"

        # Save ml flow run                  
        run_id = save_to_mlflow(commit_hash_output)
        command_outputs += "Successfully saved run in MLFLOW."
        
        return JSONResponse(content={
                "message": "Training completed successfully",
                "output": str(command_outputs),
                "confusion_matrix": str(matrix),
                "scores": str(scores),
                "run_id": str(run_id)
            }
        )
    except Exception as e:
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