#!/usr/bin/env python3
import sys
import logging
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Setup logging
log_file = "/tmp/order_reminders_log.txt"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def main():
    # GraphQL endpoint
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=False,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Calculate cutoff date (7 days ago)
    cutoff_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")

    # GraphQL query for recent orders
    query = gql(
        """
        query GetRecentOrders {
          allOrders {
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
        """
    )

    # Execute query
    try:
        result = client.execute(query)

        orders = result.get("allOrders", {}).get("edges", [])
        if not orders:
            logging.info("No recent orders found.")
        else:
            for order_edge in orders:
                order = order_edge["node"]
                order_id = order["id"]
                customer_email = order["customer"]["email"]
                order_date = order["orderDate"]
                
                # Check if order is within last 7 days
                order_datetime = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
                if order_datetime >= datetime.now() - timedelta(days=7):
                    logging.info(f"Reminder for Order #{order_id} - Customer: {customer_email}")

        print("Order reminders processed!")

    except Exception as e:
        logging.error(f"Error fetching orders: {e}")
        print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

