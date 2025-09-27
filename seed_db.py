#!/usr/bin/env python
"""
Seed database with sample data for testing GraphQL mutations
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from models import Customer, Product, Order

def seed_database():
    """Seed the database with sample data"""
    print("Seeding database...")
    
    # Clear existing data
    Order.objects.all().delete()
    Product.objects.all().delete()
    Customer.objects.all().delete()
    
    # Create sample customers
    customers = [
        Customer(name="Alice Johnson", email="alice@example.com", phone="+1234567890"),
        Customer(name="Bob Smith", email="bob@example.com", phone="123-456-7890"),
        Customer(name="Carol Davis", email="carol@example.com", phone="+1-555-123-4567"),
        Customer(name="David Wilson", email="david@example.com"),
    ]
    
    for customer in customers:
        customer.save()
        print(f"Created customer: {customer.name}")
    
    # Create sample products
    products = [
        Product(name="Laptop", price=999.99, stock=10),
        Product(name="Mouse", price=29.99, stock=50),
        Product(name="Keyboard", price=79.99, stock=25),
        Product(name="Monitor", price=299.99, stock=15),
        Product(name="Headphones", price=149.99, stock=30),
    ]
    
    for product in products:
        product.save()
        print(f"Created product: {product.name} - ${product.price}")
    
    # Create sample orders
    alice = Customer.objects.get(name="Alice Johnson")
    bob = Customer.objects.get(name="Bob Smith")
    
    laptop = Product.objects.get(name="Laptop")
    mouse = Product.objects.get(name="Mouse")
    keyboard = Product.objects.get(name="Keyboard")
    monitor = Product.objects.get(name="Monitor")
    
    # Order 1: Alice buys laptop and mouse
    order1 = Order.objects.create(customer=alice, total_amount=1029.98)
    order1.products.set([laptop, mouse])
    print(f"Created order: {order1}")
    
    # Order 2: Bob buys keyboard and monitor
    order2 = Order.objects.create(customer=bob, total_amount=379.98)
    order2.products.set([keyboard, monitor])
    print(f"Created order: {order2}")
    
    print("\nDatabase seeded successfully!")
    print(f"Created {Customer.objects.count()} customers")
    print(f"Created {Product.objects.count()} products")
    print(f"Created {Order.objects.count()} orders")

if __name__ == "__main__":
    seed_database()
