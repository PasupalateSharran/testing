from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserRegistrationSerializer, UserProfileSerializer, PasswordResetSerializer
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
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django_ratelimit.decorators import ratelimit
from django.template.loader import render_to_string
from django.utils.html import strip_tags
# from rest_framework.decorators import api_view
# from ipware import get_client_ip
import random




# otp_storage = {}

# class RegisterView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         data = request.data
#         email = data.get("email")

#         if "otp" not in data:
#             otp = str(randint(100000, 999999))
#             otp_storage[email] = otp 

#             send_mail(
#                 subject="Your OTP for Registration",
#                 message=f"Your OTP for registration is: {otp}",
#                 from_email=settings.EMAIL_HOST_USER,
#                 recipient_list=[email],
#                 fail_silently=False,
#             )
#             return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)

#         elif "otp" in data:
#             if email in otp_storage and otp_storage[email] == data["otp"]:
#                 serializer = UserRegistrationSerializer(data=data)
#                 if serializer.is_valid():
#                     user = User.objects.create_user(
#                         email=data['email'],
#                         password=data['password'],
#                         gender=data['gender'],
#                         preferences=data['preferences'],
#                         dob=data['dob']
#                     )
#                     otp_storage.pop(email, None)
#                     return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#             return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
#         return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

otp_storage = {}

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        email = data.get("email")
        otp = data.get("otp")

        # Step 1: Check if OTP is provided
        if not otp:
            # Use the serializer to validate the data before sending OTP
            serializer = UserRegistrationSerializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Generate OTP and store it
            otp = str(randint(100000, 999999))
            otp_storage[email] = otp

            # Send OTP to the email
            send_mail(
                subject="Your OTP for Registration",
                message=f"Your OTP for registration is: {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)

        # Step 2: Verify OTP and register the user
        if email in otp_storage and otp_storage[email] == otp:
            serializer = UserRegistrationSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                # Remove OTP after successful registration
                otp_storage.pop(email, None)
                return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

    
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
    


User = get_user_model()
class PasswordResetRequestView(APIView):
    # @ratelimit(key='ip', rate='3/m', block=True)
    def post(self, request):
        # ip, _ = get_client_ip(request)
        # print(f"Password reset requested from IP: {ip}")
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset link sent!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid or expired link."}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = PasswordResetTokenGenerator()

        if not token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get("password")
        if not new_password:
            return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        html_message = render_to_string('password_reset_confirmation.html')
        plain_message = strip_tags(html_message)
        send_mail(
            subject="Your Password Has Been Reset",
            message=plain_message,
            html_message=html_message,
            from_email="sharran1594@gmail.com",
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({"message": "Password reset successful!"}, status=status.HTTP_200_OK)
