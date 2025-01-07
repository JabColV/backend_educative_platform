from django.urls import path
from . import views

urlpatterns = [
    path('access_token/', views.Login.as_view(), name='token_access'),
    path('token/refresh/', views.GenerateNewToken.as_view(), name='token_refresh'),
    path('logout/', views.Logout, name='logout'),
]