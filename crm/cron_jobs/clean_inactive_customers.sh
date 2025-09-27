#!/bin/bash
# Script to delete customers with no orders since a year ago
# Logs the number of deleted customers with a timestamp

# Activate your virtual environment if needed
# source /path/to/your/venv/bin/activate

# Get the timestamp
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

# Run Django shell command to delete inactive customers
deleted_count=$(python manage.py shell -c "
from datetime import datetime, timedelta
from crm.models import Customer, Order

one_year_ago = datetime.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(order__isnull=True) | Customer.objects.filter(order__date__lt=one_year_ago)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log the result with timestamp
echo \"$timestamp: Deleted $deleted_count inactive customers\" >> /tmp/customer_cleanup_log.txt
