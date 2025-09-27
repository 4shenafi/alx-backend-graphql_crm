import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.core.exceptions import ValidationError
from models import Customer, Product, Order
import re

# Object Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

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
class CreateCustomerResponse(graphene.ObjectType):
    customer = graphene.Field(CustomerType)
    message = graphene.String()

class BulkCreateCustomersResponse(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

class CreateProductResponse(graphene.ObjectType):
    product = graphene.Field(ProductType)

class CreateOrderResponse(graphene.ObjectType):
    order = graphene.Field(OrderType)

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)
    
    Output = CreateCustomerResponse
    
    def mutate(self, info, input):
        try:
            # Validate email uniqueness
            if Customer.objects.filter(email=input.email).exists():
                raise ValidationError("Email already exists")
            
            # Validate phone format if provided
            if input.phone:
                phone_pattern = r'^(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
                if not re.match(phone_pattern, input.phone):
                    raise ValidationError("Invalid phone format. Use formats like +1234567890 or 123-456-7890")
            
            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            
            return CreateCustomerResponse(
                customer=customer,
                message="Customer created successfully"
            )
            
        except ValidationError as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise ValidationError(f"Error creating customer: {str(e)}")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = BulkCustomerInput(required=True)
    
    Output = BulkCreateCustomersResponse
    
    def mutate(self, info, input):
        customers = []
        errors = []
        
        with transaction.atomic():
            for i, customer_data in enumerate(input.customers):
                try:
                    # Validate email uniqueness
                    if Customer.objects.filter(email=customer_data.email).exists():
                        errors.append(f"Customer {i+1}: Email already exists")
                        continue
                    
                    # Validate phone format if provided
                    if customer_data.phone:
                        phone_pattern = r'^(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
                        if not re.match(phone_pattern, customer_data.phone):
                            errors.append(f"Customer {i+1}: Invalid phone format")
                            continue
                    
                    customer = Customer.objects.create(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.phone
                    )
                    customers.append(customer)
                    
                except Exception as e:
                    errors.append(f"Customer {i+1}: {str(e)}")
        
        return BulkCreateCustomersResponse(
            customers=customers,
            errors=errors
        )

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)
    
    Output = CreateProductResponse
    
    def mutate(self, info, input):
        try:
            # Validate price is positive
            if input.price <= 0:
                raise ValidationError("Price must be positive")
            
            # Validate stock is not negative
            stock = input.stock if input.stock is not None else 0
            if stock < 0:
                raise ValidationError("Stock cannot be negative")
            
            product = Product.objects.create(
                name=input.name,
                price=input.price,
                stock=stock
            )
            
            return CreateProductResponse(product=product)
            
        except ValidationError as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise ValidationError(f"Error creating product: {str(e)}")

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)
    
    Output = CreateOrderResponse
    
    def mutate(self, info, input):
        try:
            # Validate customer exists
            try:
                customer = Customer.objects.get(id=input.customer_id)
            except Customer.DoesNotExist:
                raise ValidationError("Invalid customer ID")
            
            # Validate products exist
            if not input.product_ids:
                raise ValidationError("At least one product must be selected")
            
            products = []
            total_amount = 0
            
            for product_id in input.product_ids:
                try:
                    product = Product.objects.get(id=product_id)
                    products.append(product)
                    total_amount += product.price
                except Product.DoesNotExist:
                    raise ValidationError(f"Invalid product ID: {product_id}")
            
            # Create order
            order = Order.objects.create(
                customer=customer,
                total_amount=total_amount
            )
            
            # Add products to order
            order.products.set(products)
            
            return CreateOrderResponse(order=order)
            
        except ValidationError as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise ValidationError(f"Error creating order: {str(e)}")

# Query class
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)
    
    def resolve_customers(self, info):
        return Customer.objects.all()
    
    def resolve_products(self, info):
        return Product.objects.all()
    
    def resolve_orders(self, info):
        return Order.objects.all()

# Mutation class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
