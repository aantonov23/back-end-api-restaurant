from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items', views.MenuItemsViewSet.as_view({'get':'list', 'post':'create'})),
    path('menu-items/<int:pk>', views.MenuItemsViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'})),
    path('category',views.CategoriesView.as_view()),
    path('secret', views.secret),
    path('api-token-auth', obtain_auth_token),
    path('manager-view', views.manager_view),
    path('groups/manager/users', views.managers),
    path('groups/manager/users/<int:pk>', views.manager_detail),
    path('groups/delivery-crew/users', views.delivery_crew),
    path('groups/delivery-crew/users/<int:pk>', views.delivery_crew_detail),
    path('cart', views.cart),
    path('orders', views.orders_view),
    path('orders/<int:pk>', views.order_detail),
    # path('cart', views.CartViewSet.as_view({'get':'list', 'post':'create', 'delete':'destroy'})),
    # path('orders', views.order),
    # path('orders/<int:pk>', views.order_item),


    path('groups', views.groups),
    path('users_list/', views.users_list),
    path('ratings', views.RatingView.as_view()),
    # path('throttle-check', views.throttle_check),
    # path('throttle-check-auth', views.throttle_check_auth),
]

