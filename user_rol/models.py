from django.db import models
from django.contrib.auth.models import User

class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = "Role"

    def __str__(self):
        return self.name
    
class UserRole(models.Model):
    userid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')
    rolid = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users')
    assigned_at = models.DateTimeField(auto_now_add=True)  

    class Meta:
        db_table = "UserRole"

    def __str__(self):
        return f'{self.userid.first_name} {self.rolid.name}'