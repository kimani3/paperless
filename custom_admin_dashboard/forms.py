# custom_admin_dashboard/forms.py
from django import forms
from documents.models import Department, Folder, Document, Profile
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

CustomUser = get_user_model()

class EditUserForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True)  # Include username
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)
    is_active = forms.BooleanField(required=False)
    is_superuser = forms.BooleanField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'department', 'is_active', 'is_superuser']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError("This email is already in use.")
        return email
    
class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    department = forms.ModelChoiceField(queryset=Department.objects.all())

    class Meta:
        model = CustomUser
        fields = ['email', 'department']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email

# Form for updating the Profile, including the department
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['department', 'nationalID', 'contact_number']   


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
