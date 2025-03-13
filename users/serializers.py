from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
import random
from datetime import date

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

