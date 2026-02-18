# Backend Setup Guide

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 14+
- Redis 6+
- pip (Python package manager)

## Step-by-Step Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
```

### 2. Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

**Option A: Using psql command line**

```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE financeflow_db;
CREATE USER financeflow_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE financeflow_db TO financeflow_user;

# Grant schema permissions
\c financeflow_db
GRANT ALL ON SCHEMA public TO financeflow_user;

# Exit
\q
```

**Option B: Using pgAdmin**

1. Open pgAdmin
2. Right-click "Databases" → Create → Database
3. Name: `financeflow_db`
4. Right-click "Login/Group Roles" → Create → Login/Group Role
5. Name: `financeflow_user`, set password
6. Grant privileges to the user

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file with your settings:

```env
DEBUG=True
SECRET_KEY=your-very-secret-key-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Update with your PostgreSQL credentials
DATABASE_URL=postgresql://financeflow_user:your_password@localhost:5432/financeflow_db

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Configuration (for Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

FRONTEND_URL=http://localhost:3000
```

**Note for Gmail:** You need to create an [App Password](https://support.google.com/accounts/answer/185833) instead of using your regular password.

### 6. Run Database Migrations

```bash
python manage.py migrate
```

This will:
- Create all necessary database tables
- Enable Row-Level Security (RLS) in PostgreSQL
- Set up indexes for performance

### 7. Create Default Categories & Train ML Model

```bash
python manage.py train_categorizer --create-categories
```

This command will:
- Create 18 default system categories
- Train the TF-IDF categorization model
- Save the model for auto-categorization

### 8. Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 9. Collect Static Files (for production)

```bash
python manage.py collectstatic
```

### 10. Start Redis Server

**On macOS (with Homebrew):**
```bash
brew services start redis
```

**On Linux:**
```bash
sudo systemctl start redis
```

**On Windows:**
Download and run Redis from [https://redis.io/download](https://redis.io/download)

Or use Docker:
```bash
docker run -d -p 6379:6379 redis:latest
```

### 11. Start Celery Workers (in separate terminals)

**Terminal 1: Start Celery Worker**
```bash
cd backend
source venv/bin/activate  # Activate virtual environment
celery -A financeflow worker --loglevel=info
```

**Terminal 2: Start Celery Beat (Scheduler)**
```bash
cd backend
source venv/bin/activate
celery -A financeflow beat --loglevel=info
```

### 12. Run Development Server

```bash
python manage.py runserver
```

The API will be available at: `http://localhost:8000`

Admin panel: `http://localhost:8000/admin`

## Testing the Setup

### Test API Endpoints

```bash
# Check if API is running
curl http://localhost:8000/api/

# Test registration
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123"
  }'
```

### Test Celery Tasks

In Django shell:
```bash
python manage.py shell
```

```python
from tasks.tasks import send_daily_budget_summary
result = send_daily_budget_summary.delay()
print(result.status)
```

## Common Issues & Solutions

### Issue 1: Database Connection Error

**Error:** `could not connect to server`

**Solution:**
- Ensure PostgreSQL is running: `sudo systemctl status postgresql`
- Check your `DATABASE_URL` in `.env`
- Verify user has correct permissions

### Issue 2: Redis Connection Error

**Error:** `Error connecting to Redis`

**Solution:**
- Ensure Redis is running: `redis-cli ping` (should return "PONG")
- Check `REDIS_URL` in `.env`

### Issue 3: Import Errors

**Error:** `ModuleNotFoundError`

**Solution:**
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

### Issue 4: Migration Errors

**Error:** `relation already exists`

**Solution:**
```bash
python manage.py migrate --fake-initial
```

### Issue 5: Celery Not Picking Up Tasks

**Solution:**
- Restart Celery worker and beat
- Check Redis connection
- Verify `CELERY_BROKER_URL` in settings

## Production Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Change `SECRET_KEY` to a strong random key
- [ ] Set proper `ALLOWED_HOSTS`
- [ ] Use production database (not SQLite)
- [ ] Configure proper email backend
- [ ] Set up SSL/TLS certificates
- [ ] Use environment variables for sensitive data
- [ ] Set up proper logging
- [ ] Configure CORS properly
- [ ] Use process manager (Supervisor, systemd) for Celery
- [ ] Set up database backups
- [ ] Configure monitoring (Sentry, etc.)

## Useful Commands

```bash
# Create new Django app
python manage.py startapp app_name

# Make migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Django shell
python manage.py shell

# Check for issues
python manage.py check

# Show SQL for migration
python manage.py sqlmigrate app_name migration_name

# Retrain categorizer model
python manage.py train_categorizer
```

## Next Steps

1. Proceed to [Frontend Setup Guide](../frontend/SETUP.md)
2. Read [API Documentation](API.md)
3. Review [Architecture Overview](ARCHITECTURE.md)
