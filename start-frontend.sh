#!/bin/bash
# Frontend Startup Script

echo "🎨 Starting FinanceFlow Frontend..."
echo ""

cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node dependencies (this may take a minute)..."
    npm install
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    echo "VITE_API_URL=http://localhost:8000/api" > .env
fi

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "🌐 Starting React app on http://localhost:3000"
echo ""

# Start development server
npm run dev
