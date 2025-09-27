import os
import django
from django.db import transaction
from faker import Faker
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

fake = Faker()

def create_customers(count=10):
    """Generate fake customers with unique emails"""
    customers = []
    for _ in range(count):
        email = fake.unique.email()
        phone = None
        if fake.boolean(chance_of_getting_true=70):  # 70% chance of having phone
            phone = f"+1{fake.msisdn()[3:]}" if fake.boolean() else fake.phone_number()
        
        customer = Customer(
            name=fake.name(),
            email=email,
            phone=phone
        )
        customers.append(customer)
    
    Customer.objects.bulk_create(customers)
    return customers

def create_products(count=15):
    """Generate fake products with realistic prices"""
    product_names = [
        "Laptop", "Smartphone", "Headphones", "Monitor", "Keyboard",
        "Mouse", "Tablet", "Smartwatch", "Printer", "Router",
        "External HDD", "USB Drive", "Webcam", "Microphone", "Speaker"
    ]
    
    products = []
    for name in product_names[:count]:
        product = Product(
            name=name,
            price=Decimal(fake.pydecimal(left_digits=3, right_digits=2, positive=True)),
            stock=fake.random_int(min=0, max=100)
        )
        products.append(product)
    
    Product.objects.bulk_create(products)
    return products

def create_orders(customers, products, count=20):
    """Generate orders with random products"""
    for _ in range(count):
        customer = fake.random_element(customers)
        order_products = fake.random_elements(
            elements=products,
            length=fake.random_int(min=1, max=5),
            unique=True
        )
        
        total = sum(p.price for p in order_products)
        order = Order.objects.create(
            customer=customer,
            total_amount=total
        )
        order.products.set(order_products)

@transaction.atomic
def seed_database():
    print("Deleting old data...")
    Order.objects.all().delete()
    Customer.objects.all().delete()
    Product.objects.all().delete()
    
    print("Creating customers...")
    customers = create_customers()
    
    print("Creating products...")
    products = create_products()
    
    print("Creating orders...")
    create_orders(customers, products)
    
    print(f"""
    Database seeded successfully!
    - Customers: {len(customers)}
    - Products: {len(products)}
    - Orders: {Order.objects.count()}
    """)

if __name__ == '__main__':
    seed_database()
