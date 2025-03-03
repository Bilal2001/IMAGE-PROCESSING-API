from fastapi import FastAPI
from .routes import *

app = FastAPI()

app.include_router(UploadRoute)
app.include_router(StatusRoute)
app.include_router(ImageRoute)