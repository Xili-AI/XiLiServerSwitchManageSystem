@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0show-credentials.ps1" %*