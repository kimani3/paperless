# custom_admin_dashboard/forms.py
from django import forms
from django.contrib.auth.models import User
from documents.models import Department, Folder, Document, CustomUser

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser  # Change this to CustomUser
        fields = ['username', 'email', 'department', 'is_superuser','is_active']  # Include the department field

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    new_password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm New Password")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        new_password_confirm = cleaned_data.get("new_password_confirm")

        if new_password and new_password_confirm and new_password != new_password_confirm:
            raise forms.ValidationError("Passwords do not match.")

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
