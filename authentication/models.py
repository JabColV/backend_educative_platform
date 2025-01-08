from datetime import timezone
from django.db import models
from django.contrib.auth.models import User

# class User(AbstractUser):
#     name = models.CharField(max_length=255)
#     lastname = models.CharField(max_length=255)
#     birth_date = models.DateField(null=True, blank=True)
#     phonenumber = models.CharField(max_length=15, null=True, blank=True) 
#     address = models.CharField(max_length=500, null=True, blank=True)  
#     # created_at = models.DateTimeField(auto_now_add=True)  
#     # username = models.CharField(max_length=255, unique=True)
#     # email = models.CharField(max_length=255)
#     # password = models.CharField(max_length=255)
#     # last_login = models.DateTimeField(null=True, blank=True)  
#     # is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return f'{self.name} {self.lastname}' 


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField()
    class Meta:
        managed = True
        db_table = 'PasswordResetToken'

    def __str__(self):
        return f"Token for {self.user.email}"
