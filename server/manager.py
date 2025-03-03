import json
import os
import traceback
from .functions import log, LogType
from .enums import CREDENTIALS_KEYS
from pymongo import MongoClient
from gridfs import GridFS


if not os.path.exists(os.path.join("credentials.json")):
    log(LogType.ERROR, "No credentials.json")
    exit(0)

with open(os.path.join("credentials.json"), "r") as file:
    credentials = json.load(file)
    file.close() 

QUALITY = credentials[CREDENTIALS_KEYS.COMPRESSION_PERCENTAGE]
HOST = credentials[CREDENTIALS_KEYS.HOST_SERVER]
PORT = credentials[CREDENTIALS_KEYS.PORT_SERVER]
EMAIL_SENDER = credentials[CREDENTIALS_KEYS.EMAIL_SENDER]
EMAIL_PASSWORD = credentials[CREDENTIALS_KEYS.EMAIL_PASSWORD]

url = f"mongodb://{credentials[CREDENTIALS_KEYS.DB_UNAME]}{':' if len(credentials[CREDENTIALS_KEYS.DB_UNAME]) != 0 else ''}{credentials[CREDENTIALS_KEYS.DB_PASSWORD]}{'@' if len(credentials[CREDENTIALS_KEYS.DB_UNAME]) != 0 else ''}{credentials[CREDENTIALS_KEYS.HOST]}:27017/{credentials[CREDENTIALS_KEYS.DATABASE]}"

try:
    db_instance = MongoClient(url)[credentials[CREDENTIALS_KEYS.DATABASE]]
    fs = GridFS(db_instance, collection="compressed_images")  # Separate collection for images
    log(LogType.SUCCESS, "DB Connected")
except:
    log(LogType.ERROR, "DB couldn't connect")
    log(LogType.ERROR, traceback.format_exc(limit=1))
    exit(0)