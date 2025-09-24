@echo off
REM Naviguer jusqu'au dossier du projet Django
cd C:\WALNER\walner-durel\Backend

REM Activer le virtualenv (adapter le chemin si besoin)
call venv\Scripts\activate

REM Lancer le serveur Django sur toutes les interfaces, port 8000
python manage.py runserver