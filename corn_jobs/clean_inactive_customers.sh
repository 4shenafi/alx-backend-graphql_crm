#!/bin/bash

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Change to Django project directory
cd /path/to/alx-backend-graphql_crm

# Execute Django shell command to delete inactive customers
DELETED_COUNT=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders in the past year
inactive_customers = Customer.objects.filter(
    order__isnull=True
).distinct() | Customer.objects.filter(
    order__order_date__lt=one_year_ago
).distinct()

count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log the result
echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt
