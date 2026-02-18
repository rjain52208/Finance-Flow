# Quick Start Guide

Get FinanceFlow up and running in minutes!

## Prerequisites

Make sure you have these installed:
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

## Quick Setup (5 minutes)

### 1. Clone & Setup Database

```bash
# Create PostgreSQL database
psql postgres -c "CREATE DATABASE financeflow_db;"
psql postgres -c "CREATE USER financeflow_user WITH PASSWORD 'password123';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE financeflow_db TO financeflow_user;"
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
python manage.py migrate

# Create categories and train ML model
python manage.py train_categorizer --create-categories

# Create admin user
python manage.py createsuperuser

# Start Redis (in a new terminal)
redis-server

# Start Celery worker (in a new terminal)
celery -A financeflow worker --loglevel=info

# Start Celery beat (in a new terminal)
celery -A financeflow beat --loglevel=info

# Start Django server
python manage.py runserver
```

Backend running at: `http://localhost:8000` ✅

### 3. Frontend Setup

```bash
# Navigate to frontend (in a new terminal)
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

Frontend running at: `http://localhost:3000` ✅

## First Steps

1. **Register an Account**
   - Go to `http://localhost:3000/register`
   - Create your account

2. **Add Your First Transaction**
   - Click "Add Transaction"
   - Enter details
   - Watch it auto-categorize! 🎯

3. **Create a Budget**
   - Go to "Budgets"
   - Set spending limits
   - Get alerts when approaching limits

4. **View Analytics**
   - Check your dashboard
   - Explore spending patterns
   - View monthly trends

## Sample Data (Optional)

Want to test with sample data? Create a CSV file:

**transactions.csv:**
```csv
date,amount,type,description
2024-10-01,50.00,expense,Starbucks Coffee
2024-10-02,120.00,expense,Whole Foods Groceries
2024-10-03,3500.00,income,Salary Payment
2024-10-04,60.00,expense,Shell Gas Station
2024-10-05,25.00,expense,Netflix Subscription
```

Upload via "Bulk Upload" in Transactions page.

## Docker Setup (Alternative)

Coming soon! Docker compose file for one-command setup.

## Troubleshooting

**Port already in use?**
```bash
# Backend
python manage.py runserver 8001

# Frontend
npm run dev -- --port 3001
```

**Database connection error?**
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify credentials in `.env`

**Redis error?**
- Start Redis: `redis-server`
- Or use Docker: `docker run -d -p 6379:6379 redis`

## What's Next?

- 📖 Read the [Architecture Overview](ARCHITECTURE.md)
- 🔧 Detailed [Backend Setup](backend/SETUP.md)
- 🎨 Detailed [Frontend Setup](frontend/SETUP.md)

## Need Help?

- Check [Common Issues](#troubleshooting)
- Review setup guides
- Open an issue on GitHub

---

**Congratulations!** 🎉 You're now running FinanceFlow!
