#!/bin/bash

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

echo "Virtual environment setup complete. To activate, run: source venv/bin/activate"
echo "To run the app locally, use: python src/main.py"