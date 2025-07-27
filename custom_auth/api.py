# views.py
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_secure_token.models import Token
from .models import ApplicationUser
from .serializers import SignUpSerializer, LoginSerializer, ApplicationUserReadSerializer , ChangePasswordSerializer, ApplicationUserUpdateSerializer
from .utils import generate_4_digit_code


class GenerateVerificationCodeAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = generate_4_digit_code()
        return Response({"verification_code": code}, status=status.HTTP_200_OK)


class SignUpAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully.",
                "user_id": str(user.uuid)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Handle token creation
            token, created = Token.objects.get_or_create(user=user)

            user_data = ApplicationUserReadSerializer(user).data

            return Response({
                "message": "Login successful.",
                "token": token.key,
                "user": user_data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Delete the token to force re-authentication next time
        Token.objects.filter(user=user).delete()

        return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)


class UserListAPIView(ListAPIView):
    queryset = ApplicationUser.objects.all()
    serializer_class = ApplicationUserReadSerializer
    permission_classes = [IsAuthenticated]


class UserDetailAPIView(RetrieveAPIView):
    queryset = ApplicationUser.objects.all()
    serializer_class = ApplicationUserReadSerializer
    lookup_field = 'uuid'  # Make sure this matches your URL pattern
    permission_classes = [IsAuthenticated]

class UserUpdateAPIView(UpdateAPIView):
    queryset = ApplicationUser.objects.all()
    serializer_class = ApplicationUserUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'  # or use 'pk' if you want to use primary key

    def get_object(self):
        # Option 1: Allow users to update themselves only
        return self.request.user

        # Option 2: Allow admin to update any user
        # uuid = self.kwargs.get("uuid")
        # return get_object_or_404(ApplicationUser, uuid=uuid)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

