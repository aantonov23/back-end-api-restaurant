from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items', views.MenuItemsViewSet.as_view({'get':'list'})),
    path('menu-items/<int:pk>', views.MenuItemsViewSet.as_view({'get':'retrieve'})),
    path('category',views.CategoriesView.as_view()),
    path('secret', views.secret),
    path('api-token-auth', obtain_auth_token),
    path('manager-view', views.manager_view),
    path('group/manager/users', views.managers),
    path('ratings', views.RatingView.as_view()),
    # path('throttle-check', views.throttle_check),
    # path('throttle-check-auth', views.throttle_check_auth),
]
