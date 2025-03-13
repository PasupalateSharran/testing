from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer, LoginSerializer
from rest_framework import status
from django.contrib.auth.hashers import make_password
from datetime import date
from django.contrib.auth import authenticate


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        if data['password'] != data['confirm_password']:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        dob = data.get('dob')
        if not dob:
            return Response({"error": "Date of birth is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        dob = date.fromisoformat(dob) 
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            return Response({"error": "You must be at least 18 years old to register"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            username=data['email'],
            email=data['email'],
            password=make_password(data['password']),
            gender=data['gender'],
            preferences=data['preferences'],
            dob=dob 
        )
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    
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
                "username": user.username,
                "email": user.email
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)