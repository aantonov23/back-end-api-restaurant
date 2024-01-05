from .models import MenuItem
from .serializer import MenuItemSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status


@api_view(['GET', 'POST'])
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        if category_name:
            items = items.filter(category__title=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__contains=search)
        if ordering:
            ordering_fields = ordering.split(',')
            items = items.order_by(*ordering_fields)
        serialized_items = MenuItemSerializer(items, many=True)
        return Response(serialized_items.data)
    elif request.method == 'POST':
        serialized_items = MenuItemSerializer(data=request.data)
        serialized_items.is_valid(raise_exception=True)
        serialized_items.save()
        return Response(serialized_items.validated_data, status.HTTP_201_CREATED)
    

@api_view()
def single_menu_item(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    serialized_item = MenuItemSerializer(item)
    return Response(serialized_item.data)


