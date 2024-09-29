# documents/models.py
from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Department(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='departments_created')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Folder(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='folders')
    created_at = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='folders_created')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.department.name})"

class Document(models.Model):
    file_name = models.CharField(max_length=255)
    file_content = models.BinaryField()
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='documents_created')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.file_name} ({self.folder.name})"

    def assign_default_folder(self, user):
        if not self.folder:
            today_str = date.today().strftime('%Y-%m-%d')
            folder, created = Folder.objects.get_or_create(name=today_str, created_by=user)
            if created:
                # You may want to associate a default department if necessary
                department = Department.objects.first()  # Example, or handle this logic as needed
                folder.department = department
                folder.save()
            self.folder = folder
