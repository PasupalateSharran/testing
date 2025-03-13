# from django.contrib.auth.models import AbstractUser
# from django.db import models

# class User(AbstractUser):
#     gender = models.CharField(max_length=10)
#     preferences = models.CharField(max_length=100, blank=True)
#     dob = models.DateField(null=True, blank=True)
    
#     class Meta:
#         verbose_name = 'user'
#         verbose_name_plural = 'users'

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10)
    preferences = models.CharField(max_length=100)
    dob = models.DateField(default="2000-01-01")
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
