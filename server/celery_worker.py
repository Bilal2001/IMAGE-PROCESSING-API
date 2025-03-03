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
# from enums import *
class LogType:
    INFO = "info"
    SUCCESS = "success"
    ERROR = "error"

class CREDENTIALS_KEYS:
    DB_UNAME = "username"
    DB_PASSWORD = "password"
    HOST = "host"
    DATABASE = "database"


    HOST_SERVER = "host_server"
    PORT_SERVER = "port_server"
    COMPRESSION_PERCENTAGE = "compression_percentage"

class DataCollection:
    """
        {
            request_id: ...,
            product_details: {
                <prod_name>: {
                    input_urls: ["...", "..."],
                    output_urls: ["...", "..."],
                },
                ...
            },
            status: any [PENDING, COMPLETED],
            no_img_compressed: 0
        }
    """
    REQ_ID = "request_id"
    PROD_DETAILS = "product_details"
    STATUS = "status"
    INP_URLS = "input_urls"
    OUT_URLS = "output_urls"
    IMG_COMPRESSED_COUNT = "no_img_compressed"
    TOTAL_IMG = "total_images"

    STATUS_COMPLETED = "completed"
    STATUS_PENDING = "pending"    


def log(log_type: LogType, message: str):
    os.makedirs(os.path.join("content", "logs"), exist_ok=True)
    current_datetime = datetime.now()
    message = f"{current_datetime} : {log_type.upper()}: {message}"
    try:
        print(message)
        with open(os.path.join("content", "logs", f"{current_datetime.date().strftime('%Y-%m-%d')}.txt"), "a+") as f:
            f.write(f"{message}\n")
            f.close()
    except:
        ...
        
if not os.path.exists(os.path.join("credentials.json")):
    log(LogType.ERROR, "No credentials.json")
    exit(0)

with open(os.path.join("credentials.json"), "r") as file:
    credentials = json.load(file)
    file.close() 

QUALITY = credentials[CREDENTIALS_KEYS.COMPRESSION_PERCENTAGE]
HOST = credentials[CREDENTIALS_KEYS.HOST_SERVER]
PORT = credentials[CREDENTIALS_KEYS.PORT_SERVER]

url = f"mongodb://{credentials[CREDENTIALS_KEYS.DB_UNAME]}{':' if len(credentials[CREDENTIALS_KEYS.DB_UNAME]) != 0 else ''}{credentials[CREDENTIALS_KEYS.DB_PASSWORD]}{'@' if len(credentials[CREDENTIALS_KEYS.DB_UNAME]) != 0 else ''}{credentials[CREDENTIALS_KEYS.HOST]}:27017/{credentials[CREDENTIALS_KEYS.DATABASE]}"

try:
    db_instance = MongoClient(url)[credentials[CREDENTIALS_KEYS.DATABASE]]
    fs = GridFS(db_instance, collection="compressed_images")  # Separate collection for images
    log(LogType.SUCCESS, "DB Connected")
except:
    log(LogType.ERROR, "DB couldn't connect")
    log(LogType.ERROR, traceback.format_exc(limit=1))
    exit(0)


# Celery Configuration
celery_app = Celery(
    "tasks",
    broker="redis://127.0.0.1:6379/0",  # Still need a broker (Redis or RabbitMQ) [set up redis using wsl or something]
    backend="mongodb://localhost:27017/celery_db"  # Use MongoDB for task results
)
celery_app.conf.task_routes = {
    "server.celery_worker.compress_image": {"queue": "celery"},
}

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
