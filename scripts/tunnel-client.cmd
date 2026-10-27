@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tunnel-client.ps1" %*