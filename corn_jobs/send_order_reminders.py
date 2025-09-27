#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime, timedelta
import requests
import json

# Add Django project to path
sys.path.append('/path/to/alx-backend-graphql_crm')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.utils import timezone

def send_order_reminders():
    # GraphQL query
    query = """
    query {
        orders(orderDate_Gte: "%s") {
            edges {
                node {
                    id
                    customer {
                        email
                    }
                    orderDate
                }
            }
        }
    }
    """ % (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Make GraphQL request
    response = requests.post(
        'http://localhost:8000/graphql',
        json={'query': query},
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        orders = data.get('data', {}).get('orders', {}).get('edges', [])
        
        # Log results
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('/tmp/order_reminders_log.txt', 'a') as f:
            f.write(f"[{timestamp}] Order reminders:\n")
            for order in orders:
                order_data = order['node']
                f.write(f"Order ID: {order_data['id']}, Customer Email: {order_data['customer']['email']}\n")
        
        print("Order reminders processed!")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    send_order_reminders()
