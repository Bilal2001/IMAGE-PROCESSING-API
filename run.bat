:: Run server
start cmd /k "call .\\venv\\Scripts\\activate && python launch.py"

:: Run Celery
start cmd /k "call cd server && celery -A celery_worker worker --pool=solo --loglevel=info"