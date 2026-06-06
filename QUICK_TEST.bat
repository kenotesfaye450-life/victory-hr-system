@echo off
cls
echo ===============================================
echo   VICTORY HR SYSTEM - QUICK DIAGNOSTIC TEST
echo ===============================================
echo.

python test_connection.py

echo.
echo ===============================================
echo   TEST COMPLETE
echo ===============================================
echo.
echo If all tests passed, start the server with:
echo   START_SERVER.bat
echo.
echo Then open browser:
echo   http://127.0.0.1:5000
echo.

pause
