call pip install virtualenv
call python -m venv .venv
call .\\venv\\Scripts\\activate
call pip install -r requirements.txt
echo "Done Setup"
pause