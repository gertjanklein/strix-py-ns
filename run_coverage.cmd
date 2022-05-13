@echo off

if "%VIRTUAL_ENV%" == "" (
    echo Activating virtual environment...
    call %~dp0venv\scripts\activate.bat
)

if "%PYTHONPATH%" == "" set PYTHONPATH=src
if "%PYTHONDEVMODE%" == "" set PYTHONDEVMODE=1

python -m pytest --cov=src tests
coverage html
