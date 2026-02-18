#!/bin/bash
# Quick Start Script for FinanceFlow Demo

echo "🚀 Starting FinanceFlow Demo Setup..."
echo ""

# Navigate to backend
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies (this may take a minute)..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << EOF
DEBUG=True
SECRET_KEY=demo-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
FRONTEND_URL=http://localhost:3000
EOF
fi

# Run migrations
echo "🗄️  Setting up database..."
python manage.py migrate --noinput

# Create default categories and train ML model
echo "🤖 Setting up categories and training ML model..."
python manage.py train_categorizer --create-categories

# Create superuser non-interactively
echo "👤 Creating demo admin user..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@demo.com', 'admin123')" | python manage.py shell

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "📝 Demo credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "🌐 Starting Django server on http://localhost:8000"
echo ""

# Start Django server
python manage.py runserver
