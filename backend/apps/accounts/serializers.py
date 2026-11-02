from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, PatientProfile, ConsentRecord


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'is_active', 'email_verified_at', 'created_at']
        read_only_fields = ['id', 'is_active', 'email_verified_at', 'created_at']


class PatientProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            'id', 'email', 'full_name', 'origin_country_code',
            'preferred_language', 'display_currency',
            'phone_country_code', 'phone_number', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(required=False, allow_blank=True, default='')
    origin_country_code = serializers.CharField(required=False, allow_blank=True, default='')
    display_currency = serializers.CharField(required=False, default='USD', max_length=3)
    consent_accepted = serializers.BooleanField(required=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate_consent_accepted(self, value):
        if not value:
            raise serializers.ValidationError("Consent to data processing is required.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=User.Role.PATIENT
        )
        PatientProfile.objects.create(
            user=user,
            full_name=validated_data.get('full_name', ''),
            origin_country_code=validated_data.get('origin_country_code', ''),
            display_currency=validated_data.get('display_currency', 'USD')
        )
        ConsentRecord.objects.create(
            user=user,
            consent_type='PRIVACY_AND_DATA_PROCESSING',
            policy_version='1.0',
            source='REGISTRATION'
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("User account is inactive.")
        attrs['user'] = user
        return attrs

