from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.contrib.auth import login, logout
from .models import PatientProfile
from .serializers import (
    UserSerializer,
    PatientProfileSerializer,
    RegisterSerializer,
    LoginSerializer
)


class RegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response({
                'message': 'Registration successful.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                'message': 'Login successful.',
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully.'})


class CurrentUserView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'patient_profile', None)
        profile_data = PatientProfileSerializer(profile).data if profile else None
        return Response({
            'user': UserSerializer(request.user).data,
            'profile': profile_data
        })


class ProfileUpdateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        profile, _ = PatientProfile.objects.get_or_create(user=request.user)
        serializer = PatientProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DemoLoginView(views.APIView):
    """
    Seamless 1-click authentication for demo and testing users.
    Ensures a valid demo patient account exists, authenticates session, and returns user profile.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user, created = User.objects.get_or_create(
            email='patient@tourplus.ai',
            defaults={
                'role': 'PATIENT',
                'is_active': True,
            }
        )
        if created or not user.has_usable_password():
            user.set_password('TourPlus2026!')
            user.save()

        PatientProfile.objects.get_or_create(
            user=user,
            defaults={
                'full_name': 'John Doe (Demo Patient)',
                'origin_country_code': 'US',
                'display_currency': 'USD',
            }
        )
        login(request, user)
        return Response({
            'message': 'Demo patient authentication successful.',
            'user': UserSerializer(user).data
        })

