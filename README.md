# 📸 Image Processing System (Async Backend)

## 🚀 Overview
This project processes images asynchronously from a CSV file, compressing them by **50%**, storing them in a database, and providing **API endpoints** to track their status. A **webhook flow** is implemented to notify through email after all images are processed. [Draw.io](https://drive.google.com/file/d/1-DnBlG7b78wJnopZaW5sMjR8XzL_k7kx/view?usp=sharing)

## 📑 Features
✅ **Upload CSV** with image URLs  
✅ **Validate CSV format** before processing  
✅ **Asynchronously compress images using Celery**  
✅ **Store processed image data in MongoDB**  
✅ **Check processing status via API**  
✅ **Webhook integration** for emailing Output CSV 

---

## 🏗️ System Architecture
### **1️⃣ API Endpoints**
| **Method** | **Endpoint** | **Description** |
|-----------|-------------|-----------------|
| **POST**  | `/upload` | Accepts a CSV file and an email, validates it, and returns a `request_id`. |
| **GET**   | `/status/{request_id}` | Checks the processing status of a request and also provides progress. |
| **GET**   | `/image/{file_id}` | Downloads the processed image after completion. |
| **POST**  | `/webhook-completed` | Webhook that triggers and sends an email after processing is completed. |

### **2️⃣ Data Flow**
1. **User uploads CSV → Returns `request_id`**
2. **CSV is validated**
3. **Images are compressed asynchronously using Celery**
4. **Database stores input/output image URLs**
5. **Webhook is triggered after completion**
6. **User recieves the processed CSV through email**

---

## 🛠️ Tech Stack
- **Backend:** FastAPI (Python)
- **Database:** MongoDB (GridFS for image storage)
- **Task Queue:** Celery + Redis
- **Worker:** Asynchronous processing with Celery
- **API Testing:** Postman

---

## 📜 MongoDB (Database) Schema Documentation
This collection stores **image compression requests** and tracks their processing status.

### **📌 Document Structure**
```json
{
    "request_id": "string", 
    "email": "string",
    "product_details": {
        "<prod_name>": {
            "input_urls": ["string", "string"],
            "output_urls": ["string", "string"],
            "task_ids": ["string", "string"]
        }
    },
    "status": "PENDING | COMPLETED",
    "no_img_compressed": 0,
    "total_images": 0
}
```

### Field Description
| **Field**	| **`Type`** |	**Description** |
|-----------|------------|------------------|
| request_id	| `string` |	Unique identifier for each image compression request. |
| email	| `string` |	Email address of the user who uploaded the CSV. |
| product_details	| `object` |	Dictionary storing product names and image processing details. |
| <prod_name>	| `string` |	The name of the product being processed. |
| input_urls	| `array` |	List of original image URLs before compression. |
| output_urls	| `array` |	List of compressed image URLs, corresponding to input_urls. |
| task_ids	| `array` |	Celery task IDs used for processing each image. |
| status	| `enum` |	Processing status (`PENDING` or `COMPLETED`). |
| no_img_compressed	| `integer` |	Number of images successfully compressed. |
| total_images	| `integer` |	Total images expected to be processed. |

---

## 🛠️ Setup & Installation
### **1️⃣ Install Dependencies**
1. **[Redis](https://github.com/tporadowski/redis/releases): Download and follow the msi installer here**
2. **Run this command on cmd after installing Redis**
   
   ```bash
   redis-server
   ```
4. **[MongoDB](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-windows/): Download and follow the instructions here**
5. **[Python](https://www.python.org/downloads/): Download python 3.11**
6. **Create a `credentials.json` with the following details in the root folder**

    ```
    {
        "username": "",                            //db username (keep empty if nothing)
        "password": "",                            //db password (keep empty if nothing)
        "host": "127.0.0.1",                       //db host ip
        "database": "SDE1_BACKEND",                //db name
        "compression_percentage": 50,
    
        "host_server": "127.0.0.1",                //server ip
        "port_server": "80",                       //server port
        "email": "randomrajesh164@gmail.com",      //email (test email for this project)
        "email_password": "ynmd wwwh bref ekbf"    //password
    }
    ```
   
### **2️⃣ Get it up and running**
1. **Clone the repository**
2. **Run the setup.bat file**
3. **Run the run.bat file**
4. **Open [fastapi docs](http://127.0.0.1/docs#/)**
5. **Use the upload endpoint**
