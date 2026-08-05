@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo Starting backend at 0.0.0.0:9099 ...
python -u start_backend.py
