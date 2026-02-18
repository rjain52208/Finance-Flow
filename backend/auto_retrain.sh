#!/bin/bash

# Auto-retrain ML model with all user-categorized transactions
# This script should be run periodically (daily/weekly) via cron

cd "$(dirname "$0")"

echo "==========================================​==============="
echo "Auto-Retraining ML Model with User Data"
echo "========================================================​="

# Activate virtual environment
source venv/bin/activate

# Run the training command
python manage.py train_categorizer

echo ""
echo "✅ Model retrained successfully!"
echo "The model now learns from all manually categorized transactions."
echo "========================================================​="
