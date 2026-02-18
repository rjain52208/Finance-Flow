#!/bin/bash
# Script to retrain the ML model after adding more data

cd /Users/riddhijain/Desktop/Financeflow/backend

echo "🤖 Retraining ML Model..."
echo ""

venv/bin/python manage.py shell << 'PYTHON_EOF'
from categorization.ml_categorizer import TransactionCategorizer
from transactions.models import Transaction
import pandas as pd

# Get all labeled transactions
transactions = Transaction.objects.filter(category__isnull=False).values('description', 'category__name')
df = pd.DataFrame(transactions)
df.rename(columns={'category__name': 'category'}, inplace=True)

print(f"📊 Training data: {len(df)} labeled transactions")
print(f"\nCategories: {df['category'].nunique()} unique")
print(df['category'].value_counts())

# Retrain
categorizer = TransactionCategorizer()
accuracy = categorizer.train(df)

print(f"\n✅ Model retrained with {accuracy*100:.1f}% accuracy!")
print("\nTest predictions:")

test_cases = [
    "scholarship",
    "rent",
    "Starbucks Coffee",
    "Walmart Groceries"
]

for desc in test_cases:
    category, confidence = categorizer.predict(desc, user=None)
    symbol = "✅" if confidence > 0.5 else "❌"
    print(f"  {symbol} '{desc}' → {category.name if category else 'None'} ({confidence*100:.1f}%)")
PYTHON_EOF

echo ""
echo "✅ Done! Auto-categorization should work better now."
