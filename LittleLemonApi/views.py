from rest_framework.response import Response
from rest_framework import viewsets
from .models import MenuItem, Category, Rating
from .serializer import MenuItemSerializer, CategorySerializer, RatingSerializer
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework import status

class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemsViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

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

    

@api_view(['POST', 'DELETE'])
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name='Manager')
        if request.method == "POST":
            managers.user_set.add(user)
            message =  f"{username} is now a manager"
        elif request.method == 'DELETE':
            managers.user_set.remove(user)
            message = f"{username} is no longer a manager"
        return Response({'message': message})
    
    return Response({'message': "error. username not provided"}, status.HTTP_400_BAD_REQUEST)

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

