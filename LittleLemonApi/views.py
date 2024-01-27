from rest_framework.response import Response
from rest_framework import viewsets
from .models import MenuItem, Category, Rating, Cart, Order, OrderItem
from .serializer import MenuItemSerializer, CategorySerializer, RatingSerializer, GroupSerializer, UserSerializer
from .serializer import CartSerializer, OrderSerializer, OrderItemSerializer, AddCartSerializer
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
    

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def cart(request):
    carts = Cart.objects.filter(user=request.user)

    if request.method == 'GET':
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        try:
            quantity = request.data['quantity']
        except:
            quantity = 1

        try:
            menuitem_id = request.data['menuitem_id']
        except:
            return Response({'message': "menuitem_id not provided"}, status.HTTP_400_BAD_REQUEST)
        
        menuitem = get_object_or_404(MenuItem, id=menuitem_id)
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
            serializer = CartSerializer(cart, data=request.data)

            if not serializer.is_valid():
                return Response({'message': f"{serializer.errors}"}, status.HTTP_400_BAD_REQUEST)
            # serializer.is_valid()
            serializer.save()
            return Response({'message': f"Cart for {user} created, serializer.data: {serializer.data}"}, status.HTTP_201_CREATED)
        else:
            cart = cart.first()
            cart.quantity += int(quantity)
            cart.price = cart.quantity * cart.unit_price
            cart.save()
            serializer = CartSerializer(cart)
            return Response({'message': f"cart has been updated, new data: {serializer.data}"}, status.HTTP_200_OK)


# class CartViewSet(viewsets.ModelViewSet):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated,]
#     lookup_field = 'pk'
    
    # def create(self, request, *args, **kwargs):
    #     try:
    #         menuitem_id = request.data['menuitem_id']
    #     except:
    #         return Response({'message': "menueitem_id are not provided"}, status.HTTP_400_BAD_REQUEST)
  
    
    # def get_serializer_class(self):
    #     if self.request.method == 'POST':
    #         print("\nPoint 3\n")
    #         return CartSerializer #AddCartSerializer
    #     print("\nPoint 31\n")
    #     return CartSerializer



# @api_view(['POST', 'GET', 'DELETE'])
# @permission_classes([IsAuthenticated])
# def cart(request):
#     if request.method == 'POST':
#         try:
#             menueitem_id = request.data['menuitem_id']
#             quantity = request.data['quantity']
#         except:
#             return Response({'message': "menueitem_id or quantity are not provided"}, status.HTTP_400_BAD_REQUEST)
        
#         menuitem = MenuItem.objects.get(id=menueitem_id)
#         user = request.user
#         cart = Cart.objects.filter(user=user, menuitem=menuitem)
#         if not cart.exists():
#             cart = Cart.objects.create(
#                 user=user, menuitem=menuitem, quantity=quantity , unit_price=menuitem.price, price=menuitem.price*int(quantity)
#             )
#             serializer = CartSerializer(cart, data=request.data)

#             if not serializer.is_valid():
#                 return Response({'message': f"WTF! {serializer.errors}"}, status.HTTP_400_BAD_REQUEST)
#             serializer.is_valid()
#             serializer.save()
#             return Response({'message': f"Cart for {user} created, serializer.data: {serializer.data}"}, status.HTTP_201_CREATED)
#         else:
#             cart = cart.first()
#             cart.quantity += int(quantity)
#             cart.price = cart.quantity * cart.unit_price
#             cart.save()
#             serializer = CartSerializer(cart)
#             return Response({'message': f"cart has been updated, new data: {serializer.data}"}, status.HTTP_200_OK)
        
#     elif request.method == 'GET':
#         user = request.user
#         cart = Cart.objects.filter(user=user)
#         serializer = CartSerializer(cart, many=True)
#         return Response(serializer.data, status.HTTP_200_OK)
    
#     elif request.method == 'DELETE':
#         user = request.user
#         cart = Cart.objects.filter(user=user)
#         cart.delete()
#         return Response({'message': f"cart for {user} has been deleted"}, status.HTTP_200_OK)


# @api_view(['POST', 'GET'])
# @permission_classes([IsAuthenticated])
# def order(request):
#     if request.method == 'POST':
#         user = request.user
#         cart = Cart.objects.filter(user=user)
#         if not cart.exists():
#             return Response({'message': f"cart for {user} is empty"}, status.HTTP_400_BAD_REQUEST)
#         else:
#             order = Order.objects.create(user=user, total=0, date=timezone.now())
#             total = 0
#             for item in cart:
#                 OrderItem.objects.create(order=order, menuitem=item.menuitem, quantity=item.quantity, unit_price=item.unit_price, price=item.price)
#                 total += item.price
#             order.total = total
#             order.save()
#             cart.delete()
#             return Response({'message': f"order for {user} has been created"}, status.HTTP_201_CREATED)
    
#     elif request.method == 'GET':
#         user = request.user
#         if user.groups.filter(name='Manager').exists():
#             return Response(OrderSerializer(Order.objects.all(), many=True).data, status.HTTP_200_OK)
#         elif user.groups.filter(name='Delivery crew').exists():
#             return Response(OrderSerializer(Order.objects.filter(delivery_crew=user), many=True).data, status.HTTP_200_OK)
#         else:
#             orders = Order.objects.filter(user=user)
#             serializer = OrderSerializer(orders, many=True)
#             return Response(serializer.data, status.HTTP_200_OK)


# @api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
# @permission_classes([IsAuthenticated])
# def order_item(request, pk):
#     if request.method == 'GET':
#         order = get_object_or_404(Order, pk=pk)
#         serializer = OrderSerializer(order)
#         return Response(serializer.data, status.HTTP_200_OK)
            
        


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
def managers_detail(request, pk):
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

