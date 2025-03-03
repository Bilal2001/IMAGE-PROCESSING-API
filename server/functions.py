import os
from datetime import datetime
from .enums import LogType



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