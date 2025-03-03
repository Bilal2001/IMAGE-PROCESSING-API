from datetime import datetime
import json
import os
import traceback
from celery import Celery
from PIL import Image
import io
from gridfs import GridFS
from pymongo import MongoClient
import requests
from launch_celery import celery_app
from .enums import *
from .manager import log, db_instance, fs, HOST, PORT


@celery_app.task(name="server.celery_worker.compress_image")
def compress_image(request_id, product_name, image_url, output_quality):
    """
        Fetches an image from a URL, compresses it to the given quality, 
        and returns the compressed image as url.
    """
    try:
        # Download the image from the URL
        response = requests.get(image_url)
        response.raise_for_status()
        print(response.text)

        # Open image using PIL
        img = Image.open(io.BytesIO(response.content))

        # Convert to RGB if needed
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Compress image and save to memory buffer
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="JPEG", quality=output_quality)
        img_buffer.seek(0)

        # Store compressed image in MongoDB GridFS
        file_id = fs.put(img_buffer.getvalue(), filename=os.path.basename(image_url))
        new_output_url = f"http://{HOST}:{PORT}/image/{file_id}"

        # In mongo update the number of files compressed by adding the output url
        query = {DataCollection.REQ_ID: request_id}  # Find the document by request_id
        update = {
            "$push": {f"{DataCollection.PROD_DETAILS}.{product_name}.{DataCollection.OUT_URLS}": new_output_url},  # Append to output_urls
            "$inc": {DataCollection.IMG_COMPRESSED_COUNT: 1}  # Increment compressed image count
        }

        result = db_instance["DATA"].update_one(query, update)

        doc = db_instance["DATA"].find_one(query, {DataCollection.TOTAL_IMG: 1, DataCollection.IMG_COMPRESSED_COUNT: 1})
        if doc[DataCollection.TOTAL_IMG] == doc[DataCollection.IMG_COMPRESSED_COUNT]:
            requests.post(url=f"http://{HOST}:{PORT}/status/webhook-completed", params={"request_id": request_id})
        
        return {"status": "success"}

    except Exception as e:
        log(LogType.ERROR, f"req_id = {request_id}, pname = {product_name}, url = {image_url}, error = {e}")
        return {"status": "error", "message": str(e)}
