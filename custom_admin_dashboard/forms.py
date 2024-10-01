# custom_admin_dashboard/forms.py
from django import forms
from django.contrib.auth.models import User
from documents.models import Department, Folder, Document

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser']  # Add any fields you need

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'department']

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file_name']  # Include the necessary fields
        widgets = {
            'file_content': forms.ClearableFileInput(attrs={
                'accept': 'application/pdf,image/*,application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }),
        }
