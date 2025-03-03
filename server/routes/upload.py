import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File
import pandas as pd
from ..manager import db_instance, QUALITY
from ..enums import *
from ..functions import log
from ..celery_worker import compress_image


router = APIRouter(prefix='/upload', tags=['upload'])

@router.post("/")
async def upload_document(email: str, file: UploadFile = File(...)):
    """
        Upload csv, endpoint will validate the format and return the req id
    """

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    csv = pd.read_csv(file.file)

    #* Check if csv is formatted correctly
    if csv.columns.to_list() != ["S. No.", "Product Name","Input Image Urls"] and len(csv) == 0:
        raise HTTPException(status_code=400, detail='Invalid CSV. Please upload a CSV file with columns "S. No.", "Product Name","Input Image Urls" and size > 0.')
    
    try:
        csv["clean_image_urls"] = csv[UploadColumns.IMG_URLS].apply(lambda x: x.split(","))
    except:
        raise HTTPException(status_code=400, detail='Invalid CSV. Please upload a CSV file with column "Input Image Urls" having image urls separated with ",".')

    req_id = str(uuid.uuid4())
    products = {}
    no_img = 0

    for i in csv.itertuples():
        #* Add it to mongo as a collection for each row in the csv in the following document format:
        """
            {
                request_id: ...,
                email: ...,
                product_details: {
                    <prod_name>: {
                        input_urls: ["...", "..."],
                        output_urls: ["...", "..."],
                    },
                    ...
                },
                status: any [PENDING, COMPLETED],    
                no_img_compressed: 0
                total_img: 0
            }
        """
        prod_name = str(i[1])
        clean_urls = i[4]
        task_ids = []

        for img_url in clean_urls:
            task = compress_image.delay(req_id, prod_name, img_url, QUALITY)  # Run Celery task asynchronously
            task_ids.append(task.id)
            no_img += 1

        products[prod_name] = {          
            "input_urls": clean_urls,
            "output_urls": [],
            "task_ids": task_ids        
        }
        log(LogType.INFO, f"Saved data to db for {req_id} and {prod_name}")
    

    db_instance["DATA"].insert_one({
        "request_id": req_id,
        "email": email,
        "product_details": products,      
        "status": DataCollection.STATUS_PENDING,
        "no_img_compressed": 0,
        "total_images": no_img
    })

    return req_id