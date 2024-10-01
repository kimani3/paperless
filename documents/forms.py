# documents/forms.py
from django import forms
from .models import Document, Folder, Department
from django.contrib.auth.models import User


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file_name']  # Include the necessary fields
        widgets = {
            'file_content': forms.ClearableFileInput(attrs={
                'accept': 'application/pdf,image/*,application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }),
        }

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['department']

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
