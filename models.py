from django.db import models
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
import re

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def clean(self):
        # Validate phone format
        if self.phone:
            phone_pattern = r'^(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
            if not re.match(phone_pattern, self.phone):
                raise ValidationError('Invalid phone format. Use formats like +1234567890 or 123-456-7890')

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def clean(self):
        if self.price <= 0:
            raise ValidationError('Price must be positive')
        if self.stock < 0:
            raise ValidationError('Stock cannot be negative')

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.customer.name}"
    
    def calculate_total(self):
        return sum(product.price for product in self.products.all())
    
    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)
