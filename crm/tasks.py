from celery import shared_task
import requests
from datetime import datetime

@shared_task
def generate_crm_report():
    # GraphQL query to get CRM statistics
    query = """
    query {
        customers {
            totalCount
        }
        orders {
            totalCount
            edges {
                node {
                    totalAmount
                }
            }
        }
    }
    """
    
    try:
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': query},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            customer_count = data['data']['customers']['totalCount']
            order_count = data['data']['orders']['totalCount']
            
            # Calculate total revenue
            revenue = sum(
                float(order['node']['totalAmount']) 
                for order in data['data']['orders']['edges']
            )
            
            # Log the report
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open('/tmp/crm_report_log.txt', 'a') as f:
                f.write(f"{timestamp} - Report: {customer_count} customers, {order_count} orders, {revenue:.2f} revenue\n")
                
        else:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open('/tmp/crm_report_log.txt', 'a') as f:
                f.write(f"{timestamp} - Error: Failed to generate report (HTTP {response.status_code})\n")
                
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(f"{timestamp} - Exception: {str(e)}\n")
