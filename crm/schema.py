import graphene
from graphene_django import DjangoObjectType, DjangoFilterConnectionField
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
from django.core.exceptions import ValidationError
import re
from decimal import Decimal
from datetime import datetime

from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filter_fields = []
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filter_fields = []
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filter_fields = []
        interfaces = (graphene.relay.Node,)


# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class BulkCustomerInput(graphene.InputObjectType):
    customers = graphene.List(CustomerInput, required=True)


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


# Response Types
class CustomerResponse(graphene.ObjectType):
    customer = graphene.Field(CustomerType)
    message = graphene.String()


class BulkCustomerResponse(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)


class ProductResponse(graphene.ObjectType):
    product = graphene.Field(ProductType)


class OrderResponse(graphene.ObjectType):
    order = graphene.Field(OrderType)


# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    Output = CustomerResponse

    def mutate(self, info, input):
        # Validate email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            raise ValidationError("Email already exists")

        # Validate phone format if provided
        if input.phone:
            phone_pattern = r'^(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
            if not re.match(phone_pattern, input.phone):
                raise ValidationError("Invalid phone format. Use format like +1234567890 or 123-456-7890")

        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone
        )

        return CustomerResponse(
            customer=customer,
            message="Customer created successfully"
        )


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = BulkCustomerInput(required=True)

    Output = BulkCustomerResponse

    def mutate(self, info, input):
        customers = []
        errors = []

        with transaction.atomic():
            for customer_data in input.customers:
                try:
                    # Validate email uniqueness
                    if Customer.objects.filter(email=customer_data.email).exists():
                        errors.append(f"Email {customer_data.email} already exists")
                        continue

                    # Validate phone format if provided
                    if customer_data.phone:
                        phone_pattern = r'^(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
                        if not re.match(phone_pattern, customer_data.phone):
                            errors.append(f"Invalid phone format for {customer_data.email}")
                            continue

                    customer = Customer.objects.create(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.phone
                    )
                    customers.append(customer)

                except Exception as e:
                    errors.append(f"Error creating customer {customer_data.email}: {str(e)}")

        return BulkCustomerResponse(
            customers=customers,
            errors=errors
        )


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    Output = ProductResponse

    def mutate(self, info, input):
        # Validate price is positive
        if input.price <= 0:
            raise ValidationError("Price must be positive")

        # Validate stock is non-negative
        stock = input.stock if input.stock is not None else 0
        if stock < 0:
            raise ValidationError("Stock cannot be negative")

        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=stock
        )

        return ProductResponse(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    Output = OrderResponse

    def mutate(self, info, input):
        # Validate customer exists
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Invalid customer ID")

        # Validate products exist and at least one product is provided
        if not input.product_ids:
            raise ValidationError("At least one product must be selected")

        try:
            products = Product.objects.filter(id__in=input.product_ids)
            if len(products) != len(input.product_ids):
                raise ValidationError("One or more product IDs are invalid")
        except Exception:
            raise ValidationError("Invalid product IDs")

        # Calculate total amount
        total_amount = sum(product.price for product in products)

        # Create order
        order_date = input.order_date if input.order_date else datetime.now()
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=order_date
        )

        # Add products to order
        order.products.set(products)

        return OrderResponse(order=order)


# Queries
class Query(graphene.ObjectType):
    hello = graphene.String()
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    def resolve_hello(self, info):
        return "Hello, GraphQL!"

    def resolve_all_customers(self, info, **kwargs):
        return Customer.objects.all()

    def resolve_all_products(self, info, **kwargs):
        return Product.objects.all()

    def resolve_all_orders(self, info, **kwargs):
        return Order.objects.all()


# Mutations
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
