def update_low_stock():
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Execute GraphQL mutation
    mutation = """
    mutation {
        updateLowStockProducts {
            success
            message
            updatedProducts
        }
    }
    """
    
    try:
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': mutation},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('data', {}).get('updateLowStockProducts', {})
            
            # Log results
            with open('/tmp/low_stock_updates_log.txt', 'a') as f:
                f.write(f"[{timestamp}] Low stock update:\n")
                f.write(f"Success: {result.get('success', False)}\n")
                f.write(f"Message: {result.get('message', 'No message')}\n")
                if result.get('updatedProducts'):
                    for product in result['updatedProducts']:
                        f.write(f"Updated: {product}\n")
        else:
            with open('/tmp/low_stock_updates_log.txt', 'a') as f:
                f.write(f"[{timestamp}] Error: HTTP {response.status_code}\n")
                
    except Exception as e:
        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
            f.write(f"[{timestamp}] Exception: {str(e)}\n")
