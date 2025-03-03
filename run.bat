:: Run server
start cmd /k "call .\\venv\\Scripts\\activate && python launch.py"

:: Run Celery
start cmd /k "call celery -A launch_celery worker --pool=solo --loglevel=info"