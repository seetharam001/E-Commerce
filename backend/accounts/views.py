from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token  # Import Token model

from .serializers import RegisterSerializer, LoginSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Create or get token for the user
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "message": "Login successful",
            "username": user.username,
            "email": user.email,
            "token": token.key  # Return token in response
        }, status=status.HTTP_200_OK)
