    @echo off
    REM Change directory to your frontend project
    cd /d C:\WALNER\walner-durel\Frontend\

    REM Restore PM2 processes from saved list
    pm2 resurrect

    REM Optional: Keep window open to see output if run manually for testing
    REM pause