# CRM Celery Setup

This project uses **Celery + Celery Beat** with Redis for scheduling background jobs.

## Setup Instructions

### 1. Install Redis and Dependencies
```bash
# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Start Celery Worker
```bash
celery -A crm worker -l info
```

### 4. Start Celery Beat
```bash
celery -A crm beat -l info
```

### 5. Verify Logs
Check the generated reports in `/tmp/crm_report_log.txt` for weekly CRM reports.
