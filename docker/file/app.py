from typing import List, Optional
from io import BytesIO
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from src.file.file_manager import push_to_bucket

app = FastAPI(
    title="File API",
    description="API de gestion des fichiers.",
    version="1.0.0"
)
Instrumentator().instrument(app).expose(
    app=app,
    endpoint="/metrics"
)


class Files(BaseModel):
    content: str
    name: str | None = None

    class Config:
        arbitrary_types_allowed = True

class InputUpload(BaseModel):
    files: List[Files]
    prefix: Optional[str] = None

class OutputUpload(BaseModel):
    full_path: str
    filename: str

@app.post(
    path="/load",
    tags=["File"],
    response_model=List[OutputUpload]
)
async def upload( payload: InputUpload ):
    try:
        infos = push_to_bucket(payload.files, payload.prefix)
        return infos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
