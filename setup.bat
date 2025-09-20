@echo off
echo "Creating virtual environment..."
if not exist venv (
    python -m venv venv
)
echo "Activating virtual environment and installing dependencies..."
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo "Setup complete."