@echo off

REM update pip
echo update pip
call python.exe -m pip install --upgrade pip

REM Check if .venv folder exists
if not exist .venv (
    echo Creating .venv virtual environment...
    python -m venv .venv
) else (
    echo .venv virtual environment already exists.
)

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Check if requirements.txt exists and install packages
if exist requirements.txt (
    echo Installing packages from requirements.txt...
    pip install -r requirements.txt
    echo Packages installed successfully.
) else (
    echo No requirements.txt file found.
)

REM keep the cmd shell open
pause > nul