from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'),
    path('token/refresh/', views.GenerateNewToken.as_view(), name='token_refresh'),
    path('logout/', views.Logout, name='logout'),
]