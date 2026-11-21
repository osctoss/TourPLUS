# TourPlus AI — One-Command Full-Stack Runner (PowerShell)
# Starts both Django (port 8000) and Next.js (port 3000) concurrently.

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $scriptDir "backend\.venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

$devScript = Join-Path $scriptDir "scripts\dev.py"

& $pythonExe $devScript
