from starlette.responses import PlainTextResponse
from fastapi import FastAPI
from clean import main

app = FastAPI()

@app.post("/clean", response_class = PlainTextResponse)
def clean(text: str):    

    return main(text)
