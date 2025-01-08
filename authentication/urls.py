from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.Register.as_view(), name='register'),
    path('reset_password_request/', views.PasswordResetRequest.as_view(), name='reset_password'),
    path("password_reset_validate/<str:token>/", views.PasswordResetTokenValidation.as_view(), name='password_reset_validate'),
    path("password_reset_completed/", views.PasswordResetTokenCompleted.as_view(), name='password_reset_completed'),
    path('login/', views.Login.as_view(), name='login'),
    path('token/refresh/', views.GenerateNewToken.as_view(), name='token_refresh'),
    path('logout/', views.Logout, name='logout'),
]