from starlette.responses import PlainTextResponse
from fastapi import FastAPI, APIRouter
from clean_text import main

app = FastAPI()
router = APIRouter(prefix="/clean")

@router.post("/", response_class = PlainTextResponse)
def clean(text: str):    

    return main(text)
