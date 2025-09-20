from celery import shared_task
import requests
from datetime import datetime

@shared_task
def generate_crm_report():
    url = "http://localhost:8000/graphql"
    query = """
    query {
        allCustomers {
            totalCount
        }
        allOrders {
            totalCount
        }
    }
    """
    try:
        response = requests.post(url, json={'query': query})
        data = response.json()

        # Extract data
        customers = data['data']['allCustomers']['totalCount']
        orders = data['data']['allOrders']['totalCount']
        
        # Calculate total revenue from orders
        revenue_query = """
        query {
            allOrders {
                edges {
                    node {
                        totalAmount
                    }
                }
            }
        }
        """
        revenue_response = requests.post(url, json={'query': revenue_query})
        revenue_data = revenue_response.json()
        
        total_revenue = 0
        for edge in revenue_data['data']['allOrders']['edges']:
            total_revenue += float(edge['node']['totalAmount'])

        log_file = "/tmp/crm_report_log.txt"
        with open(log_file, "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Report: "
                    f"{customers} customers, {orders} orders, {total_revenue} revenue\n")
    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error: {str(e)}\n")
