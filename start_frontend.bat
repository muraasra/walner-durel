@echo off
cd /d "C:\WALNER\walner-durel\Frontend" || (echo Dossier introuvable & pause & exit /b 1)

set CHOKIDAR_USEPOLLING=0
:: Nitro (Nuxt 3) lit surtout ces variables:
set NITRO_HOST=localhost
set NITRO_PORT=3000

:: On force aussi via les flags (fiable sous Windows)
call npx nuxi dev --host localhost --port 3000
