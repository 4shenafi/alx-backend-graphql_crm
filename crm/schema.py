import graphene
from graphene_django.types import DjangoObjectType
from .models import Product

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass
    
    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(graphene.String)
    
    def mutate(self, info):
        # Find products with low stock
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []
        
        for product in low_stock_products:
            product.stock += 10  # Restock by 10
            product.save()
            updated_products.append(f"{product.name}: {product.stock}")
        
        return UpdateLowStockProducts(
            success=True,
            message=f"Updated {len(updated_products)} products",
            updated_products=updated_products
        )

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

# Add to existing schema
