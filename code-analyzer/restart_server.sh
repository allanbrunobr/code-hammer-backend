#!/bin/bash

echo "Stopping running server..."
pkill -f "python -m code-analyzer.local" || true

echo "Starting server..."
cd /Users/bruno/Desktop/GenAI\ -\ projects/code-analyzer
python -m code-analyzer.local &

echo "Server restarted!"
