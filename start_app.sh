#!/bin/bash

# --- CONFIGURATION ---
# IMPORTANT: Put your exact project path here
PROJECT_DIR="~/workspace/myproject"
# ---------------------

# 1. Stop on errors
set -e

# 2. Go to the project directory
cd "$PROJECT_DIR"

# 3. Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 4. Activate venv
source venv/bin/activate

# 5. Install/Update dependencies silently
# This ensures any new libraries needed are added automatically
echo "Checking requirements..."
pip install -r requirements.txt -q

# 6. Run the main script
# If you need port 80 (HTTP) or system access, this script will inherit sudo
echo "🚀 Starting App..."
python main.py