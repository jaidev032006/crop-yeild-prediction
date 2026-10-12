@echo off
title AgriSmart - Precision Agriculture Platform
echo Starting AgriSmart Platform...
"%~dp0.venv\Scripts\python.exe" "%~dp0app.py" %*
pause
