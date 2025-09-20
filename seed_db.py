#!/usr/bin/env python
"""
Database seeding script for the GraphQL CRM system.
Run this script to populate the database with sample data.
"""

import os
import sys
import django
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order


def seed_database():
    """Seed the database with sample data"""
    print("Starting database seeding...")
    
    # Clear existing data
    Order.objects.all().delete()
    Product.objects.all().delete()
    Customer.objects.all().delete()
    print("Cleared existing data")
    
    # Create customers
    customers_data = [
        {'name': 'Alice Johnson', 'email': 'alice@example.com', 'phone': '+1234567890'},
        {'name': 'Bob Smith', 'email': 'bob@example.com', 'phone': '123-456-7890'},
        {'name': 'Carol Davis', 'email': 'carol@example.com', 'phone': '+1987654321'},
        {'name': 'David Wilson', 'email': 'david@example.com', 'phone': '555-123-4567'},
        {'name': 'Eva Brown', 'email': 'eva@example.com', 'phone': '+1555123456'},
    ]
    
    customers = []
    for customer_data in customers_data:
        customer = Customer.objects.create(**customer_data)
        customers.append(customer)
        print(f"Created customer: {customer.name}")
    
    # Create products
    products_data = [
        {'name': 'Laptop', 'price': Decimal('999.99'), 'stock': 10},
        {'name': 'Mouse', 'price': Decimal('29.99'), 'stock': 50},
        {'name': 'Keyboard', 'price': Decimal('79.99'), 'stock': 25},
        {'name': 'Monitor', 'price': Decimal('299.99'), 'stock': 15},
        {'name': 'Headphones', 'price': Decimal('149.99'), 'stock': 30},
        {'name': 'Webcam', 'price': Decimal('89.99'), 'stock': 20},
        {'name': 'Tablet', 'price': Decimal('399.99'), 'stock': 8},
        {'name': 'Smartphone', 'price': Decimal('699.99'), 'stock': 12},
    ]
    
    products = []
    for product_data in products_data:
        product = Product.objects.create(**product_data)
        products.append(product)
        print(f"Created product: {product.name}")
    
    # Create orders
    orders_data = [
        {
            'customer': customers[0],  # Alice
            'products': [products[0], products[1], products[2]],  # Laptop, Mouse, Keyboard
            'total_amount': Decimal('1109.97')
        },
        {
            'customer': customers[1],  # Bob
            'products': [products[3], products[4]],  # Monitor, Headphones
            'total_amount': Decimal('449.98')
        },
        {
            'customer': customers[2],  # Carol
            'products': [products[5], products[6]],  # Webcam, Tablet
            'total_amount': Decimal('489.98')
        },
        {
            'customer': customers[3],  # David
            'products': [products[7]],  # Smartphone
            'total_amount': Decimal('699.99')
        },
        {
            'customer': customers[4],  # Eva
            'products': [products[0], products[3], products[4]],  # Laptop, Monitor, Headphones
            'total_amount': Decimal('1449.97')
        },
    ]
    
    for order_data in orders_data:
        products_list = order_data.pop('products')
        order = Order.objects.create(**order_data)
        order.products.set(products_list)
        print(f"Created order: {order}")
    
    print(f"\nDatabase seeding completed!")
    print(f"Created {len(customers)} customers")
    print(f"Created {len(products)} products")
    print(f"Created {len(orders_data)} orders")


if __name__ == '__main__':
    seed_database()
