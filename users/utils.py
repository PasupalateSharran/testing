import random
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Generate a 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Send OTP to the user's email
def send_otp_email(email, otp):
    send_mail(
        subject="Your OTP for Registration",
        message=f"Your OTP for registration is: {otp}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )

def is_otp_valid(user):
    expiration_time = user.otp_created_at + timedelta(minutes=10)
    return timezone.now() <= expiration_time
