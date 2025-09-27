import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re
from .models import Customer, Product, Order

# Type Definitions
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

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
    success = graphene.Boolean()

class BulkCustomerResponse(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    success_count = graphene.Int()
    error_count = graphene.Int()

class ProductResponse(graphene.ObjectType):
    product = graphene.Field(ProductType)
    message = graphene.String()
    success = graphene.Boolean()

class OrderResponse(graphene.ObjectType):
    order = graphene.Field(OrderType)
    message = graphene.String()
    success = graphene.Boolean()

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    Output = CustomerResponse

    @staticmethod
    def validate_phone(phone):
        if phone and not re.match(r'^(\+\d{1,15}|\d{3}-\d{3}-\d{4})$', phone):
            raise ValidationError("Invalid phone format. Use +1234567890 or 123-456-7890")

    def mutate(self, info, input):
        try:
            validate_email(input.email)
            self.validate_phone(input.phone)
            
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            customer.full_clean()
            customer.save()
            
            return CustomerResponse(
                customer=customer,
                message="Customer created successfully",
                success=True
            )
        except ValidationError as e:
            return CustomerResponse(
                customer=None,
                message=str(e),
                success=False
            )
        except Exception as e:
            return CustomerResponse(
                customer=None,
                message=f"Error creating customer: {str(e)}",
                success=False
            )

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(CustomerInput, required=True)

    Output = BulkCustomerResponse

    def mutate(self, info, inputs):
        customers = []
        errors = []
        
        with transaction.atomic():
            for idx, input in enumerate(inputs):
                try:
                    validate_email(input.email)
                    CreateCustomer.validate_phone(input.phone)
                    
                    customer = Customer(
                        name=input.name,
                        email=input.email,
                        phone=input.phone
                    )
                    customer.full_clean()
                    customer.save()
                    customers.append(customer)
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")
        
        return BulkCustomerResponse(
            customers=customers,
            errors=errors,
            success_count=len(customers),
            error_count=len(errors)
        )

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    Output = ProductResponse

    def mutate(self, info, input):
        try:
            if input.price <= 0:
                raise ValidationError("Price must be greater than 0")
            
            if hasattr(input, 'stock') and input.stock < 0:
                raise ValidationError("Stock cannot be negative")
            
            product = Product(
                name=input.name,
                price=input.price,
                stock=getattr(input, 'stock', 0)
            )
            product.full_clean()
            product.save()
            
            return ProductResponse(
                product=product,
                message="Product created successfully",
                success=True
            )
        except Exception as e:
            return ProductResponse(
                product=None,
                message=f"Error creating product: {str(e)}",
                success=False
            )

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    Output = OrderResponse

    def mutate(self, info, input):
        try:
            if not input.product_ids:
                raise ValidationError("At least one product is required")
            
            try:
                customer = Customer.objects.get(pk=input.customer_id)
            except Customer.DoesNotExist:
                raise ValidationError(f"Customer with ID {input.customer_id} does not exist")
            
            products = []
            invalid_ids = []
            
            for product_id in input.product_ids:
                try:
                    product = Product.objects.get(pk=product_id)
                    products.append(product)
                except Product.DoesNotExist:
                    invalid_ids.append(product_id)
            
            if invalid_ids:
                raise ValidationError(f"Invalid product IDs: {', '.join(invalid_ids)}")
            
            total_amount = sum(product.price for product in products)
            
            order = Order(
                customer=customer,
                total_amount=total_amount
            )
            order.save()
            order.products.set(products)
            
            return OrderResponse(
                order=order,
                message="Order created successfully",
                success=True
            )
        except Exception as e:
            return OrderResponse(
                order=None,
                message=str(e),
                success=False
            )

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    success = graphene.Boolean()

    @staticmethod
    def validate_phone(phone):
        if phone and not re.match(r'^(\+\d{1,15}|\d{3}-\d{3}-\d{4})$', phone):
            raise ValidationError("Invalid phone format. Use +1234567890 or 123-456-7890")

    def mutate(self, info, input):
        try:
            validate_email(input.email)
            self.validate_phone(input.phone)
            
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            customer.full_clean()
            customer.save()
            
            return CreateCustomer(
                customer=customer,
                message="Customer created successfully",
                success=True
            )
        except ValidationError as e:
            return CreateCustomer(
                customer=None,
                message=str(e),
                success=False
            )
        except Exception as e:
            return CreateCustomer(
                customer=None,
                message=str(e),
                success=False
            )

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    success_count = graphene.Int()
    error_count = graphene.Int()

    def mutate(self, info, inputs):
        customers = []
        errors = []
        
        with transaction.atomic():
            for input in inputs:
                try:
                    validate_email(input.email)
                    CreateCustomer.validate_phone(input.phone)
                    
                    customer = Customer(
                        name=input.name,
                        email=input.email,
                        phone=input.phone
                    )
                    customer.full_clean()
                    customer.save()
                    customers.append(customer)
                except Exception as e:
                    errors.append(f"Failed to create customer {input.name}: {str(e)}")
        
        return BulkCreateCustomers(
            customers=customers,
            errors=errors,
            success_count=len(customers),
            error_count=len(errors)
        )

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    message = graphene.String()
    success = graphene.Boolean()

    def mutate(self, info, input):
        try:
            if input.price <= 0:
                raise ValidationError("Price must be positive")
            
            if hasattr(input, 'stock') and input.stock < 0:
                raise ValidationError("Stock cannot be negative")
            
            product = Product(
                name=input.name,
                price=input.price,
                stock=getattr(input, 'stock', 0)
            )
            product.full_clean()
            product.save()
            
            return CreateProduct(
                product=product,
                message="Product created successfully",
                success=True
            )
        except Exception as e:
            return CreateProduct(
                product=None,
                message=str(e),
                success=False
            )

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    message = graphene.String()
    success = graphene.Boolean()

    def mutate(self, info, input):
        try:
            if not input.product_ids:
                raise ValidationError("At least one product is required")
            
            customer = Customer.objects.get(pk=input.customer_id)
            products = Product.objects.filter(pk__in=input.product_ids)
            
            if len(products) != len(input.product_ids):
                found_ids = {str(p.id) for p in products}
                missing_ids = [pid for pid in input.product_ids if pid not in found_ids]
                raise ValidationError(f"Invalid product IDs: {', '.join(missing_ids)}")
            
            total_amount = sum(product.price for product in products)
            
            order = Order(
                customer=customer,
                total_amount=total_amount
            )
            order.save()
            order.products.set(products)
            
            return CreateOrder(
                order=order,
                message="Order created successfully",
                success=True
            )
        except Customer.DoesNotExist:
            return CreateOrder(
                order=None,
                message="Customer not found",
                success=False
            )
        except Exception as e:
            return CreateOrder(
                order=None,
                message=str(e),
                success=False
            )

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
