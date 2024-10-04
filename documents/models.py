from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings

class Department(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'CustomUser', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='departments_created'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    department = models.ForeignKey(
        'Department', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='users'
    )
    nationalID = models.CharField(max_length=20, unique=True, null=True, blank=True)
    contact_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_profile_complete = models.BooleanField(default=False)
    profile_image = models.BinaryField(null=True, blank=True)  # Binary field for profile image

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
    )

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=10, blank=True, null=True)
    
class Folder(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name='folders'
    )
    created_at = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(
        CustomUser, 
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
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='documents_created'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.file_name} ({self.folder.name})"
