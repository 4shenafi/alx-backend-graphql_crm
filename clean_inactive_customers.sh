#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Navigate to the project directory
cd "$PROJECT_DIR"

# Execute the Django command to delete inactive customers and log the results
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
OUTPUT=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order
from django.db.models import Max

# Calculate the date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders since a year ago
inactive_customers = Customer.objects.annotate(
    last_order_date=Max('order__order_date')
).filter(
    last_order_date__lt=one_year_ago
) | Customer.objects.filter(
    order__isnull=True
)

count = inactive_customers.count()
inactive_customers.delete()
print(f'Deleted {count} customers')
")

# Log the results
echo "[$TIMESTAMP] $OUTPUT" >> /tmp/customer_cleanup_log.txt
