import io
from fastapi import APIRouter, HTTPException, Response
import pandas as pd

from ..email import send_email_with_attachment
from ..manager import db_instance, log
from ..enums import *


router = APIRouter(tags=['status'])

@router.get("/status")
async def check_status(request_id: str):
    """
        Get current status of request id
    """
    data = db_instance["DATA"].find_one({DataCollection.REQ_ID: request_id})
    if data is None:
        raise HTTPException(status_code=400, detail="Request id not found.")
    status = data[DataCollection.STATUS]

    progress = (data[DataCollection.IMG_COMPRESSED_COUNT] / data[DataCollection.TOTAL_IMG]) * 100

    return {"status": status, "progress": f"{progress}%"}

    #* In case code needed for giving downloadable csv
    # res = []
    # for k,v in data[DataCollection.PROD_DETAILS].items():
    #     res.append([k, v[DataCollection.INP_URLS], v[DataCollection.OUT_URLS]])
    
    # df = pd.DataFrame(res, columns=[OutputColumns.PNAME, OutputColumns.IMG_URLS, OutputColumns.OUTPUT_URLS])

    # # Convert DataFrame to CSV in memory
    # csv_buffer = io.StringIO()
    # df.to_csv(csv_buffer, index=False)
    # csv_buffer.seek(0)  # Move cursor to the start

    # # Return as downloadable CSV file
    # return Response(
    #     content=csv_buffer.getvalue(),
    #     media_type="text/csv",
    #     headers={
    #         "Content-Disposition": f"attachment; filename={request_id}.csv"
    #     }
    # )


@router.post("/webhook-completed")
async def on_complete(request_id: str):
    """
    
    """
    db_instance["DATA"].find_one_and_update({DataCollection.REQ_ID: request_id}, {"$set": {DataCollection.STATUS: DataCollection.STATUS_COMPLETED}})
    log(LogType.SUCCESS, f"COMPLETED req_id = {request_id}")
    data = db_instance["DATA"].find_one({DataCollection.REQ_ID: request_id})

    res = []
    for k,v in data[DataCollection.PROD_DETAILS].items():
        res.append([k, v[DataCollection.INP_URLS], v[DataCollection.OUT_URLS]])
    
    df = pd.DataFrame(
        res, 
        columns=[
            OutputColumns.PNAME, 
            OutputColumns.IMG_URLS, 
            OutputColumns.OUTPUT_URLS
        ]
    )

    send_email_with_attachment(
        to_email=data[DataCollection.EMAIL], 
        subject=f"Compression Completed for {request_id}", 
        body="Kindly find your attached Output file.", 
        file=df
    )