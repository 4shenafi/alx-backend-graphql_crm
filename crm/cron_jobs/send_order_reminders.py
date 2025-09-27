#!/usr/bin/env python3
"""
Script to query pending orders via GraphQL and log reminders.
"""

import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# GraphQL endpoint
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)
client = Client(transport=transport, fetch_schema_from_transport=True)

# GraphQL query for orders in the last 7 days
query = gql("""
query {
  orders(lastDays: 7) {
    id
    customer {
      email
    }
    orderDate
  }
}
""")

# Execute query
result = client.execute(query)

# Timestamp
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Log file
log_file = "/tmp/order_reminders_log.txt"

# Process orders and log
with open(log_file, "a") as f:
    for order in result.get("orders", []):
        order_id = order["id"]
        customer_email = order["customer"]["email"]
        log_line = f"{timestamp}: Order ID {order_id}, Customer {customer_email}\n"
        f.write(log_line)

print("Order reminders processed!")
