from rest_framework import serializers
from .models import MenuItem, Category, Rating
from decimal import Decimal
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
import bleach
from django.contrib.auth.models import User


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = Rating
        fields = ['user', 'menuitem_id', 'rating']
        validators = [
            UniqueTogetherValidator(
                queryset=Rating.objects.all(),
                fields=['user', 'menuitem_id']
            )
        ]
        extra_kwargs = {
            'rating': {'min_value': 0, 'max_value': 5},
        }


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    # change the name of the field 'inventory' in models to 'stock'
    stock = serializers.IntegerField(source='inventory')
    tax = serializers.SerializerMethodField(method_name='calculate_tax')
    price_after_tax = serializers.SerializerMethodField(method_name='calculate_price_after_tax')
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=2)
    title = serializers.CharField(
        max_length=255,
        validators=[UniqueValidator(queryset=MenuItem.objects.all())]
    )

    def validate(self, attrs):
        attrs['title'] = bleach.clean(attrs['title'])
        if(attrs['price']<2):
            raise serializers.ValidationError('Price should not be less than 2.0')
        if(attrs['inventory']<0):
            raise serializers.ValidationError('Stock cannot be negative')
        return super().validate(attrs)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'stock', 'tax', 'price_after_tax', 'category', 'category_id']
        extra_kwargs = {
            'price': {'min_value': 2},
            'inventory': {'min_value': 0}
        }

    def calculate_tax(self, product:MenuItem):
        return round(product.price * Decimal(0.1), 2)
    
    def calculate_price_after_tax(self, product:MenuItem):
        return product.price + self.calculate_tax(product)