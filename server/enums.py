
class LogType:
    INFO = "info"
    SUCCESS = "success"
    ERROR = "error"

class UploadColumns:
    SNO = "S. No."
    PNAME = "Product Name"
    CLEAN_URLS = "clean_image_urls"
    IMG_URLS = "Input Image Urls"

class OutputColumns(UploadColumns):
    OUTPUT_URLS = "Output Image Urls"

class CREDENTIALS_KEYS:
    DB_UNAME = "username"
    DB_PASSWORD = "password"
    HOST = "host"
    DATABASE = "database"
    EMAIL_SENDER = "email"
    EMAIL_PASSWORD = "email_password"

    HOST_SERVER = "host_server"
    PORT_SERVER = "port_server"
    COMPRESSION_PERCENTAGE = "compression_percentage"

class DataCollection:
    """
        {
            request_id: ...,
            email: ...,
            product_details: {
                <prod_name>: {
                    input_urls: ["...", "..."],
                    output_urls: ["...", "..."],
                    task_ids: ["...", "..."]
                },
                ...
            },
            status: any [PENDING, COMPLETED],
            no_img_compressed: 0,
            total_images: x,
        }
    """
    REQ_ID = "request_id"
    EMAIL = "email"
    PROD_DETAILS = "product_details"
    STATUS = "status"
    INP_URLS = "input_urls"
    OUT_URLS = "output_urls"
    IMG_COMPRESSED_COUNT = "no_img_compressed"
    TOTAL_IMG = "total_images"

    STATUS_COMPLETED = "completed"
    STATUS_PENDING = "pending"    