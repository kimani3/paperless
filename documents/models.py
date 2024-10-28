# documents/models.py
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Department(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='departments_created'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nationalID = models.CharField(max_length=20, unique=True, null=True, blank=True)
    contact_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    profile_image = models.BinaryField()  # Binary field for profile image
    created_by = models.ForeignKey(  
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='profiles_created'
    )
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='users'
    )
    is_profile_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def completion_percentage(self):
        total_fields = 5  # Adjust this if more fields are added
        filled_fields = sum(1 for field in [self.nationalID, self.department, self.contact_number] if field)
        return (filled_fields / total_fields) * 100



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class VerificationCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()  # New field for expiration time

    def __str__(self):
        return f"Code {self.code} for {self.user.username}"

    def is_expired(self):
        return timezone.now() > self.expires_at
    

class Folder(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name='folders'
    )
    created_at = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='folders_created'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.department.name})"

    @property
    def is_empty(self):
        return not self.documents.exists()


class Document(models.Model):
    file_name = models.CharField(max_length=255)
    file_content = models.BinaryField()
    file_extension = models.CharField(max_length=10, default='.pdf')
    folder = models.ForeignKey(
        Folder, 
        on_delete=models.CASCADE, 
        related_name='documents', 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='documents_created'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.file_name} ({self.folder.name if self.folder else 'No Folder'})"
