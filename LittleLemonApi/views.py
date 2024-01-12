from rest_framework.response import Response
from rest_framework import viewsets
from .models import MenuItem, Category, Rating
from .serializer import MenuItemSerializer, CategorySerializer, RatingSerializer, GroupSerializer, UserSerializer
from .permissions import IsManagerOrReadOnly
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny, DjangoModelPermissionsOrAnonReadOnly
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.contrib.auth.models import User, Group, Permission
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.exceptions import PermissionDenied

class CategoriesView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# class MenuItemsView(generics.ListCreateAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer
#     ordering_fields = ['price', 'inventory']
#     # filterset_fields = ['price', 'inventory'] # it is braking the code
#     search_fields = ['title', 'category__title']

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

@api_view(['GET'])
@permission_classes([IsManagerOrReadOnly])
def groups(request):
    groups = Group.objects.all()
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data)
    

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsManagerOrReadOnly])
def managers(request, pk=None):
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
        
    elif request.method == 'DELETE':
        if pk is None:
            return Response({'message': "user id not provided"}, status.HTTP_400_BAD_REQUEST)
        else:
            user = get_object_or_404(User, pk=pk)
            managers.user_set.remove(user)
            message =  f"{user.username} is no longer a manager"
            return Response({'message': message}, status.HTTP_200_OK)
        

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsManagerOrReadOnly])
def delivery_crew(request, pk=None):

    if request.method == 'GET':
        delivery_crew = Group.objects.get(name='Delivery crew')
        serializer = UserSerializer(delivery_crew.user_set.all(), many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        try:
            username = request.data['username']
        except:
            return Response({'message': "username not provided"}, status.HTTP_400_BAD_REQUEST)
        else:
            user = get_object_or_404(User, username=username)
            delivery_crew.user_set.add(user)
            message =  f"{username} is now a member of the delivery crew"
            return Response({'message': message}, status.HTTP_201_CREATED)
        
    elif request.method == 'DELETE':
        if pk is None:
            return Response({'message': "user id not provided"}, status.HTTP_400_BAD_REQUEST)
        else:
            user = get_object_or_404(User, pk=pk)
            delivery_crew.user_set.remove(user)
            message =  f"{user.username} is no longer a member of the delivery crew"
            return Response({'message': message}, status.HTTP_200_OK)

# class MenuItemsView(generics.ListCreateAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer
#     ordering_fields = ['price', 'inventory']
#     # filterset_fields = ['price', 'inventory'] # it is braking the code
#     search_fields = ['title', 'category__title']


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

