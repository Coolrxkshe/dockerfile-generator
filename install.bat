@echo off
echo ================================
echo  Dockerfile Generator - Setup
echo ================================
echo.

echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Install from python.org
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ================================
echo  Setup complete!
echo.
echo  To run the web app:
echo    1. venv\Scripts\activate
echo    2. streamlit run app.py
echo.
echo  Make sure Ollama is running and
echo  you have pulled a model:
echo    ollama pull codellama
echo ================================
pause