@echo off
REM TourPlus AI — One-Command Full-Stack Runner (Windows Batch / CMD)
REM Starts both Django (port 8000) and Next.js (port 3000) concurrently.

title TourPlus AI Full-Stack Server

if exist "%~dp0backend\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0backend\.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" "%~dp0scripts\dev.py"
