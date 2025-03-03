import io
import traceback
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..manager import fs, log, LogType
from bson import ObjectId

router = APIRouter(prefix='/image', tags=['image'])

@router.get("/{file_id}")
def get_image(file_id: str):
    """
    Fetches and returns a compressed image from MongoDB.
    """
    try:
        image_file = fs.get(ObjectId(file_id))
        return StreamingResponse(io.BytesIO(image_file.read()), media_type="image/jpeg")

    except Exception as e:
        log(LogType.ERROR, f"Error {e}, {traceback.format_exc(limit=1)}")
        raise HTTPException(status_code=404, detail=f"Image not found")