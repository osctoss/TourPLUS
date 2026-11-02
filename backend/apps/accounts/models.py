import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role='PATIENT', **extra_fields):
        if not email:
            raise ValueError('An email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        PATIENT = 'PATIENT', 'Patient'
        ADMIN = 'ADMIN', 'Administrator'
        DATA_CURATOR = 'DATA_CURATOR', 'Data Curator'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255, db_index=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.email} ({self.role})"


class PatientProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    full_name = models.CharField(max_length=255, blank=True)
    origin_country_code = models.CharField(max_length=3, blank=True, help_text="ISO 3166-1 alpha-2/3 code")
    preferred_language = models.CharField(max_length=10, default='en')
    display_currency = models.CharField(max_length=3, default='USD')
    phone_country_code = models.CharField(max_length=5, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patient_profiles'
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'

    def __str__(self):
        return f"Profile of {self.user.email} ({self.full_name or 'Unnamed'})"


class ConsentRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consent_records')
    consent_type = models.CharField(max_length=50, help_text="e.g. PRIVACY_POLICY, DATA_PROCESSING, AI_TERMS")
    policy_version = models.CharField(max_length=20)
    accepted_at = models.DateTimeField(default=timezone.now)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=50, default='WEB_APP')

    class Meta:
        db_table = 'consent_records'
        verbose_name = 'Consent Record'
        verbose_name_plural = 'Consent Records'

    def __str__(self):
        return f"{self.user.email} - {self.consent_type} ({self.policy_version})"

