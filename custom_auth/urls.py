from django.urls import path
from . import api

app_name = 'auth'

urlpatterns = [
    # Authentication endpoints
    path('generate-code/', api.GenerateVerificationCodeAPIView.as_view(), name='generate-code'),
    path('signup/', api.SignUpAPIView.as_view(), name='signup'),
    path('login/', api.LoginAPIView.as_view(), name='login'),
    path('change-password/', api.ChangePasswordView.as_view(), name='change-password'),
]