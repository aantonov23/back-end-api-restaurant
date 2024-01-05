from django.urls import path
from . import views

urlpatterns = [
    path('menu-items', views.menu_items),
    path('menu-items/<int:pk>', views.single_menu_item),
    # path('category/<int:pk>',views.SingleMenuItemView.as_view(), name='category-detail'),
]
