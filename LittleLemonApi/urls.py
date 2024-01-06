from django.urls import path
from . import views

urlpatterns = [
    path('menu-items', views.MenuItemsViewSet.as_view({'get': 'list'})),
    path('menu-items/<int:pk>', views.MenuItemsViewSet.as_view({'get': 'retrieve'})),
    # path('category/<int:pk>',views.SingleMenuItemView.as_view(), name='category-detail'),
]
