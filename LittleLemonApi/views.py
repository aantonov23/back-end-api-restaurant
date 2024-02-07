from rest_framework.response import Response
from rest_framework import viewsets
from .models import MenuItem, Category, Rating, Cart, Order, OrderItem
from .serializer import (
    MenuItemSerializer, CategorySerializer, RatingSerializer, 
    GroupSerializer, UserSerializer, CartSerializer, 
    OrderSerializer, OrderItemSerializer, 
)
from .permissions import IsManagerOrReadOnly
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.contrib.auth.models import User, Group, Permission
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin
from datetime import date


class CategoriesView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemsViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'inventory']
    search_fields = ['title', 'category__title']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
          
        return [IsManagerOrReadOnly()]

    def get_throttles(self):
        if self.action == 'create':
            throttle_classes = [UserRateThrottle]
        else:
            throttle_classes = [] 
        return [throttle() for throttle in throttle_classes]

    
class RatingView(generics.ListCreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsAuthenticated()]
    

@api_view(['POST', 'GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart(request):
    carts = Cart.objects.filter(user=request.user)

    if request.method == 'DELETE':
        carts.delete()
        return Response(status.HTTP_200_OK)
        
    if request.method == 'GET':
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        try:
            quantity = int(request.data['quantity'])
        except:
            quantity = 1
        assert (quantity >= 0), ("Quantity must be >= 0")
        try:
            menuitem = request.data['menuitem']
        except:
            return Response({'message': "menuitem_id not provided"}, status.HTTP_400_BAD_REQUEST)
        
        menuitem = get_object_or_404(MenuItem, id=menuitem)
        user = request.user
        unit_price = menuitem.price
        cart = Cart.objects.filter(user=user, menuitem=menuitem)
        if not cart.exists():
            cart = Cart.objects.create(
                user=user, 
                menuitem=menuitem, 
                quantity=quantity, 
                unit_price=unit_price,
                price=menuitem.price*int(quantity)
            )

            data = {
                'menuitem': menuitem.id,
                'user': user.id, 
                'quantity': quantity, 
                'unit_price': unit_price,
                'price': menuitem.price*int(quantity)
            }
            
            serializer = CartSerializer(cart, data=data)

            if not serializer.is_valid():
                return Response({'message': serializer.errors}, status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({'message': f"Cart for {user} created, serializer.data: {serializer.data}"}, status.HTTP_201_CREATED)
        else:
            cart = cart.first()
            cart.quantity += int(quantity)
            cart.price = cart.quantity * cart.unit_price
            cart.save()
            serializer = CartSerializer(cart)
            return Response({'message': f"cart has been updated, new data: {serializer.data}"}, status.HTTP_200_OK)


@api_view(['POST', 'DELETE', 'GET'])
@permission_classes([IsAuthenticated])
def orders_view(request):
    user = request.user
    
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=user)
        
        user = user.id 
        total = cart.price 
        _date = date.today()
        order_data = {
                    'user': user, 
                    'total': total, 
                    'date': _date
                }
        order_serializer = OrderSerializer(data=order_data)
        order_serializer.is_valid(raise_exception=True)
        order_serializer.save()
        order = order_serializer.data

        order_items_data = {
                    'order': order['id'], 
                    'menuitem': cart.menuitem.id, 
                    'quantity': cart.quantity,
                    'unit_price': cart.unit_price,
                    'price': total,
                    'user': user,
                    'total': total,
                    'date': _date
                }
        order_items_serializer = OrderItemSerializer(data=order_items_data)
        order_items_serializer.is_valid(raise_exception=True)
        order_items_serializer.save()
        cart.delete()
        return Response({'message': f"Order for {user} created. "}, status.HTTP_201_CREATED)

    if request.method == 'GET':
        if user.groups.filter(name='Manager').exists():
            orders = Order.objects.all()
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
        elif user.groups.filter(name='Delivery crew').exists():
            orders = Order.objects.filter(delivery_crew=user)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            orders = OrderItem.objects.filter(order__user=user)
            serializer = OrderItemSerializer(orders, many=True)
            return Response(serializer.data, status.HTTP_200_OK)


@api_view(['PUT', 'PATCH', 'DELETE', 'GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, pk):
    user = request.user
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'DELETE' and user.groups.filter(name='Manager').exists():
        order.delete()
        return Response(status.HTTP_204_NO_CONTENT)
    elif request.method == 'DELETE' and not user.groups.filter(name='Manager').exists():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'GET':
        if user.groups.filter(name='Manager').exists():
            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data, status.HTTP_200_OK)
        elif user.groups.filter(name='Delivery crew').exists() and order.delivery_crew == user:
            serializer = OrderSerializer(order)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            if order.user != user:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            order_items = OrderItem.objects.get(order=order)
            serializer = OrderItemSerializer(order_items)
            return Response(serializer.data, status.HTTP_200_OK)
        
    elif request.method in ['PUT', 'PATCH']:
        data = request.data
        if user.groups.filter(name='Manager').exists():
            serializer = OrderSerializer(order, data=data, partial=True, many=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        elif user.groups.filter(name='Delivery crew').exists() and order.delivery_crew == user:
            data_keys = list(data.keys())
            if not data_keys[0] == 'status' or len(data_keys) > 1:
                return Response({'message': "Must change only 'Status'"})
            serializer = OrderSerializer(order, data=data, partial=True, many=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            order_items = OrderItem.objects.get(order=order, order__user=user)
            serializer = OrderItemSerializer(order_items, data=data, partial=True, many=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
         

# List all groups
@api_view(['GET'])
@permission_classes([IsManagerOrReadOnly])
def groups(request):
    groups = Group.objects.all()
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data)


# List all users
@api_view(['GET'])
@permission_classes([IsManagerOrReadOnly])
def users_list(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
    

# List and ADD Managers
@api_view(['GET', 'POST'])
@permission_classes([IsManagerOrReadOnly])
def managers(request):
    managers = Group.objects.get(name='Manager')

    if request.method == 'GET':
        serializer = UserSerializer(managers.user_set.all(), many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        try:
            username = request.data['username']
        except:
            return Response({'message': "username not provided"}, status.HTTP_400_BAD_REQUEST)
        else:
            user = get_object_or_404(User, username=username)
            managers.user_set.add(user)
            message =  f"{username} is now a manager"
            return Response({'message': message}, status.HTTP_201_CREATED)
    

# Remove Manager
@api_view(['DELETE'])
@permission_classes([IsManagerOrReadOnly])
def manager_detail(request, pk):
    manager = Group.objects.get(name='Manager')
    user = get_object_or_404(User, pk=pk)
    manager.user_set.remove(user)
    message =  f"{user.username} is no longer a manager"
    return Response({'message': message}, status.HTTP_200_OK)


# List and ADD Delivery crew
@api_view(['GET', 'POST'])
@permission_classes([IsManagerOrReadOnly])
def delivery_crew(request):
    crew = Group.objects.get(name='Delivery crew')

    if request.method == 'GET':
        serializer = UserSerializer(crew.user_set.all(), many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        try:
            username = request.data['username']
        except:
            return Response({'message': "username not provided"}, status.HTTP_400_BAD_REQUEST)
        else:
            user = get_object_or_404(User, username=username)
            crew.user_set.add(user)
            message =  f"{username} is now a member of the delivery crew"
            return Response({'message': message}, status.HTTP_201_CREATED)


# Remove Delivery crew
@api_view(['DELETE'])
@permission_classes([IsManagerOrReadOnly])
def delivery_crew_detail(request, pk):
    crew = Group.objects.get(name='Delivery crew')
    user = get_object_or_404(User, pk=pk)
    crew.user_set.remove(user)
    message =  f"{user.username} is no longer a member of the delivery crew"
    return Response({'message': message}, status.HTTP_200_OK)


@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({'message': 'This is a secret message!'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_view(request):
    if request.user.groups.filter(name='Manager').exists():
        return Response({'message': 'This is a secret message for managers!'})
    else:
        return Response({'message': 'You are not authorized'})


# @api_view(['GET'])
# @throttle_classes([AnonRateThrottle])
# def throttle_check(request):
#     return Response({'message': 'Successfull'})

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @throttle_classes([TenCallsPerMinute])
# def throttle_check_auth(request):
#     return Response({'message': 'Successfull for authorized users only'})

# class MenuItemsViewSet(viewsets.ModelViewSet):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer
#     ordering_fields = ['price', 'inventory']
#     search_fields = ['title', 'category__title']

