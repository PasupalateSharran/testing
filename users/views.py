from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserRegistrationSerializer, UserProfileSerializer
from rest_framework import status
from django.contrib.auth.hashers import make_password
from datetime import date
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User
from django.conf import settings
from random import randint
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
import random




otp_storage = {}

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        email = data.get("email")

        if "otp" not in data:
            # Generate a random 6-digit OTP
            otp = str(randint(100000, 999999))
            otp_storage[email] = otp  # Store OTP in the dictionary

            # Send OTP to the given email
            send_mail(
                subject="Your OTP for Registration",
                message=f"Your OTP for registration is: {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)

        # Step 2: Verifying OTP
        elif "otp" in data:
            if email in otp_storage and otp_storage[email] == data["otp"]:
                serializer = UserRegistrationSerializer(data=data)
                if serializer.is_valid():
                    user = User.objects.create_user(
                        email=data['email'],
                        password=data['password'],
                        gender=data['gender'],
                        preferences=data['preferences'],
                        dob=data['dob']
                    )
                    otp_storage.pop(email, None)
                    return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(username=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "email": user.email
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
