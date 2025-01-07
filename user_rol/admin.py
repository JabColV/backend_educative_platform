from django.contrib import admin
from .models import UserRole, Role

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'status']

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['userid', 'rolid', 'assigned_at']