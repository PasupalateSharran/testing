from rest_framework import serializers
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .models import User
from django.contrib.auth import authenticate
import random
from datetime import date
from django.utils.html import strip_tags

SUPERHERO_NAMES = [
    "IronMan", "SpiderMan", "CaptainAmerica", "Thor", "Hulk", "BlackPanther",
    "DoctorStrange", "Wolverine", "Deadpool", "BlackWidow", "Hawkeye",
    "Superman", "Batman", "WonderWoman", "Flash", "GreenLantern", "Aquaman",
    "Cyborg", "Shazam", "GreenArrow", "AntMan", "StarLord", "Groot"
]

class UserProfileSerializer(serializers.ModelSerializer):
    superhero_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['email', 'gender', 'preferences', 'dob', 'superhero_name']

    def get_superhero_name(self, obj):
        return random.choice(SUPERHERO_NAMES)
    

class UserRegistrationSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'gender', 'preferences', 'dob', 'otp']
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True}
        }

    def validate(self, data):
        if 'password' in data and 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError("Passwords do not match.")
        dob = data.get('dob')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                raise serializers.ValidationError("You must be at least 18 years old to register.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)  
        validated_data.pop('otp', None) 

        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password) 
        user.save()
        return user

#password reset
User = get_user_model()

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user is associated with this email address.")
        return value

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Construct the reset URL
        reset_url = f"http://localhost:8000/api/users/reset/{uid}/{token}/"

        # Send email
        send_mail(
            subject="Password Reset Request",
            message=strip_tags(render_to_string("password_reset_email.html")),
            from_email="sharran1594@gmail.com",
            recipient_list=[email],
            html_message=render_to_string("password_reset_email.html", {"reset_url": reset_url}),
            fail_silently=False,
        )

