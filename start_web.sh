#!/bin/bash

# Start the CSV to Kotlin Converter Web Interface
echo "🚀 Starting CSV to Kotlin Converter Web Interface..."

# Activate virtual environment
source venv/bin/activate

# Start Flask server
echo "📱 Web interface will be available at: http://localhost:8080"
echo "🔄 Press Ctrl+C to stop the server"
echo ""

python app.py
