@echo off
cd /d "C:\Users\gifte\Desktop\boutique_POS"

:: activate venv if you’re using one
call myenv\Scripts\activate

:: run the sync script first
python sync.py

:: start Django server silently
start "" /min python manage.py runserver 127.0.0.1:8000

:: wait a bit for the server to start
timeout /t 5 /nobreak >nul

:: open the POS in default browser
start "" http://127.0.0.1:8000
exit
