from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import datetime

def log_crm_heartbeat():
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive\n"

    # Append to log file
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(log_message)

        # Optional: check GraphQL hello field
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql("{ hello }")
        try:
            result = client.execute(query)
            f.write(f"{timestamp} GraphQL endpoint response: {result}\n")
        except Exception as e:
            f.write(f"{timestamp} GraphQL endpoint error: {e}\n")


def update_low_stock():
    """
    Executes the UpdateLowStockProducts mutation via GraphQL
    and logs updated products to /tmp/low_stock_updates_log.txt
    """
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_file = "/tmp/low_stock_updates_log.txt"

    # GraphQL client
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Mutation
    mutation = gql("""
    mutation {
      updateLowStockProducts {
        message
        updatedProducts {
          name
          stock
        }
      }
    }
    """)

    try:
        result = client.execute(mutation)
        updated = result["updateLowStockProducts"]["updatedProducts"]

        with open(log_file, "a") as f:
            if updated:
                for prod in updated:
                    f.write(f"{timestamp}: Product {prod['name']} new stock {prod['stock']}\n")
            else:
                f.write(f"{timestamp}: No low-stock products found\n")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp}: Error updating low-stock products: {e}\n")
