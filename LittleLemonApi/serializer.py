from rest_framework import serializers
from .models import MenuItem
from decimal import Decimal
from .models import Category


class MenuItemSerializer(serializers.ModelSerializer):
    # change the name of the field 'inventory' in models to 'stock'
    stock = serializers.IntegerField(source='inventory')
    tax = serializers.SerializerMethodField(method_name='calculate_tax')
    price_after_tax = serializers.SerializerMethodField(method_name='calculate_price_after_tax')

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'stock', 'tax', 'price_after_tax', 'category']
        depth = 1
        extra_kwargs = {
            'price': {'min_value': 2},
            'inventory': {'min_value': 0}
        }

    def calculate_tax(self, product:MenuItem):
        return round(product.price * Decimal(0.1), 2)
    
    def calculate_price_after_tax(self, product:MenuItem):
        return product.price + self.calculate_tax(product)