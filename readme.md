User Registration

    URL: /api/users/register/
    Method: POST
    Description: Registers a new user with email and OTP verification.
    Request Body:

{
"email": "user@example.com",
"password": "password123",
"confirm_password": "password123",
"gender": "Male",
"preferences": "Chatting, Gaming",
"dob": "2000-05-15"
}

Response (OTP sent):

{
"message": "OTP sent to your email"
}

Request Body (OTP Confirmation):

{
"email": "user@example.com",
"otp": "123456",
"password": "password123",
"confirm_password": "password123",
"gender": "Male",
"preferences": "Chatting, Gaming",
"dob": "2000-05-15"
}

Response (Successful Registration):

    {
        "message": "User registered successfully"
    }

User Login

    URL: /api/users/login/
    Method: POST
    Description: Authenticates a user and returns JWT tokens.
    Request Body:

{
"email": "user@example.com",
"password": "password123"
}

Response:

    {
        "access": "your_access_token",
        "refresh": "your_refresh_token"
    }

User Profile

    URL: /api/users/profile/
    Method: GET

Headers:

Authorization: Bearer <your_access_token>

Description: Retrieves the authenticated user's profile.
Response:

    {
        "email": "user@example.com",
        "gender": "Male",
        "preferences": "Chatting, Gaming",
        "dob": "2000-05-15",
        "superhero_name": "deadpool"
    }

Password Reset Request

    URL: /api/users/reset-password/
    Method: POST
    Description: Sends a password reset link to the user's email.
    Request Body:

{
"email": "user@example.com"
}

Response:

    {
        "message": "Password reset link sent to your email"
    }

Password Reset Confirmation

    URL: /api/users/reset/<uidb64>/<token>/
    Method: POST
    Description: Confirms the password reset and updates the password.
    Request Body:

{
"new_password": "new_password123",
"confirm_password": "new_password123"
}

Response:

    {
        "message": "Password reset successful"
    }

Token Refresh

    URL: /api/token/refresh/
    Method: POST
    Description: Refreshes the access token.
    Request Body:

{
"refresh": "your_refresh_token"
}

Response:

{
"access": "new_access_token"
}
