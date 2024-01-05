from django.urls import path
from . import views

urlpatterns = [
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('category/<int:pk>',views.SingleMenuItemView.as_view(), name='category-detail'),
    # path('raitings', views.RatingView.as_view()),
]
