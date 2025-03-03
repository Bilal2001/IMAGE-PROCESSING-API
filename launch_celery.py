# Celery Configuration
from celery import Celery


celery_app = Celery(
    "tasks",
    broker="redis://127.0.0.1:6379/0",  # Still need a broker (Redis or RabbitMQ) [set up redis using wsl or something]
    backend="mongodb://localhost:27017/celery_db",  # Use MongoDB for task results
    include=["server.celery_worker"]
)
celery_app.conf.task_routes = {
    "server.celery_worker.compress_image": {"queue": "celery"},
}