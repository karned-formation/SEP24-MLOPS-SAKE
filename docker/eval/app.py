from fastapi import FastAPI, HTTPException, Depends

from src.eval.eval import main

app = FastAPI()

@app.post('/eval')
def eval():
    try:
        # Run the main evaluation function
        main()
    except FileNotFoundError as e:
        # Handle missing files
        raise HTTPException(status_code=404, detail=f"File not found: {e}")
    except Exception as e:
        # Handle any other exceptions
        raise HTTPException(status_code=500, detail=f"An error occurred during evaluation: {e}")