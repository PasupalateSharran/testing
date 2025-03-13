from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    gender = models.CharField(max_length=10)
    preferences = models.CharField(max_length=100, blank=True)
    dob = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
