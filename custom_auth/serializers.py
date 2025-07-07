# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from .models import ApplicationUser
import re


class SignUpSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    verification_code = serializers.CharField(write_only=True)

    class Meta:
        model = ApplicationUser
        fields = ('email', 'username', 'password', 'confirm_password', 'verification_code')
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False, 'max_length': 254},
            'username': {'required': True, 'allow_blank': False, 'max_length': 150},
            'password': {'write_only': True}
        }

    def validate_password(self, password):
        if not (8 <= len(password) <= 15):
            raise serializers.ValidationError("Password must be between 8 and 15 characters.")

        if re.search(r'\s', password):
            raise serializers.ValidationError("Password must not contain spaces.")

        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError("Password must contain at least 1 uppercase letter.")

        if not re.search(r'[a-z]', password):
            raise serializers.ValidationError("Password must contain at least 1 lowercase letter.")

        if not re.search(r'[0-9]', password):
            raise serializers.ValidationError("Password must contain at least 1 number.")

        if re.search(r'[^a-zA-Z0-9]', password):
            raise serializers.ValidationError("Password must not contain special characters.")

        return password

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        if attrs['username'].lower() in attrs['password'].lower():
            raise serializers.ValidationError("Password cannot be the same as username.")

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data.pop('verification_code')

        password = validated_data.pop('password')
        user = ApplicationUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ApplicationUserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationUser
        # Include only the fields you want in the response (excluding password, OTP, etc.)
        exclude = ('password', )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    verification_code = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            print(user)
            if not user:
                raise serializers.ValidationError("Invalid username or password.")

            if not user.is_active:
                raise serializers.ValidationError("User account is inactive.")
        else:
            raise serializers.ValidationError("Username and password are required.")

        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, data):
        user = self.context['request'].user
        new_password = data['new_password']
        confirm_password = data['confirm_password']

        if new_password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        # Password length
        if not (8 <= len(new_password) <= 15):
            raise serializers.ValidationError({"new_password": "Password must be 8 to 15 characters long."})

        # No whitespace
        if " " in new_password:
            raise serializers.ValidationError({"new_password": "Password must not contain spaces."})

        # Must be alphanumeric only (no special characters)
        if not new_password.isalnum():
            raise serializers.ValidationError({"new_password": "Password must contain only alphanumeric characters."})

        # At least 1 capital letter, 1 lowercase, 1 digit
        if not re.search(r"[A-Z]", new_password):
            raise serializers.ValidationError({"new_password": "Password must contain at least one uppercase letter."})
        if not re.search(r"[a-z]", new_password):
            raise serializers.ValidationError({"new_password": "Password must contain at least one lowercase letter."})
        if not re.search(r"[0-9]", new_password):
            raise serializers.ValidationError({"new_password": "Password must contain at least one digit."})

        # Must not be same as username or nickname
        if new_password.lower() == user.username.lower() or new_password.lower() == user.nickname.lower():
            raise serializers.ValidationError({"new_password": "Password must not be the same as username or nickname."})

        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

