@echo off
echo 🚀 Starting Hedera Audit AI Backend...
echo ==================================================

cd /d "%~dp0"
set PYTHONPATH=src
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

pause
